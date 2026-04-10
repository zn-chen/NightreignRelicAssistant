"""对比 use_det=True vs False 的耗时"""
import time, cv2
from rapidocr import RapidOCR

engine = RapidOCR(params={
    "Det.model_path": "NRrelics/resources/models/ch_PP-OCRv4_det_infer.onnx",
    "Cls.model_path": "NRrelics/resources/models/ch_ppocr_mobile_v2.0_cls_infer.onnx",
    "Rec.model_path": "NRrelics/resources/models/ch_PP-OCRv4_rec_infer.onnx",
})

# 用正面掩码图测试 (模拟实际输入)
img = cv2.imread("yw4.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
binary = cv2.inRange(hsv, (0, 0, 100), (180, 45, 255))

# 热身
engine(binary, use_det=True, use_cls=False)
engine(binary, use_det=False, use_cls=False)

N = 20
# use_det=True
t0 = time.time()
for _ in range(N):
    engine(binary, use_det=True, use_cls=False)
det_true = (time.time() - t0) / N * 1000

# use_det=False
t0 = time.time()
for _ in range(N):
    engine(binary, use_det=False, use_cls=False)
det_false = (time.time() - t0) / N * 1000

print(f"use_det=True:  {det_true:.1f}ms / 次")
print(f"use_det=False: {det_false:.1f}ms / 次")
print(f"差异: {det_true - det_false:.1f}ms ({det_true/det_false:.1f}x)")
