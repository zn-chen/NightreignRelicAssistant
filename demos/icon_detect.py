"""通过轮廓检测定位图标方框 - 多策略"""
import cv2
import numpy as np

def find_icon_square(image, debug_prefix=""):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_area = image.shape[0] * image.shape[1]
    min_area = img_area * 0.015
    max_area = img_area * 0.25

    candidates = []

    # 策略1: 直接 Canny + 轮廓
    for t1, t2 in [(30, 80), (50, 120), (80, 180)]:
        edges = cv2.Canny(gray, t1, t2)
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)

        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.05 * peri, True)
            if 4 <= len(approx) <= 6:
                x, y, w, h = cv2.boundingRect(approx)
                area = w * h
                aspect = min(w, h) / max(w, h)
                if aspect > 0.7 and min_area < area < max_area:
                    candidates.append((x, y, w, h, area, aspect, f"canny_{t1}"))

    # 策略2: 自适应阈值
    for block in [11, 21, 31]:
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, block, 2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.05 * peri, True)
            if 4 <= len(approx) <= 6:
                x, y, w, h = cv2.boundingRect(approx)
                area = w * h
                aspect = min(w, h) / max(w, h)
                if aspect > 0.7 and min_area < area < max_area:
                    candidates.append((x, y, w, h, area, aspect, f"adaptive_{block}"))

    if not candidates:
        return None, []

    # 去重 (IoU > 0.5 的合并)
    unique = []
    for c in sorted(candidates, key=lambda x: x[4], reverse=True):
        x, y, w, h = c[:4]
        is_dup = False
        for u in unique:
            ux, uy, uw, uh = u[:4]
            # 计算 IoU
            ix = max(x, ux)
            iy = max(y, uy)
            iw = min(x+w, ux+uw) - ix
            ih = min(y+h, uy+uh) - iy
            if iw > 0 and ih > 0:
                inter = iw * ih
                union = w*h + uw*uh - inter
                if inter / union > 0.5:
                    is_dup = True
                    break

        if not is_dup:
            unique.append(c)

    return unique[0][:4] if unique else None, unique

for f in ["yw.jpg", "yw2.jpg", "yw4.jpg"]:
    img = cv2.imread(f)
    if img is None:
        continue

    best, all_cands = find_icon_square(img, f)
    print(f"\n{f}: 找到 {len(all_cands)} 个候选")
    for c in all_cands[:5]:
        x, y, w, h, area, aspect, method = c
        print(f"  x={x:4d} y={y:4d} w={w:4d} h={h:4d} ratio={aspect:.2f} method={method}")

    if best:
        x, y, w, h = best
        vis = img.copy()
        cv2.rectangle(vis, (x, y), (x+w, y+h), (0, 255, 0), 3)
        cv2.imwrite(f"debug_icon_box_{f}", vis)
