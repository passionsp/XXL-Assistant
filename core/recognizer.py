import cv2
import numpy as np
from PIL import Image

def find_template(screenshot_pil, template_path, threshold=0.7):
    """返回 (中心x, 中心y) 或 None"""
    img_cv = cv2.cvtColor(np.array(screenshot_pil), cv2.COLOR_RGB2BGR)
    img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    template = cv2.imread(template_path, 0)
    if template is None:
        return None
    h, w = template.shape
    result = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        center = (max_loc[0] + w//2, max_loc[1] + h//2)
        print(f"[匹配] {template_path} 相似度={max_val:.2f} 位置={center}")
        return center
    else:
        print(f"[未匹配] {template_path} 相似度={max_val:.2f}")
        return None