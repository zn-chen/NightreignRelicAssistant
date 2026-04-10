"""仓库清理流程编排服务。"""

from __future__ import annotations

from dataclasses import asdict
from time import sleep

from core.interfaces import IAutomationGateway, IOCRService, IRelicStateDetector, IRuleEngine
from core.models import RuleContext
from services.history_service import HistoryService
from services.preset_service import PresetService


class RepoService:
    def __init__(
        self,
        *,
        automation: IAutomationGateway,
        detector: IRelicStateDetector,
        ocr_service: IOCRService,
        rule_engine: IRuleEngine,
        preset_service: PresetService,
        history_service: HistoryService,
        logger,
    ):
        self.automation = automation
        self.detector = detector
        self.ocr_service = ocr_service
        self.rule_engine = rule_engine
        self.preset_service = preset_service
        self.history_service = history_service
        self.logger = logger
        self.is_running = False
        self.stats = self._new_stats()

    def start(
        self,
        *,
        mode: str,
        cleaning_mode: str,
        max_relics: int,
        allow_operate_favorited: bool,
        require_double: bool,
        log_callback=None,
        stats_callback=None,
    ) -> None:
        log = log_callback or self._log
        self.is_running = True
        self.stats = self._new_stats()

        # 开始任何自动化前先做四层安全检查，避免占位实现误触发真实动作。
        if not self.ocr_service.is_ready():
            log("未配置可用的 OCR 服务，已安全停止。", "ERROR")
            self.is_running = False
            return

        if not self.rule_engine.is_ready():
            log("未配置可用的规则引擎，已安全停止。", "ERROR")
            self.is_running = False
            return

        if not self.detector.is_ready():
            log("未配置可用的遗物状态检测器，已安全停止。", "ERROR")
            self.is_running = False
            return

        if not self.automation.is_ready():
            log("自动化运行环境未就绪，已安全停止。", "ERROR")
            self.is_running = False
            return

        log("等待 3 秒，请切换到游戏仓库界面...", "INFO")
        for _ in range(30):
            if not self.is_running:
                return
            sleep(0.1)

        if not self.automation.focus_game():
            log("未能聚焦到游戏窗口。", "ERROR")
            self.is_running = False
            return

        presets = self.preset_service.list_presets(enabled_only=True)

        # 当前仓库流程仍是单次安全验证运行，便于后续接入真实检测器和自动化动作。
        context = RuleContext(
            mode=mode,
            scene="repository",
            require_match_count=2 if require_double else 3,
            extra={"cleaning_mode": cleaning_mode, "allow_operate_favorited": allow_operate_favorited, "max_relics": max_relics},
        )

        image = self.automation.capture("affixes")
        relic_state = self.detector.detect_relic_state(image)
        ocr_result = self.ocr_service.recognize_affixes(image, "repo_affixes")
        if not ocr_result.success:
            log(f"OCR 未返回有效结果：{ocr_result.error or 'unknown error'}", "ERROR")
            self.is_running = False
            return

        evaluation = self.rule_engine.evaluate(
            ocr_result,
            {
                "presets": [asdict(item) for item in presets],
                "relic_state": relic_state,
            },
            context,
        )
        if evaluation.error:
            log(f"规则引擎返回错误：{evaluation.error}", "ERROR")
            self.is_running = False
            return

        self.stats["已检测"] += 1
        if evaluation.qualified:
            self.stats["合格"] += 1
            log("识别到合格遗物。", "SUCCESS")
            if cleaning_mode == "收藏":
                # 收藏模式下先记录历史，后续接入真实动作时可直接在这里扩展。
                self.history_service.add_record(
                    "repo_favorited",
                    source="repository",
                    index=self.stats["已检测"],
                    affixes=[{"text": item.normalized_text, "confidence": item.confidence} for item in ocr_result.affixes],
                    extra={"relic_state": relic_state, "reason": evaluation.reason},
                )
        else:
            self.stats["不合格"] += 1
            log("识别到不合格遗物。", "INFO")
            if cleaning_mode == "售出":
                # 售出模式当前只记录一次模拟结果，避免在规则未完成前误卖装备。
                self.history_service.add_record(
                    "repo_sold",
                    source="repository",
                    index=self.stats["已检测"],
                    affixes=[{"text": item.normalized_text, "confidence": item.confidence} for item in ocr_result.affixes],
                    extra={"relic_state": relic_state, "reason": evaluation.reason},
                )
                self.stats["已售出"] += 1

        if stats_callback:
            stats_callback(dict(self.stats))

        log("仓库流程已完成一次安全验证运行。", "INFO")
        self.is_running = False

    def stop(self) -> None:
        self.is_running = False

    def _log(self, message: str, level: str = "INFO") -> None:
        getattr(self.logger, level.lower(), self.logger.info)(message)

    @staticmethod
    def _new_stats() -> dict[str, int]:
        return {"已检测": 0, "合格": 0, "不合格": 0, "已售出": 0}
