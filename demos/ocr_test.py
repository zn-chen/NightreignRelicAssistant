"""
OCR 方案验证脚本
用法: python ocr_test.py <遗物区域截图路径>

方案: 大区域截图 → 按字体颜色分离正/负面 → 分别OCR(use_det=True) → 模糊匹配词条库
额外: 识别遗物标题 + 图标主色调
"""

import sys
import cv2
import numpy as np
from rapidocr import RapidOCR
from rapidfuzz import fuzz


# ========== 词条库 ==========

def load_vocabulary(vocab_file):
    vocabs = []
    with open(vocab_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if "→" in line:
                line = line.split("→", 1)[1].strip()
            if line:
                vocabs.append(line)
    return vocabs


def load_all_vocabulary():
    pos_files = [
        "NRrelics/data/normal.txt",
        "NRrelics/data/normal_special.txt",
        "NRrelics/data/deepnight_pos.txt",
    ]
    neg_files = [
        "NRrelics/data/deepnight_neg.txt",
    ]

    pos_vocabs = []
    for f in pos_files:
        try:
            pos_vocabs.extend(load_vocabulary(f))
        except FileNotFoundError:
            print(f"[警告] 词条库文件不存在: {f}")
    pos_vocabs = list(dict.fromkeys(pos_vocabs))

    neg_vocabs = []
    for f in neg_files:
        try:
            neg_vocabs.extend(load_vocabulary(f))
        except FileNotFoundError:
            print(f"[警告] 词条库文件不存在: {f}")
    neg_vocabs = list(dict.fromkeys(neg_vocabs))

    return pos_vocabs, neg_vocabs


# ========== 图标颜色识别 ==========

def detect_icon_color(image):
    """
    识别遗物图标主色调

    所有图标底色都是蓝色结晶，中心物体颜色不同(红/黄/绿/蓝)。
    策略: 排除蓝色/紫色底色像素，看剩余有色像素的主色调。
    如果非蓝像素极少(< 3%)，判定为蓝色图标。
    """
    h, w = image.shape[:2]
    icon_region = image[int(h * 0.15):int(h * 0.65), int(w * 0.02):int(w * 0.22)]
    icon_hsv = cv2.cvtColor(icon_region, cv2.COLOR_BGR2HSV)

    s = icon_hsv[:, :, 1]
    v = icon_hsv[:, :, 2]
    colored_mask = (s > 40) & (v > 50)

    if not colored_mask.any():
        return "unknown", {}

    h_vals = icon_hsv[colored_mask][:, 0]
    total_colored = len(h_vals)

    # 排除蓝色(H 85-130)和紫色(H 130-160) — 底色
    non_blue_mask = (h_vals < 85) | (h_vals > 160)
    non_blue_h = h_vals[non_blue_mask]
    total_non_blue = len(non_blue_h)

    if total_non_blue < total_colored * 0.03:
        return "blue", {"blue": 1.0}

    # 在非蓝像素中统计颜色
    red = ((non_blue_h < 10) | (non_blue_h >= 160)).sum()
    yellow = ((non_blue_h >= 10) & (non_blue_h < 35)).sum()
    green = ((non_blue_h >= 35) & (non_blue_h < 85)).sum()

    ratios = {
        "red": red / total_non_blue,
        "yellow": yellow / total_non_blue,
        "green": green / total_non_blue,
    }

    dominant = max(ratios, key=ratios.get)
    return dominant, ratios


COLOR_NAMES = {
    "red": "红色",
    "yellow": "黄色",
    "green": "绿色",
    "blue": "蓝色",
    "unknown": "未知",
}


# ========== 颜色分离 ==========

def separate_by_color(image):
    """
    按字体颜色分离正面和负面词条

    - 正面词条: 低饱和度(S<45), 高亮度(V>100) → 白/灰色文字
    - 负面词条: 高饱和度(S>50), 高亮度(V>100) → 偏蓝色文字
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    pos_mask = cv2.inRange(hsv, (0, 0, 100), (180, 45, 255))
    neg_mask = cv2.inRange(hsv, (0, 50, 100), (180, 255, 255))
    return pos_mask, neg_mask


# ========== OCR ==========

def ocr_full_region(engine, image):
    """对整个区域做 OCR (开启文本检测), 按 Y 排序"""
    result = engine(image, use_det=True, use_cls=False)
    if not result or not result.txts:
        return []

    entries = []
    for i, (text, score) in enumerate(zip(result.txts, result.scores)):
        text = text.strip()
        if not text:
            continue
        box = result.boxes[i] if result.boxes is not None else None
        y_pos = float(box[0][1]) if box is not None else i * 100
        # 计算文字高度 (用于区分标题和词条)
        if box is not None:
            text_height = float(box[2][1]) - float(box[0][1])
        else:
            text_height = 0
        entries.append({
            "text": text,
            "score": score,
            "y": y_pos,
            "height": text_height,
            "box": box.tolist() if box is not None else None,
        })

    entries.sort(key=lambda e: e["y"])
    return entries


# ========== 标题与词条分离 ==========

def separate_title_and_affixes(entries):
    """
    将 OCR 结果分为标题和词条

    标题特征: Y 坐标最小 (最上方) 且不匹配词条库
    也可以通过文字高度判断 (标题字号更大)
    """
    if not entries:
        return None, []

    # 标题 = 第一个识别结果 (最上方)
    title_entry = entries[0]
    affix_entries = entries[1:]

    return title_entry, affix_entries


# ========== 模糊匹配 ==========

def match_affix(text, vocabulary, threshold=65.0):
    """对单条文本在词条库中做模糊匹配，返回最佳匹配"""
    best_match = None
    best_score = 0.0

    for vocab in vocabulary:
        score = fuzz.ratio(text, vocab)
        if score > best_score:
            best_score = score
            best_match = vocab

    if best_score >= threshold:
        return {"matched": best_match, "score": best_score, "raw": text}
    return None


# ========== 匹配驱动合并 ==========

def match_and_merge(entries, vocabulary, threshold=65.0):
    """
    先匹配，匹配不上再尝试与下一行合并

    逻辑:
    1. 当前行单独匹配词条库
    2. 如果匹配分数 >= threshold → 直接采纳
    3. 如果匹配分数低 → 尝试拼接下一行再匹配
    4. 取单独 vs 合并中分数更高的结果
    """
    if not entries:
        return []

    texts = [e["text"] for e in entries]
    results = []
    i = 0

    while i < len(texts):
        current = texts[i]
        single_result = match_affix(current, vocabulary, threshold)
        single_score = single_result["score"] if single_result else 0

        # 尝试与下一行合并
        merged_result = None
        merged_score = 0
        if i + 1 < len(texts):
            merged_text = current + texts[i + 1]
            merged_result = match_affix(merged_text, vocabulary, threshold)
            merged_score = merged_result["score"] if merged_result else 0

        if merged_result and merged_score > single_score:
            # 合并更好
            results.append(merged_result)
            i += 2  # 跳过下一行
        elif single_result:
            results.append(single_result)
            i += 1
        else:
            # 都没匹配上，保留原文
            results.append({"matched": None, "score": 0, "raw": current})
            i += 1

    return results


# ========== 主流程 ==========

def main():
    if len(sys.argv) < 2:
        print("用法: python ocr_test.py <遗物区域截图路径>")
        sys.exit(1)

    image_path = sys.argv[1]
    image = cv2.imread(image_path)
    if image is None:
        print(f"[错误] 无法读取图片: {image_path}")
        sys.exit(1)

    print(f"图片尺寸: {image.shape[1]}x{image.shape[0]}")
    print()

    # 加载词条库
    pos_vocabs, neg_vocabs = load_all_vocabulary()
    all_vocabs = pos_vocabs + neg_vocabs
    print(f"词条库: 正面 {len(pos_vocabs)} 条, 负面 {len(neg_vocabs)} 条")
    print()

    # 初始化 OCR
    engine = RapidOCR(params={
        "Det.model_path": "NRrelics/resources/models/ch_PP-OCRv4_det_infer.onnx",
        "Cls.model_path": "NRrelics/resources/models/ch_ppocr_mobile_v2.0_cls_infer.onnx",
        "Rec.model_path": "NRrelics/resources/models/ch_PP-OCRv4_rec_infer.onnx",
    })

    # ========== 图标颜色 ==========
    icon_color, color_ratios = detect_icon_color(image)
    print("=" * 60)
    print("【图标颜色识别】")
    print("=" * 60)
    print(f"  主色调: {COLOR_NAMES[icon_color]}")
    for color, ratio in sorted(color_ratios.items(), key=lambda x: -x[1]):
        bar = "█" * int(ratio * 40)
        print(f"    {COLOR_NAMES[color]:4s}: {ratio:5.1%} {bar}")
    print()

    # ========== 颜色分离 ==========
    pos_binary, neg_binary = separate_by_color(image)
    cv2.imwrite("debug_positive.png", pos_binary)
    cv2.imwrite("debug_negative.png", neg_binary)

    # ========== 正面词条 OCR ==========
    print("=" * 60)
    print("【正面词条 OCR】")
    print("=" * 60)
    pos_entries = ocr_full_region(engine, pos_binary)

    # 分离标题和词条
    title_entry, pos_affix_entries = separate_title_and_affixes(pos_entries)

    if title_entry:
        print(f"  标题: {title_entry['text']} (score={title_entry['score']:.3f}, height={title_entry['height']:.0f}px)")

    print(f"\n  词条 OCR 原文:")
    for e in pos_affix_entries:
        print(f"    y={e['y']:6.1f}  h={e['height']:4.0f}px  score={e['score']:.3f}  text={e['text']}")

    pos_results = match_and_merge(pos_affix_entries, pos_vocabs)
    print(f"\n  匹配驱动合并:")
    matched_pos = []
    for r in pos_results:
        if r["matched"]:
            matched_pos.append(r["matched"])
            print(f"    {r['raw']}")
            print(f"      → {r['matched']} ({r['score']:.1f}%)")
        else:
            print(f"    {r['raw']} → 未匹配")

    # ========== 负面词条 OCR ==========
    print()
    print("=" * 60)
    print("【负面词条 OCR】")
    print("=" * 60)
    neg_entries = ocr_full_region(engine, neg_binary)

    neg_results = match_and_merge(neg_entries, neg_vocabs)
    print(f"  匹配驱动合并:")
    matched_neg = []
    for r in neg_results:
        if r["matched"]:
            matched_neg.append(r["matched"])
            print(f"    {r['raw']}")
            print(f"      → {r['matched']} ({r['score']:.1f}%)")
        else:
            print(f"    {r['raw']} → 未匹配")

    # ========== 最终结果 ==========
    print()
    print("=" * 60)
    print("【识别结果】")
    print("=" * 60)
    print(f"  遗物名称: {title_entry['text'] if title_entry else '未识别'}")
    print(f"  图标颜色: {COLOR_NAMES[icon_color]}")
    print(f"  正面词条 ({len(matched_pos)}):")
    for affix in matched_pos:
        print(f"    + {affix}")
    print(f"  负面词条 ({len(matched_neg)}):")
    for affix in matched_neg:
        print(f"    - {affix}")


if __name__ == "__main__":
    main()
