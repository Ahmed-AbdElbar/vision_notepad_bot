# config.py
from pathlib import Path
import numpy as np

# --------- General paths ---------
HOME_DIR = Path.home()
DESKTOP_DIR = HOME_DIR / "Desktop"
TARGET_DIR = DESKTOP_DIR / "tjm-project"

# --------- Screen / search region ---------
# Assuming 1920x1080 and a bottom taskbar.
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
TASKBAR_HEIGHT = 80  # pixels reserved for taskbar

# Region where we search for the Notepad icon (desktop only, no taskbar)
SEARCH_X_MIN = 0
SEARCH_Y_MIN = 0
SEARCH_X_MAX = SCREEN_WIDTH
SEARCH_Y_MAX = SCREEN_HEIGHT - TASKBAR_HEIGHT

# --------- Icon detection / color ---------
LOWER_BLUE = np.array([95, 70, 70])
UPPER_BLUE = np.array([125, 255, 255])

# Icon size constraints
MIN_ICON_AREA = 16 * 16       # Support small icons
MAX_ICON_AREA = 128 * 128     # Support larger icons too

# Accept only near-square regions
MIN_ASPECT_RATIO = 0.7        # w/h - more flexible for small icons
MAX_ASPECT_RATIO = 1.4        # Allow slightly more variation

BLUE_RATIO_THRESHOLD = 0.12   # Lower threshold for small icons
MAX_ICON_SEARCH_RETRIES = 3

# --------- Monitor index for mss ---------
# mss.monitors[0] is "all monitors", monitors[1] is first physical monitor
MONITOR_INDEX = 1
