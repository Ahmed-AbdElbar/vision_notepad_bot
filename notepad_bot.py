# notepad_bot.py
import time
from pathlib import Path
from typing import Dict, Optional

import pyautogui
import pygetwindow as gw
from botcity.core import DesktopBot

from config import TARGET_DIR
from icon_detector import locate_notepad_icon_center


def ensure_target_dir() -> Path:
    """Ensure target directory exists."""
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[notepad_bot] Target directory: {TARGET_DIR}")
    return TARGET_DIR


def show_desktop(bot: DesktopBot) -> None:
    """Press Win+D to show desktop."""
    print("[notepad_bot] Pressing Win+D to show desktop...")
    pyautogui.hotkey('win', 'd')
    bot.sleep(500)


def _double_click_at(bot: DesktopBot, x: int, y: int, delay_ms: int = 150) -> None:
    """Simulate double-click at (x, y)."""
    bot.click_at(x=x, y=y)
    bot.sleep(delay_ms)
    bot.click_at(x=x, y=y)
    bot.sleep(500)


def open_notepad_via_icon(bot: DesktopBot, max_retries: int = 3, retry_delay_sec: float = 1.0, 
                          save_screenshot: bool = True, post_id: Optional[int] = None) -> bool:
    """Locate and click Notepad icon with retry logic."""
    print(f"[notepad_bot] Searching for Notepad icon (up to {max_retries} attempts)...")
    
    for attempt in range(1, max_retries + 1):
        print(f"[notepad_bot] Attempt {attempt}/{max_retries}...")
        
        if attempt > 1:
            print("[notepad_bot] Showing desktop again to clear obscured icons...")
            pyautogui.hotkey('win', 'd')
            bot.sleep(int(retry_delay_sec * 1000))
        
        center = locate_notepad_icon_center(save_screenshot=save_screenshot, post_id=post_id)
        if center is not None:
            x, y = center
            print(f"[notepad_bot] Found icon at {center}, double-clicking...")
            _double_click_at(bot, x, y)
            return True
        
        if attempt < max_retries:
            print(f"[notepad_bot] Icon not found, waiting {retry_delay_sec}s before retry...")
            bot.sleep(int(retry_delay_sec * 1000))

    print("[notepad_bot] Could not locate Notepad icon after all retries.")
    return False


def wait_for_notepad_to_open(bot: DesktopBot, timeout_sec: float = 10.0) -> bool:
    """Wait for Notepad window to appear and validate."""
    print("[notepad_bot] Waiting for Notepad window to open (validating)...")
    start = time.time()
    check_interval = 0.5
    
    while time.time() - start < timeout_sec:
        try:
            notepad_windows = [w for w in gw.getAllWindows() 
                             if w.visible and 
                             (w.title.endswith('- Notepad') or 
                              w.title == 'Notepad' or
                              w.title.startswith('Untitled') and '- Notepad' in w.title)]
            
            if notepad_windows:
                print(f"[notepad_bot] Notepad window detected: '{notepad_windows[0].title}'")
                bot.sleep(500)
                return True
        except Exception as e:
            print(f"[notepad_bot] Error checking windows: {e}")
        
        bot.sleep(int(check_interval * 1000))
    
    print(f"[notepad_bot] Timeout: Notepad window not detected after {timeout_sec}s.")
    return False


def handle_file_not_found_popup(bot: DesktopBot) -> bool:
    """Handle 'file doesn't exist' popup if present."""
    print("[notepad_bot] Checking for 'file doesn't exist' popup...")
    
    time.sleep(0.4)
    pyautogui.press('enter')
    print("[notepad_bot]   Pressed Enter to dismiss any popup")
    time.sleep(0.3)
    
    print("[notepad_bot] ✓ Popup handling complete")
    return True


def open_new_notepad_tab(bot: DesktopBot) -> None:
    """Open new Notepad tab using Ctrl+N."""
    print("[notepad_bot] Opening new Notepad tab (Ctrl+N)...")
    
    pyautogui.hotkey('ctrl', 'n')
    bot.sleep(600)
    
    handle_file_not_found_popup(bot)
    
    pyautogui.hotkey('ctrl', 'a')
    bot.sleep(100)
    pyautogui.press('delete')
    bot.sleep(200)


def type_post_content(bot: DesktopBot, post: Dict) -> None:
    """Type post content into Notepad."""
    post_id = post.get("id")
    title = post.get("title", "")
    body = post.get("body", "")

    print(f"[notepad_bot] Typing post id={post_id} into Notepad...")
    print(f"[notepad_bot] Title length: {len(title)} chars")
    print(f"[notepad_bot] Body length: {len(body)} chars")

    content = f"Title: {title}\n\nBody: {body}"
    
    print(f"[notepad_bot] Total content length: {len(content)} chars")

    bot.sleep(300)
    pyautogui.write(content, interval=0.02)
    bot.sleep(500)


def save_current_notepad_file(bot: DesktopBot, directory: Path, filename: str) -> None:
    """Save current Notepad document."""
    if not directory.exists():
        print(f"[notepad_bot] Warning: Target directory doesn't exist, creating: {directory}")
        directory.mkdir(parents=True, exist_ok=True)
    
    full_path = directory / filename
    file_existed_before = full_path.exists()
    
    print(f"[notepad_bot] Saving file: {full_path}")
    if file_existed_before:
        print(f"[notepad_bot] Note: File already exists, will be overwritten")

    bot.control_s()
    bot.sleep(1000)

    pyautogui.hotkey('ctrl', 'a')
    bot.sleep(200)
    
    full_path_str = str(full_path)
    print(f"[notepad_bot] Typing file path ({len(full_path_str)} characters)...")
    pyautogui.write(full_path_str, interval=0.01)
    bot.sleep(500)
    
    pyautogui.press('enter')
    bot.sleep(500)
    
    if file_existed_before:
        print("[notepad_bot] Handling 'Confirm Save As' dialog (replacing existing file)...")
        bot.sleep(1000)
        pyautogui.press('left')
        bot.sleep(300)
        pyautogui.press('enter')
        bot.sleep(600)
    else:
        print("[notepad_bot] New file, waiting for save to complete...")
        bot.sleep(1000)
    
    bot.sleep(500)
    if full_path.exists():
        file_size = full_path.stat().st_size
        print(f"[notepad_bot] ✓ File saved successfully: {filename} ({file_size} bytes)")
    else:
        print(f"[notepad_bot] ✗ Warning: File save verification failed - file not found")
    
    bot.sleep(300)
    pyautogui.click(960, 540)
    bot.sleep(200)


def close_notepad(bot: DesktopBot) -> None:
    """Close Notepad using Ctrl+Shift+W."""
    print("[notepad_bot] Closing Notepad completely...")
    bot.sleep(300)
    pyautogui.hotkey('ctrl', 'shift', 'w')
    bot.sleep(300)
    bot.sleep(1000)


def process_single_post(bot: DesktopBot, post: Dict, target_dir: Path) -> None:
    """Process a single post: open Notepad, type content, save, close."""
    post_id = post.get("id")
    if post_id is None:
        raise ValueError("Post has no 'id' field, cannot name file.")

    print(f"\n{'='*60}")
    print(f"[notepad_bot] Processing post id={post_id}...")
    print(f"{'='*60}")
    
    show_desktop(bot)
    
    clicked = open_notepad_via_icon(bot, max_retries=3, retry_delay_sec=1.0, 
                                    save_screenshot=True, post_id=post_id)
    if not clicked:
        raise RuntimeError(
            "Notepad icon could not be found after multiple attempts. "
            "Possible causes:\n"
            "  - Icon not on desktop\n"
            "  - Icon obscured by windows\n"
            "  - Desktop background affects detection\n"
            "  - Icon color/size outside detection parameters"
        )

    opened = wait_for_notepad_to_open(bot, timeout_sec=10.0)
    if not opened:
        raise RuntimeError(
            "Notepad window not detected after clicking icon. "
            "The application may have failed to launch."
        )
    
    bot.sleep(500)
    popup_found = handle_file_not_found_popup(bot)
    
    if popup_found:
        bot.sleep(300)
        pyautogui.click(960, 540)
        bot.sleep(200)
    
    open_new_notepad_tab(bot)
    type_post_content(bot, post)

    filename = f"post_{post_id}.txt"
    save_current_notepad_file(bot, target_dir, filename)

    close_notepad(bot)
    print(f"[notepad_bot] ✓ Finished post id={post_id}.")
    print(f"{'='*60}\n")

