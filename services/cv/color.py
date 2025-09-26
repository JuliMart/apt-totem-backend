import cv2 as cv
import numpy as np
from collections import Counter

# nombres de color básicos en HSV (rangos aproximados)
COLOR_MAP = {
    "rojo"  : [(0, 100, 60), (10, 255, 255)],   # baja H
    "rojo2" : [(170,100,60), (180,255,255)],    # alta H
    "naranjo": [(11,100,60), (20,255,255)],
    "amarillo": [(21,100,60), (35,255,255)],
    "verde": [(36, 80, 60), (85,255,255)],
    "cian": [(86, 80, 60), (100,255,255)],
    "azul": [(101,80,60), (130,255,255)],
    "morado": [(131,80,60), (160,255,255)],
    "rosado": [(161,80,60), (169,255,255)],
    "blanco/gris/negro": [(0,0,0), (180,50,255)],
}

def _dominant_color_hsv(bgr_img: np.ndarray, k: int = 3) -> np.ndarray:
    # downscale para velocidad
    img = cv.resize(bgr_img, (0,0), fx=0.5, fy=0.5, interpolation=cv.INTER_AREA)
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    # kmeans sobre HSV
    Z = hsv.reshape((-1,3)).astype(np.float32)
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv.kmeans(Z, k, None, criteria, 5, cv.KMEANS_PP_CENTERS)
    counts = Counter(labels.flatten())
    idx = counts.most_common(1)[0][0]
    return centers[idx].astype(np.uint8)  # (H,S,V)

def _hsv_to_hex(hsv):
    hsv_1 = np.uint8([[hsv]])
    bgr = cv.cvtColor(hsv_1, cv.COLOR_HSV2BGR)[0,0].astype(int)
    return "#{:02x}{:02x}{:02x}".format(bgr[2], bgr[1], bgr[0])  # R,G,B

def _map_color_name(hsv):
    H,S,V = int(hsv[0]), int(hsv[1]), int(hsv[2])
    # gris/blanco/negro
    if S < 40:
        return "negro" if V < 50 else ("blanco" if V > 200 else "gris")
    for name, (low, high) in COLOR_MAP.items():
        lH,lS,lV = low; hH,hS,hV = high
        if lH <= H <= hH and lS <= S <= hS and lV <= V <= hV:
            return "rojo" if name=="rojo2" else name
    return "desconocido"

def dominant_color_name_and_hex(bgr_img: np.ndarray) -> dict:
    hsv = _dominant_color_hsv(bgr_img, k=3)
    return {"name": _map_color_name(hsv), "hex": _hsv_to_hex(hsv)}
    
def mask_skin_hsv(hsv):
    lower = np.array([0, 40, 60]); upper = np.array([25, 180, 255])
    mask = cv.inRange(hsv, lower, upper)
    return mask
def detect_dominant_hsv(bgr_img: np.ndarray) -> dict:
    hsv = _dominant_color_hsv(bgr_img, k=3)
    return {
        "color_name": _map_color_name(hsv),
        "rgb": tuple(cv.cvtColor(np.uint8([[hsv]]), cv.COLOR_HSV2BGR)[0,0].tolist()[::-1]),
        "hex": _hsv_to_hex(hsv)
    }
