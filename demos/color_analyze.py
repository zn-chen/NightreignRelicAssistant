"""分析遗物截图中文字颜色分布"""
import cv2
import numpy as np

image = cv2.imread("yw.jpg")
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 手动采样几个区域的颜色（从截图中大致定位文字位置）
# 正面词条文字区域 (根据原图OCR的y坐标估算)
regions = {
    "标题(辽阔的火燃暗淡情景)": (500, 190, 950, 240),
    "正面1(女爵发动技艺)":       (470, 285, 1100, 330),
    "正面2(潜在能力镰刀)":       (470, 420, 1050, 470),
    "正面3(提升圣属性)":         (470, 555, 780, 600),
    "负面1(使用圣杯瓶)":         (470, 610, 850, 650),
}

for name, (x1, y1, x2, y2) in regions.items():
    roi_bgr = image[y1:y2, x1:x2]
    roi_hsv = hsv[y1:y2, x1:x2]

    # 只看亮度较高的像素（文字部分），排除背景
    v_channel = roi_hsv[:, :, 2]
    bright_mask = v_channel > 100  # 亮度阈值

    if bright_mask.any():
        bright_pixels_hsv = roi_hsv[bright_mask]
        bright_pixels_bgr = roi_bgr[bright_mask]

        h_mean = np.mean(bright_pixels_hsv[:, 0])
        s_mean = np.mean(bright_pixels_hsv[:, 1])
        v_mean = np.mean(bright_pixels_hsv[:, 2])
        b_mean = np.mean(bright_pixels_bgr[:, 0])
        g_mean = np.mean(bright_pixels_bgr[:, 1])
        r_mean = np.mean(bright_pixels_bgr[:, 2])

        h_std = np.std(bright_pixels_hsv[:, 0])
        s_std = np.std(bright_pixels_hsv[:, 1])

        print(f"{name}:")
        print(f"  HSV: H={h_mean:.1f}±{h_std:.1f}  S={s_mean:.1f}±{s_std:.1f}  V={v_mean:.1f}")
        print(f"  BGR: B={b_mean:.1f}  G={g_mean:.1f}  R={r_mean:.1f}")
        print(f"  亮像素数: {bright_mask.sum()}")
        print()
    else:
        print(f"{name}: 没有找到亮像素\n")
