"""运行期数据与资源路径工具。"""

from __future__ import annotations

import sys
from pathlib import Path


def get_app_root() -> Path:
    """返回应用根目录路径。

    打包运行时，这里是可执行文件所在目录；源码运行时，这里是当前仓库根目录。
    后续 data、resources、OCR 等运行期路径都以这里为起点。
    """
    # 打包后以可执行文件所在目录为根；源码运行时则回退到仓库根目录。
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[3]


def ensure_dir(path: Path) -> Path:
    """确保目录存在并返回该目录路径。

    这是一个通用辅助函数，用于在返回目录路径前自动创建缺失目录。
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_data_dir() -> Path:
    """返回运行期 data 目录路径。

    这里用于保存设置、预设、日志、历史记录和存档备份等运行期数据。
    """
    return ensure_dir(get_app_root() / "data")


def get_history_dir() -> Path:
    """返回历史记录目录路径。

    商店筛选和仓库清理产生的历史 JSON 文件都保存在这个目录下。
    """
    return ensure_dir(get_data_dir() / "history")


def get_logs_dir() -> Path:
    """返回日志目录路径。

    应用运行时写出的日志文件会统一保存在这个目录下。
    """
    return ensure_dir(get_data_dir() / "logs")


def get_settings_path() -> Path:
    """返回设置文件 settings.json 的路径。"""
    return get_data_dir() / "settings.json"


def get_presets_path() -> Path:
    """返回预设文件 presets.json 的路径。"""
    return get_data_dir() / "presets.json"


def get_ocr_models_dir() -> Path | None:
    """返回 OCR 模型目录路径。

    查找顺序为：仓库根目录下的 OCR/PP-OCRv4/models，随后是 resources/models。
    若都不存在，则返回 None。
    """
    # 优先使用仓库根目录下的 OCR/PP-OCRv4 模型，其次再回退到其他目录。
    ocr_path = get_app_root() / "OCR" / "PP-OCRv4" / "models"
    if ocr_path.exists():
        return ocr_path

    # 兼容后续把模型迁回 resources/models 的场景。
    local_path = get_app_root() / "resources" / "models"
    if local_path.exists():
        return local_path

    return None


def get_shop_history_path() -> Path:
    """返回商店筛选合格遗物历史文件路径。"""
    return get_history_dir() / "shop_qualified_relics.json"


def get_repo_sold_history_path() -> Path:
    """返回仓库清理中“已售出遗物”历史文件路径。"""
    return get_history_dir() / "repo_sold_relics.json"


def get_repo_favorited_history_path() -> Path:
    """返回仓库清理中“已收藏遗物”历史文件路径。"""
    return get_history_dir() / "repo_favorited_relics.json"
