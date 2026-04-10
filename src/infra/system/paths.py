"""运行期数据与资源路径工具。"""

from __future__ import annotations

import sys
from pathlib import Path


def get_app_root() -> Path:
    # 打包后以可执行文件所在目录为根；源码运行时则回退到仓库根目录。
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[4]


def get_package_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_data_dir() -> Path:
    return ensure_dir(get_app_root() / "data")


def get_history_dir() -> Path:
    return ensure_dir(get_data_dir() / "history")


def get_logs_dir() -> Path:
    return ensure_dir(get_data_dir() / "logs")


def get_settings_path() -> Path:
    return get_data_dir() / "settings.json"


def get_presets_path() -> Path:
    return get_data_dir() / "presets.json"


def get_resources_dir() -> Path:
    return ensure_dir(get_app_root() / "resources")


def get_vocab_dir() -> Path:
    return ensure_dir(get_resources_dir() / "vocab")


def get_templates_dir() -> Path:
    return ensure_dir(get_resources_dir() / "templates")


def get_ocr_models_dir() -> Path | None:
    # 优先使用当前项目自带模型，缺失时再回退到参考目录，兼顾独立运行和迁移阶段。
    local_path = get_resources_dir() / "models"
    if local_path.exists():
        return local_path

    reference_path = get_reference_root() / "resources" / "models"
    if reference_path.exists():
        return reference_path

    return None


def get_reference_root() -> Path:
    return get_app_root() / "参考" / "NRrelics"


def get_reference_data_dir() -> Path:
    return get_reference_root() / "data"


def get_reference_templates_dir() -> Path:
    return get_reference_root() / "data"


def get_shop_history_path() -> Path:
    return get_history_dir() / "shop_qualified_relics.json"


def get_repo_sold_history_path() -> Path:
    return get_history_dir() / "repo_sold_relics.json"


def get_repo_favorited_history_path() -> Path:
    return get_history_dir() / "repo_favorited_relics.json"


def resolve_resource_path(relative_path: str) -> Path:
    # 资源解析同样遵循“本地优先、参考目录兜底”的查找顺序。
    local_path = get_resources_dir() / relative_path
    if local_path.exists():
        return local_path

    reference_path = get_reference_root() / relative_path
    return reference_path
