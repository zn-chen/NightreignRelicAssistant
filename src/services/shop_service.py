"""商店筛选流程编排服务。"""

from __future__ import annotations

from dataclasses import asdict
from time import sleep

from core.interfaces import IAutomationGateway, IOCRService, IRuleEngine
from core.models import OCRResult, RuleContext
from services.history_service import HistoryService
from services.preset_service import PresetService


class ShopService:
    def __init__(
        self,
        *,
        automation: IAutomationGateway,
        ocr_service: IOCRService,
        rule_engine: IRuleEngine,
        preset_service: PresetService,
        history_service: HistoryService,
        logger,
    ):
        self.automation = automation
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
        version: str,
        stop_currency: int,
        require_double: bool,
        sl_mode_enabled: bool,
        sl_target: int,
        log_callback=None,
        stats_callback=None,
    ) -> None:
        log = log_callback or self._log
        self.is_running = True
        self.stats = self._new_stats()

        # 商店流程同样先做运行环境校验，确保当前还是“安全验证模式”。
        if not self.ocr_service.is_ready():
            log("未配置可用的 OCR 服务，已安全停止。", "ERROR")
            self.is_running = False
            return

        if not self.rule_engine.is_ready():
            log("未配置可用的规则引擎，已安全停止。", "ERROR")
            self.is_running = False
            return

        if not self.automation.is_ready():
            log("自动化运行环境未就绪，已安全停止。", "ERROR")
            self.is_running = False
            return

        log("等待 3 秒，请切换到游戏商店界面...", "INFO")
        for _ in range(30):
            if not self.is_running:
                return
            sleep(0.1)

        if not self.automation.focus_game():
            log("未能聚焦到游戏窗口。", "ERROR")
            self.is_running = False
            return

        presets = self.preset_service.list_presets(enabled_only=True)

        # 规则上下文承载模式、版本和停止条件，后续接真实逻辑时不必再改 UI 层接口。
        context = RuleContext(
            mode=mode,
            scene="shop",
            relic_version=version,
            require_match_count=2 if require_double else 3,
            extra={"stop_currency": stop_currency, "sl_mode_enabled": sl_mode_enabled, "sl_target": sl_target},
        )

        log("商店流程编排服务已启动。", "INFO")
        image = self.automation.capture("shop_affixes")
        ocr_result = self.ocr_service.recognize_affixes(image, "shop_affixes")
        if not ocr_result.success:
            log(f"OCR 未返回有效结果：{ocr_result.error or 'unknown error'}", "ERROR")
            self.is_running = False
            return

        evaluation = self.rule_engine.evaluate(
            ocr_result,
            {"presets": [asdict(item) for item in presets]},
            context,
        )
        if evaluation.error:
            log(f"规则引擎返回错误：{evaluation.error}", "ERROR")
            self.is_running = False
            return

        self.stats["已购买"] += 1
        if evaluation.qualified:
            self.stats["合格"] += 1
            # 当前只记录合格结果，不执行真实购买后动作，便于先联通识别和规则链路。
            self.history_service.add_record(
                "shop_qualified",
                source="shop",
                index=self.stats["已购买"],
                affixes=[{"text": item.normalized_text, "confidence": item.confidence} for item in ocr_result.affixes],
                extra={"reason": evaluation.reason},
            )
            log("识别到合格遗物。", "SUCCESS")
        else:
            self.stats["不合格"] += 1
            log("识别到不合格遗物。", "INFO")

        if stats_callback:
            stats_callback(dict(self.stats))

        log("商店流程已完成一次安全验证运行。", "INFO")
        self.is_running = False

    def stop(self) -> None:
        self.is_running = False

    def _log(self, message: str, level: str = "INFO") -> None:
        getattr(self.logger, level.lower(), self.logger.info)(message)

    @staticmethod
    def _new_stats() -> dict[str, int]:
        return {"已购买": 0, "合格": 0, "不合格": 0, "已售出": 0}
