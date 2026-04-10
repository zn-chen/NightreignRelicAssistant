"""Windows 自动化网关，统一封装窗口、截图与输入操作。"""

from __future__ import annotations

import time
from dataclasses import dataclass

from core.interfaces import IAutomationGateway
from infra.automation.profiles import BASE_RESOLUTION, REPO_ANCHORS, REPO_REGIONS, SHOP_ANCHORS, SHOP_REGIONS

try:
    import pyautogui
    import pydirectinput
    import pygetwindow as gw
    import win32gui
except ImportError:
    pyautogui = None
    pydirectinput = None
    gw = None
    win32gui = None


@dataclass(slots=True)
class WindowInfo:
    title: str
    left: int
    top: int
    width: int
    height: int
    client_left: int
    client_top: int
    client_width: int
    client_height: int


class WindowsAutomationGateway(IAutomationGateway):
    def __init__(self, title_hint: str = "NIGHTREIGN"):
        self.title_hint = title_hint

    def is_ready(self) -> bool:
        return all(module is not None for module in (pyautogui, pydirectinput, gw, win32gui))

    def focus_game(self) -> bool:
        window = self.find_game_window()
        if window is None:
            return False
        try:
            target = gw.getWindowsWithTitle(window.title)[0]
            target.activate()
            return True
        except Exception:
            return False

    def capture(self, region_name: str | None = None):
        if not self.is_ready():
            return None
        window = self.find_game_window()
        if window is None:
            return None

        # 不传区域名时直接截整个客户区，供状态检测或调试使用。
        if region_name is None:
            return pyautogui.screenshot(region=(window.client_left, window.client_top, window.client_width, window.client_height))

        # 其余场景按 profile 中定义的逻辑区域裁剪截图。
        region = SHOP_REGIONS.get(region_name) or REPO_REGIONS.get(region_name)
        if region is None:
            return None
        x1, y1, x2, y2 = self.scale_region(region, window)
        return pyautogui.screenshot(region=(window.client_left + x1, window.client_top + y1, x2 - x1, y2 - y1))

    def press(self, key: str, duration: float = 0.05) -> None:
        if not self.is_ready():
            return
        pydirectinput.press(key)
        time.sleep(duration)

    def click_anchor(self, anchor_name: str) -> bool:
        if not self.is_ready():
            return False
        window = self.find_game_window()
        if window is None:
            return False

        # 点击坐标统一从锚点配置换算，避免业务层直接依赖像素值。
        anchor = SHOP_ANCHORS.get(anchor_name) or REPO_ANCHORS.get(anchor_name)
        if anchor is None:
            return False

        x, y = self.scale_point(anchor, window)
        pyautogui.moveTo(window.client_left + x, window.client_top + y)
        time.sleep(0.1)
        pyautogui.click()
        return True

    def find_game_window(self) -> WindowInfo | None:
        if not self.is_ready():
            return None

        # 先按标题模糊匹配窗口，再转成客户区坐标，减少边框和标题栏干扰。
        for window in gw.getAllWindows():
            if self.title_hint in window.title.upper():
                try:
                    hwnd = win32gui.FindWindow(None, window.title)
                    client_rect = win32gui.GetClientRect(hwnd)
                    client_left, client_top = win32gui.ClientToScreen(hwnd, (client_rect[0], client_rect[1]))
                    client_width = client_rect[2] - client_rect[0]
                    client_height = client_rect[3] - client_rect[1]
                    return WindowInfo(
                        title=window.title,
                        left=window.left,
                        top=window.top,
                        width=window.width,
                        height=window.height,
                        client_left=client_left,
                        client_top=client_top,
                        client_width=client_width,
                        client_height=client_height,
                    )
                except Exception:
                    continue
        return None

    @staticmethod
    def scale_point(point: tuple[int, int], window: WindowInfo) -> tuple[int, int]:
        # 所有坐标都基于参考分辨率缩放，保证不同窗口尺寸下仍能命中目标控件。
        scale_x = window.client_width / BASE_RESOLUTION[0]
        scale_y = window.client_height / BASE_RESOLUTION[1]
        return int(point[0] * scale_x), int(point[1] * scale_y)

    @staticmethod
    def scale_region(region: tuple[int, int, int, int], window: WindowInfo) -> tuple[int, int, int, int]:
        scale_x = window.client_width / BASE_RESOLUTION[0]
        scale_y = window.client_height / BASE_RESOLUTION[1]
        return (
            int(region[0] * scale_x),
            int(region[1] * scale_y),
            int(region[2] * scale_x),
            int(region[3] * scale_y),
        )
