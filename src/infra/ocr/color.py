"""颜色处理 — 字体颜色分离 & 图标主色调识别"""

from __future__ import annotations

import cv2
import numpy as np


def separate_by_color(image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """按字体颜色分离正面和负面词条的二值掩码。

    正面词条: 低饱和度(S<45), 高亮度(V>100) → 白/灰色文字
    负面词条: 高饱和度(S>50), 高亮度(V>100) → 偏蓝色文字

    Returns:
        (pos_mask, neg_mask) — 各为单通道二值图
    """

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    pos_mask = cv2.inRange(hsv, (0, 0, 100), (180, 45, 255))
    neg_mask = cv2.inRange(hsv, (0, 50, 100), (180, 255, 255))
    return pos_mask, neg_mask


COLOR_NAMES = {
    "red": "红色",
    "yellow": "黄色",
    "green": "绿色",
    "blue": "蓝色",
    "unknown": "未知",
}


def detect_icon_color(image: np.ndarray) -> str:
    """识别遗物图标主色调。

    所有图标底色为蓝色结晶，中心物体颜色不同(红/黄/绿/蓝)。
    策略: 排除蓝/紫底色像素，看剩余有色像素的主色调。
    非蓝像素极少(< 3%) 时判定为蓝色图标。

    Returns:
        颜色标识: "red" / "yellow" / "green" / "blue" / "unknown"
    """

    h, w = image.shape[:2]
    icon_region = image[int(h * 0.15) : int(h * 0.65), int(w * 0.02) : int(w * 0.22)]
    icon_hsv = cv2.cvtColor(icon_region, cv2.COLOR_BGR2HSV)

    s = icon_hsv[:, :, 1]
    v = icon_hsv[:, :, 2]
    colored_mask = (s > 40) & (v > 50)

    if not colored_mask.any():
        return "unknown"

    h_vals = icon_hsv[colored_mask][:, 0]
    total_colored = len(h_vals)

    non_blue_mask = (h_vals < 85) | (h_vals > 160)
    non_blue_h = h_vals[non_blue_mask]
    total_non_blue = len(non_blue_h)

    if total_non_blue < total_colored * 0.03:
        return "blue"

    red = int(((non_blue_h < 10) | (non_blue_h >= 160)).sum())
    yellow = int(((non_blue_h >= 10) & (non_blue_h < 35)).sum())
    green = int(((non_blue_h >= 35) & (non_blue_h < 85)).sum())

    counts = {"red": red, "yellow": yellow, "green": green}
    return max(counts, key=counts.get)