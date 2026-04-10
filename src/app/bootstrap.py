"""启动时装配依赖并预热运行期文件。"""

from __future__ import annotations

from app.container import AppContainer, build_container


def bootstrap() -> AppContainer:
    # 先创建整套依赖容器，后续初始化都基于这套单例对象进行。
    container = build_container()

    # 提前触发基础配置文件加载，避免首次打开页面时再懒加载导致状态闪动。
    container.settings_repo.load_settings()
    container.presets_repo.load_store()

    # 历史记录按桶分别预热，保证页面一启动就能直接显示已有数据。
    for bucket in container.history_service.repositories.values():
        bucket.load()
    container.logger.info("应用基础设施初始化完成")
    return container
