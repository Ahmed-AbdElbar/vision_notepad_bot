# Vision Notepad Bot

A Python automation bot that uses computer vision to locate and interact with desktop icons. Specifically designed to find the Notepad icon on Windows desktop and automate document creation from API data.

## Features

- **Computer Vision Icon Detection**: HSV color-based detection to locate Notepad icon
- **Retry Logic**: 3 automatic retries with 1-second delays
- **Window Validation**: Confirms Notepad launched successfully
- **Screenshot Annotation**: Saves annotated screenshots showing detected icon location
- **Error Handling**: Comprehensive error handling with graceful API fallback
- **Popup Management**: Automatically handles file dialogs
- **File Management**: Smart file saving and overwrite handling

## Requirements

- Windows 10/11 (1920x1080 resolution recommended)
- Python 3.8+
- Notepad shortcut on desktop

## Prerequisites

Before installation, ensure you have a Notepad shortcut on your desktop:

1. Right-click on Desktop → **New** → **Shortcut**
2. Type: `notepad.exe` and click **Next**
3. Name it "Notepad" and click **Finish**
4. Ensure the icon is visible and not covered by other windows

## Installation

### Using UV (Recommended)

**On Windows PowerShell:**

```powershell
# Install UV
pip install uv

# Clone or download repository
cd vision-notepad-bot

# Create virtual environment and install dependencies
uv venv
uv pip install -e .
```

### Using pip

**On Windows PowerShell:**

```powershell
# Clone or download repository
cd vision-notepad-bot

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```powershell
python main.py
```

The bot will:
1. Show desktop (Win+D) to ensure icons are visible
2. Locate Notepad icon using color detection
3. Double-click to open Notepad
4. Fetch posts from JSONPlaceholder API
5. Type post content into Notepad
6. Save files to `Desktop/tjm-project/post_X.txt`
7. Close Notepad and repeat for next post

## Configuration

Edit `config.py` to adjust:

- Screen resolution settings
- HSV color range for icon detection
- Icon size constraints
- Search region boundaries
- Retry parameters

## Project Structure

```
vision-notepad-bot/
├── config.py           # Configuration parameters
├── icon_detector.py    # Computer vision icon detection
├── json_api.py        # API integration with error handling
├── main.py            # Main entry point
├── notepad_bot.py     # Core automation logic
├── requirements.txt   # Pip dependencies
├── pyproject.toml     # UV configuration
├── .python-version    # Python version
└── screenshots/       # Annotated detection screenshots
```

## How It Works

### Icon Detection

Uses HSV color space detection to find blue icons:
- Converts screenshot to HSV color space
- Applies color mask for blue range
- Filters by size (16x16 to 128x128 pixels)
- Filters by shape (aspect ratio 0.7-1.4)
- Selects best match by blue color ratio

### Error Handling

- **Icon not found**: Retries up to 3 times with desktop refresh
- **API unavailable**: Falls back to test posts
- **Window validation**: Confirms Notepad launched successfully
- **File conflicts**: Handles overwrite dialogs automatically

## Screenshots

The bot automatically saves annotated screenshots to the `screenshots/` folder showing where icons were detected. Screenshots include:
- Green circle around detected icon
- Arrow pointing to detection location
- Coordinates and confidence score
- Success indicator

## Troubleshooting

**Icon not detected:**
- Ensure Notepad shortcut is on desktop
- Check icon is not obscured by windows
- Adjust HSV color range in `config.py`

**Wrong icon clicked:**
- Verify only one blue icon matches (move other blue icons temporarily)
- Adjust `LOWER_BLUE` and `UPPER_BLUE` values

**Window not detected:**
- Install pygetwindow: `pip install pygetwindow`
- Increase timeout in `wait_for_notepad_to_open()`

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or pull request.

