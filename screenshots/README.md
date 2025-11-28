# Screenshots - Icon Detection Results

This folder contains automatically generated annotated screenshots showing where the Notepad icon was detected.

## File Naming Convention

- `detection_post_X_TIMESTAMP.png` - Detection for specific post (X = post ID)
- `detection_TIMESTAMP.png` - General detection screenshot

## Annotation Legend

- **Green Circle** - Location where icon was detected
- **Green Arrow** - Points to the detected icon
- **Coordinates** - Shows (x, y) position where bot clicked
- **"SUCCESS"** - Indicates successful detection

## Example

```
detection_post_1_20251128_052000.png
```

This means:
- Post ID: 1
- Date: November 28, 2025
- Time: 05:20:00 AM
- Icon was successfully detected and annotated

## For Deliverables

Select the best 3 screenshots showing detection in:
1. **Top-left area** (x < 640, y < 360)
2. **Bottom-right area** (x > 1280, y > 720)
3. **Center of screen** (640 < x < 1280, 360 < y < 720)

These demonstrate that the bot can detect icons regardless of desktop position.


