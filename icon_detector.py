
# icon_detector.py
import time
from typing import Optional, Tuple

import cv2
import mss
import numpy as np

from config import (
    MONITOR_INDEX,
    LOWER_BLUE,
    UPPER_BLUE,
    MIN_ICON_AREA,
    MAX_ICON_AREA,
    BLUE_RATIO_THRESHOLD,
    MAX_ICON_SEARCH_RETRIES,
    SEARCH_X_MIN,
    SEARCH_Y_MIN,
    SEARCH_X_MAX,
    SEARCH_Y_MAX,
    MIN_ASPECT_RATIO,
    MAX_ASPECT_RATIO,
)


def _take_screenshot_bgr() -> np.ndarray:
    with mss.mss() as sct:
        monitor = sct.monitors[MONITOR_INDEX]
        raw = sct.grab(monitor)
        img = np.array(raw)
        bgr = img[:, :, :3]
    return bgr


def _find_best_blue_region(bgr: np.ndarray) -> Optional[Tuple[int, int]]:
    """Find blue icon on desktop using HSV color detection."""
    h, w, _ = bgr.shape

    x1 = max(0, min(SEARCH_X_MIN, w))
    y1 = max(0, min(SEARCH_Y_MIN, h))
    x2 = max(0, min(SEARCH_X_MAX, w))
    y2 = max(0, min(SEARCH_Y_MAX, h))

    roi_bgr = bgr[y1:y2, x1:x2]
    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_BLUE, UPPER_BLUE)

    kernel = np.ones((3, 3), np.uint8)
    mask_clean = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_center = None
    best_score = -1.0
    candidates = []

    for cnt in contours:
        x, y, w_box, h_box = cv2.boundingRect(cnt)
        area = w_box * h_box

        if area < MIN_ICON_AREA or area > MAX_ICON_AREA:
            continue

        aspect = w_box / float(h_box)
        if not (MIN_ASPECT_RATIO <= aspect <= MAX_ASPECT_RATIO):
            continue

        patch_mask = mask_clean[y:y + h_box, x:x + w_box]
        blue_pixels = np.count_nonzero(patch_mask)
        blue_ratio = blue_pixels / float(area)

        if blue_ratio < BLUE_RATIO_THRESHOLD:
            continue

        center_x_roi = x + w_box // 2
        center_y_roi = y + h_box // 2
        combined_score = blue_ratio
        
        center_x = x1 + center_x_roi
        center_y = y1 + center_y_roi
        
        candidates.append({
            'center': (center_x, center_y),
            'score': combined_score,
            'blue_ratio': blue_ratio
        })

        if combined_score > best_score:
            best_score = combined_score
            best_center = (center_x, center_y)

    if len(candidates) > 1:
        print(f"[icon_detector] Found {len(candidates)} candidate icons:")
        for i, cand in enumerate(sorted(candidates, key=lambda x: x['score'], reverse=True)[:3]):
            marker = "SELECTED" if cand['center'] == best_center else ""
            print(f"  {i+1}. Center: {cand['center']}, Score: {cand['score']:.3f} "
                  f"(blue ratio: {cand['blue_ratio']:.2f}) {marker}")
    elif len(candidates) == 1:
        print(f"[icon_detector] Found 1 candidate icon at {best_center} (blue ratio: {candidates[0]['blue_ratio']:.2f})")

    return best_center


def _save_annotated_screenshot(bgr: np.ndarray, center: Tuple[int, int], post_id: Optional[int] = None) -> None:
    """Save screenshot with annotation showing detected icon location."""
    import os
    from datetime import datetime
    
    screenshots_dir = "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    annotated = bgr.copy()
    cv2.circle(annotated, center, 40, (0, 255, 0), 3)
    
    arrow_start = (center[0] - 80, center[1] - 80)
    arrow_end = (center[0] - 45, center[1] - 45)
    cv2.arrowedLine(annotated, arrow_start, arrow_end, (0, 255, 0), 3, tipLength=0.3)
    
    text = f"Icon Detected: ({center[0]}, {center[1]})"
    cv2.putText(annotated, text, (center[0] - 100, center[1] - 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    cv2.putText(annotated, "SUCCESS", (center[0] - 50, center[1] + 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if post_id is not None:
        filename = f"{screenshots_dir}/detection_post_{post_id}_{timestamp}.png"
    else:
        filename = f"{screenshots_dir}/detection_{timestamp}.png"
    
    cv2.imwrite(filename, annotated)
    print(f"[icon_detector] 📸 Annotated screenshot saved: {filename}")


def locate_notepad_icon_center(save_screenshot: bool = False, post_id: Optional[int] = None) -> Optional[Tuple[int, int]]:
    """Locate Notepad icon using color detection. Retries up to MAX_ICON_SEARCH_RETRIES times."""
    for attempt in range(1, MAX_ICON_SEARCH_RETRIES + 1):
        bgr = _take_screenshot_bgr()
        center = _find_best_blue_region(bgr)
        
        if center is not None:
            print(f"[icon_detector] Icon found at {center} on attempt {attempt}.")
            if save_screenshot:
                _save_annotated_screenshot(bgr, center, post_id)
            return center

        print(f"[icon_detector] Icon not found on attempt {attempt}, retrying...")
        time.sleep(0.5)

    print("[icon_detector] Failed to locate icon after retries.")
    return None