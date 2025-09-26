import cv2 as cv
import numpy as np
try:
    import mediapipe as mp
    _MP_OK = True
except Exception:
    _MP_OK = False

from .color import dominant_color_name_and_hex


def _mask_skin_hsv(hsv):
    lower = np.array([0, 40, 60]); upper = np.array([25, 180, 255])  # rango piel aprox.
    return cv.inRange(hsv, lower, upper)

def upper_body_roi(bgr_img: np.ndarray):
    h, w, _ = bgr_img.shape
    return bgr_img[int(0.15*h):int(0.60*h), int(0.15*w):int(0.85*w)]

def detect_dominant_upper_color(bgr_img: np.ndarray) -> dict:
    roi = upper_body_roi(bgr_img)
    if roi.size == 0:
        raise ValueError("ROI vacía")
    hsv = cv.cvtColor(roi, cv.COLOR_BGR2HSV)
    skin = _mask_skin_hsv(hsv)
    noskin = cv.bitwise_and(roi, roi, mask=cv.bitwise_not(skin))
    return dominant_color_name_and_hex(noskin)