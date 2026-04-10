"""Steam 存档备份与恢复服务。"""

from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from infra.system.paths import get_app_root, get_data_dir


@dataclass(slots=True)
class SaveBackupRecord:
    filename: str
    display_name: str
    path: str
    modified_time: str
    size: int


class SaveService:
    DEFAULT_STEAM_PATHS = [
        r"C:\Program Files (x86)\Steam",
        r"C:\Program Files\Steam",
        r"D:\Steam",
        r"D:\Program Files (x86)\Steam",
        r"D:\Program Files\Steam",
    ]

    SAVE_DIR_BASE = Path(os.environ.get("APPDATA", "")) / "Nightreign"
    SAVE_FILENAME = "NR0000.sl2"

    def __init__(self, steam_path: str = "", backup_dir: Path | None = None):
        # Steam 路径支持显式配置与常见默认目录自动探测两种模式。
        self.steam_path = steam_path or self._detect_steam_path()
        self.backup_dir = backup_dir or (get_data_dir() / "save_backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.users: dict[str, dict] = {}
        self._load_steam_users()

    def set_steam_path(self, steam_path: str) -> None:
        self.steam_path = steam_path
        self._load_steam_users()

    def get_users(self) -> dict[str, dict]:
        return dict(self.users)

    def get_most_recent_user(self) -> str:
        for steam_id, info in self.users.items():
            if info.get("most_recent"):
                return steam_id
        return next(iter(self.users), "")

    def get_save_path(self, steam_id: str) -> Path:
        return self.SAVE_DIR_BASE / steam_id / self.SAVE_FILENAME

    def get_save_info(self, steam_id: str) -> dict:
        save_path = self.get_save_path(steam_id)
        if not save_path.exists():
            return {"exists": False, "modified_time": "", "size": 0}

        stat = save_path.stat()
        return {
            "exists": True,
            "modified_time": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "size": stat.st_size,
        }

    def get_backups(self, steam_id: str) -> list[dict]:
        steam_backup_dir = self.backup_dir / steam_id
        if not steam_backup_dir.exists():
            return []

        # 备份列表默认按修改时间倒序，页面展示时可以直接拿最新结果。
        backups: list[dict] = []
        for file in steam_backup_dir.glob("*.sl2"):
            stat = file.stat()
            backups.append(
                {
                    "filename": file.name,
                    "display_name": file.stem,
                    "path": str(file),
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "size": stat.st_size,
                }
            )

        backups.sort(key=lambda item: item["modified_time"], reverse=True)
        return backups

    def backup_save(self, steam_id: str, backup_name: str = "") -> tuple[bool, str]:
        save_path = self.get_save_path(steam_id)
        if not save_path.exists():
            return False, "存档文件不存在"

        if not backup_name:
            backup_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = self._sanitize_filename(backup_name)
        # 备份目录按 Steam 用户分桶，避免多账号之间覆盖。
        steam_backup_dir = self.backup_dir / steam_id
        steam_backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = steam_backup_dir / f"{backup_name}.sl2"
        if backup_path.exists():
            return False, f"已存在同名备份: {backup_name}"

        try:
            shutil.copy2(save_path, backup_path)
            return True, f"备份成功: {backup_name}"
        except Exception as exc:
            return False, f"备份失败: {exc}"

    def restore_save(self, steam_id: str, backup_path: str) -> tuple[bool, str]:
        backup = Path(backup_path)
        if not backup.exists():
            return False, "备份文件不存在"

        save_path = self.get_save_path(steam_id)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            # 恢复前先给现有正式存档做一次旁路备份，减少误操作损失。
            if save_path.exists():
                shutil.copy2(save_path, save_path.with_suffix(save_path.suffix + ".bak"))
            shutil.copy2(backup, save_path)
            return True, "存档恢复成功"
        except Exception as exc:
            return False, f"恢复失败: {exc}"

    def rename_backup(self, old_path: str, new_name: str) -> tuple[bool, str]:
        old = Path(old_path)
        if not old.exists():
            return False, "备份文件不存在"

        new_name = self._sanitize_filename(new_name)
        new_path = old.parent / f"{new_name}.sl2"
        if new_path.exists():
            return False, f"已存在同名备份: {new_name}"

        try:
            old.rename(new_path)
            return True, f"重命名成功: {new_name}"
        except Exception as exc:
            return False, f"重命名失败: {exc}"

    def delete_backup(self, backup_path: str) -> tuple[bool, str]:
        backup = Path(backup_path)
        if not backup.exists():
            return False, "备份文件不存在"

        try:
            backup.unlink()
            return True, "删除成功"
        except Exception as exc:
            return False, f"删除失败: {exc}"

    def _detect_steam_path(self) -> str:
        for path in self.DEFAULT_STEAM_PATHS:
            if Path(path, "config", "loginusers.vdf").exists():
                return path
        return ""

    def _load_steam_users(self) -> None:
        self.users = {}
        if not self.steam_path:
            return

        vdf_path = Path(self.steam_path) / "config" / "loginusers.vdf"
        if not vdf_path.exists():
            return

        try:
            # 只解析 loginusers.vdf 里页面真正需要的字段，不引入额外 VDF 依赖。
            content = vdf_path.read_text(encoding="utf-8", errors="ignore")
            data = self._parse_vdf(content)
            for steam_id, info in data.get("users", {}).items():
                if isinstance(info, dict):
                    self.users[steam_id] = {
                        "name": info.get("PersonaName", info.get("AccountName", steam_id)),
                        "account_name": info.get("AccountName", ""),
                        "most_recent": info.get("MostRecent", "0") == "1",
                    }
        except Exception:
            self.users = {}

    @staticmethod
    def _parse_vdf(content: str) -> dict:
        # 这里保留一个最小可用解析器，只覆盖 Steam 登录用户文件的结构。
        result = {}
        stack = [result]
        current_key = None

        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("//"):
                continue

            pair = re.match(r'"([^"]*?)"\s+"([^"]*?)"', line)
            if pair:
                stack[-1][pair.group(1)] = pair.group(2)
                continue

            key_match = re.match(r'"([^"]*?)"', line)
            if key_match:
                current_key = key_match.group(1)
                continue

            if line == "{" and current_key is not None:
                new_dict = {}
                stack[-1][current_key] = new_dict
                stack.append(new_dict)
                current_key = None
                continue

            if line == "}" and len(stack) > 1:
                stack.pop()

        return result

    @staticmethod
    def _sanitize_filename(name: str) -> str:
        return re.sub(r'[<>:"/\\|?*]', '_', name)
