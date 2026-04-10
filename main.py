"""项目根目录启动器，用于直接通过 python main.py 启动应用。"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
# 允许在未安装包的情况下，从仓库根目录直接启动。
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.main import main


if __name__ == "__main__":
    # 转调包内的正式应用入口。
    raise SystemExit(main())