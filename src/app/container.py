"""阶段一使用的轻量服务容器。"""

from __future__ import annotations

from dataclasses import dataclass

from core.interfaces import IAutomationGateway, IOCRService, IRelicStateDetector, IRuleEngine
from infra.automation.windows_gateway import WindowsAutomationGateway
from infra.detection.stub_detector import StubRelicStateDetector
from infra.persistence.history_repository import build_history_repositories
from infra.persistence.preset_repository import PresetRepository
from infra.persistence.settings_repository import SettingsRepository
from infra.ocr.relic_ocr_service import NightreignOCRService
from infra.resources.vocabulary_loader import VocabularyLoader
from infra.rules.stub_rule_engine import StubRuleEngine
from infra.logging.app_logger import AppLogger
from services import HistoryService, PresetService, RepoService, SaveService, SettingsService, ShopService


@dataclass(slots=True)
class AppContainer:
    """集中保存界面层会用到的服务与基础设施对象。"""

    logger: AppLogger
    settings_repo: SettingsRepository
    presets_repo: PresetRepository
    vocabulary_loader: VocabularyLoader
    settings_service: SettingsService
    preset_service: PresetService
    history_service: HistoryService
    ocr_service: IOCRService
    rule_engine: IRuleEngine
    detector: IRelicStateDetector
    automation: IAutomationGateway
    save_service: SaveService
    shop_service: ShopService
    repo_service: RepoService


def build_container() -> AppContainer:
    """按启动顺序创建并组装应用运行所需的全部依赖。"""

    # 创建设置仓储，用于读写运行配置。
    settings_repo = SettingsRepository()

    # 创建预设仓储，用于读写遗物筛选预设。
    presets_repo = PresetRepository()

    # 创建词汇加载器，用于从资源目录加载 OCR 匹配词库。
    vocabulary_loader = VocabularyLoader()

    # 创建日志器，供应用各层输出统一格式的日志。
    logger = AppLogger()

    # 创建设置服务，对设置仓储提供业务封装。
    settings_service = SettingsService(settings_repo)

    # 创建预设服务，负责预设读取、修改和词库访问。
    preset_service = PresetService(presets_repo, vocabulary_loader)

    # 创建历史服务，统一管理商店与仓库处理记录。
    history_service = HistoryService(build_history_repositories())

    # 创建 OCR 服务，负责调用识别引擎解析遗物词条。
    ocr_service = NightreignOCRService(vocabulary_loader)

    # 创建规则引擎。当前接的是占位实现，所以真实判定能力尚未补齐。
    rule_engine = StubRuleEngine()

    # 创建遗物状态检测器。当前接的是占位实现，所以状态检测尚未补齐。
    detector = StubRelicStateDetector()

    # 创建自动化网关，负责截图、按键和窗口聚焦等操作。
    automation = WindowsAutomationGateway()

    # 创建存档服务，并从当前设置中读取 Steam 路径作为初始化参数。
    save_service = SaveService(settings_service.get_settings().steam_path)

    # 返回容器对象，把基础设施、基础服务和业务服务统一暴露给界面层使用。
    return AppContainer(
        # 日志器实例。
        logger=logger,

        # 设置仓储实例。
        settings_repo=settings_repo,

        # 预设仓储实例。
        presets_repo=presets_repo,

        # 词汇加载器实例。
        vocabulary_loader=vocabulary_loader,

        # 设置服务实例。
        settings_service=settings_service,

        # 预设服务实例。
        preset_service=preset_service,

        # 历史记录服务实例。
        history_service=history_service,

        # OCR 服务实例。
        ocr_service=ocr_service,

        # 规则引擎实例。
        rule_engine=rule_engine,

        # 遗物状态检测器实例。
        detector=detector,

        # 自动化网关实例。
        automation=automation,

        # 存档管理服务实例。
        save_service=save_service,

        # 创建商店业务服务，组合自动化、OCR、规则判定、预设与历史记录能力。
        shop_service=ShopService(
            automation=automation,
            ocr_service=ocr_service,
            rule_engine=rule_engine,
            preset_service=preset_service,
            history_service=history_service,
            logger=logger,
        ),

        # 创建仓库业务服务，额外注入遗物状态检测器用于仓库场景判断。
        repo_service=RepoService(
            automation=automation,
            detector=detector,
            ocr_service=ocr_service,
            rule_engine=rule_engine,
            preset_service=preset_service,
            history_service=history_service,
            logger=logger,
        ),
    )
