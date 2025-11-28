# config.py
from pathlib import Path
import numpy as np

# Paths
HOME_DIR = Path.home()
DESKTOP_DIR = HOME_DIR / "Desktop"
TARGET_DIR = DESKTOP_DIR / "tjm-project"

# Screen settings (1920x1080 resolution)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
TASKBAR_HEIGHT = 80

# Desktop search region (exclude taskbar)
SEARCH_X_MIN = 0
SEARCH_Y_MIN = 0
SEARCH_X_MAX = SCREEN_WIDTH
SEARCH_Y_MAX = SCREEN_HEIGHT - TASKBAR_HEIGHT

# Icon detection - HSV color range for blue icons
LOWER_BLUE = np.array([95, 70, 70])
UPPER_BLUE = np.array([125, 255, 255])

# Icon size constraints (in pixels)
MIN_ICON_AREA = 16 * 16
MAX_ICON_AREA = 128 * 128

# Icon shape constraints
MIN_ASPECT_RATIO = 0.7
MAX_ASPECT_RATIO = 1.4

# Detection parameters
BLUE_RATIO_THRESHOLD = 0.12
MAX_ICON_SEARCH_RETRIES = 3

# Monitor settings (1 = first physical monitor)
MONITOR_INDEX = 1
