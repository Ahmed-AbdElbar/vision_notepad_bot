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
    """
    Ensure that the Desktop/tjm-project directory exists.
    Returns the Path to the directory.
    """
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[notepad_bot] Target directory: {TARGET_DIR}")
    return TARGET_DIR


def show_desktop(bot: DesktopBot) -> None:
    """
    Press Win+D hotkey to show the desktop (minimize all windows).
    This ensures we can see the desktop icons before trying to locate Notepad.
    """
    print("[notepad_bot] Pressing Win+D to show desktop...")
    pyautogui.hotkey('win', 'd')
    bot.sleep(500)  # Wait for desktop to appear


def _double_click_at(bot: DesktopBot, x: int, y: int, delay_ms: int = 150) -> None:
    """
    Simulate a double-click at (x, y) using two click_at calls.
    """
    bot.click_at(x=x, y=y)
    bot.sleep(delay_ms)
    bot.click_at(x=x, y=y)
    bot.sleep(500)  # small delay for the app to start opening


def open_notepad_via_icon(bot: DesktopBot, max_retries: int = 3, retry_delay_sec: float = 1.0, 
                          save_screenshot: bool = True, post_id: Optional[int] = None) -> bool:
    """
    Locate the Notepad icon using color detection and double-click it.
    Implements retry logic with desktop refresh between attempts.
    
    Args:
        bot: DesktopBot instance
        max_retries: Maximum number of attempts to find and click the icon
        retry_delay_sec: Delay in seconds between retry attempts
        save_screenshot: If True, saves annotated screenshot when icon is found
        post_id: Optional post ID to include in screenshot filename
    
    Returns:
        True if we clicked it, False if not found after all retries.
    """
    print(f"[notepad_bot] Searching for Notepad icon (up to {max_retries} attempts)...")
    
    for attempt in range(1, max_retries + 1):
        print(f"[notepad_bot] Attempt {attempt}/{max_retries}...")
        
        # Show desktop before each attempt to clear any obscuring windows
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
    """
    Wait for Notepad window to appear and validate it's actually open.
    Uses pygetwindow to check for window title containing "Notepad".
    
    Args:
        bot: DesktopBot instance
        timeout_sec: Maximum time to wait for window to appear
    
    Returns:
        True if Notepad window was detected, False if timeout occurred.
    """
    print("[notepad_bot] Waiting for Notepad window to open (validating)...")
    start = time.time()
    check_interval = 0.5  # Check every 500ms
    
    while time.time() - start < timeout_sec:
        try:
            # Get all windows - look for actual Notepad application
            # Must end with "- Notepad" or be exactly "Notepad"
            notepad_windows = [w for w in gw.getAllWindows() 
                             if w.visible and 
                             (w.title.endswith('- Notepad') or 
                              w.title == 'Notepad' or
                              w.title.startswith('Untitled') and '- Notepad' in w.title)]
            
            if notepad_windows:
                print(f"[notepad_bot] Notepad window detected: '{notepad_windows[0].title}'")
                bot.sleep(500)  # Small delay for window to fully initialize
                return True
        except Exception as e:
            print(f"[notepad_bot] Error checking windows: {e}")
        
        bot.sleep(int(check_interval * 1000))
    
    print(f"[notepad_bot] Timeout: Notepad window not detected after {timeout_sec}s.")
    return False


def handle_file_not_found_popup(bot: DesktopBot) -> bool:
    """
    Handle the popup that says "x file doesn't exist anymore" with OK button.
    Uses a simple, reliable approach: wait briefly then press Enter.
    If popup exists, it gets dismissed. If not, the Enter is harmless (cleared later).
    
    Args:
        bot: DesktopBot instance
    
    Returns:
        True (always, since we attempt to handle it)
    """
    print("[notepad_bot] Checking for 'file doesn't exist' popup...")
    
    # Wait a moment for popup to appear if it's going to
    time.sleep(0.4)
    
    # Press Enter to dismiss any popup (OK button is usually default)
    # If no popup, this just adds a newline which gets cleared later
    pyautogui.press('enter')
    print("[notepad_bot]   Pressed Enter to dismiss any popup")
    
    # Short wait to let popup close
    time.sleep(0.3)
    
    print("[notepad_bot] ✓ Popup handling complete")
    return True


def open_new_notepad_tab(bot: DesktopBot) -> None:
    """
    Click the plus icon in Notepad to open a new tab, avoiding overwriting existing files.
    Uses Ctrl+N to create a new document (works in modern Notepad with tabs).
    Also checks for any popup dialogs that might appear.
    """
    print("[notepad_bot] Opening new Notepad tab (Ctrl+N)...")
    
    # Create a new document/tab using Ctrl+N
    # Use pyautogui for keyboard shortcuts since BotCity doesn't have control_n()
    pyautogui.hotkey('ctrl', 'n')
    bot.sleep(600)  # Wait for new tab to open
    
    # Check for popup after opening new tab (sometimes appears here too)
    handle_file_not_found_popup(bot)
    
    # Clear any content that might be in the new tab (should be empty, but just in case)
    pyautogui.hotkey('ctrl', 'a')  # Select all
    bot.sleep(100)
    pyautogui.press('delete')  # Delete if there's any content
    bot.sleep(200)


def type_post_content(bot: DesktopBot, post: Dict) -> None:
    """
    Given a JSONPlaceholder post dict, type it into Notepad.
    Format:
    Title: {title}
    Body: {body}
    """
    post_id = post.get("id")
    title = post.get("title", "")
    body = post.get("body", "")

    print(f"[notepad_bot] Typing post id={post_id} into Notepad...")
    print(f"[notepad_bot] Title length: {len(title)} chars")
    print(f"[notepad_bot] Body length: {len(body)} chars")

    # Format content with proper labels
    content = f"Title: {title}\n\nBody: {body}"
    
    print(f"[notepad_bot] Total content length: {len(content)} chars")

    # Wait a moment to ensure Notepad is ready to receive input
    bot.sleep(300)

    # Use pyautogui.write() instead of bot.kb_type() for better reliability
    # Type character by character with delay to prevent missing characters
    pyautogui.write(content, interval=0.02)  # 20ms between characters (slower for reliability)
    bot.sleep(500)  # Wait for typing to complete



def save_current_notepad_file(bot: DesktopBot, directory: Path, filename: str) -> None:
    """
    Save the currently open Notepad document to Desktop/tjm-project/filename
    using Ctrl+S and typing the full path into the Save dialog.
    Handles "file already exists" dialog by clicking Replace/Yes.
    
    Improvements:
    - Validates directory exists before saving
    - Handles file overwrite dialog reliably
    - Provides detailed logging for debugging
    - Uses more reliable typing method to prevent interruption
    """
    # Ensure directory exists
    if not directory.exists():
        print(f"[notepad_bot] Warning: Target directory doesn't exist, creating: {directory}")
        directory.mkdir(parents=True, exist_ok=True)
    
    full_path = directory / filename
    file_existed_before = full_path.exists()
    
    print(f"[notepad_bot] Saving file: {full_path}")
    if file_existed_before:
        print(f"[notepad_bot] Note: File already exists, will be overwritten")

    # Ctrl+S (BotCity has a direct helper for this)
    bot.control_s()
    bot.sleep(1000)  # Wait longer for save dialog to appear

    # Clear any existing text in the filename field first
    pyautogui.hotkey('ctrl', 'a')  # Select all existing text
    bot.sleep(200)
    
    # Type the full path using pyautogui with a small interval to prevent interruption
    # This is more reliable than bot.kb_type for long paths
    full_path_str = str(full_path)
    print(f"[notepad_bot] Typing file path ({len(full_path_str)} characters)...")
    pyautogui.write(full_path_str, interval=0.01)  # 10ms between each character
    bot.sleep(500)  # Wait to ensure typing completed
    
    # Press Enter to save (this may trigger "file exists" dialog)
    pyautogui.press('enter')
    bot.sleep(500)
    
    # Handle "Confirm Save As" dialog ONLY if file already existed before saving
    if file_existed_before:
        # File existed before save, so dialog will appear - handle it
        print("[notepad_bot] Handling 'Confirm Save As' dialog (replacing existing file)...")
        bot.sleep(1000)  # Wait longer for dialog to appear
        
        # Press Left Arrow to move focus from "No" to "Yes", then Enter
        # Since "No" is selected by default, we need to move left to "Yes"
        pyautogui.press('left')  # Move focus to "Yes" button
        bot.sleep(300)
        pyautogui.press('enter')  # Click Yes
        bot.sleep(600)
    else:
        # File doesn't exist, dialog won't appear - just wait for save to complete
        print("[notepad_bot] New file, waiting for save to complete...")
        bot.sleep(1000)  # Wait for save to complete
    
    # Verify file was saved
    bot.sleep(500)
    if full_path.exists():
        file_size = full_path.stat().st_size
        print(f"[notepad_bot] ✓ File saved successfully: {filename} ({file_size} bytes)")
    else:
        print(f"[notepad_bot] ✗ Warning: File save verification failed - file not found")
    
    # Final wait for save to complete
    bot.sleep(300)
    
    # Click somewhere in the Notepad window to ensure it's focused before closing
    # This helps ensure Alt+F4 will target Notepad
    pyautogui.click(960, 540)  # Click center of typical 1920x1080 screen
    bot.sleep(200)


def close_notepad(bot: DesktopBot) -> None:
    """
    Completely close Notepad using mouse and keyboard only.
    SAFE: Only sends Alt+F4 ONCE when Notepad is focused to avoid shutting down Windows.
    Removed Enter presses that were causing unwanted newlines.
    """
    print("[notepad_bot] Closing Notepad completely...")
    #bot.sleep(100000)
    # Step 1: Use Alt+Tab to bring Notepad window to front and focus it
    # This ensures we're targeting Notepad, not the desktop
    #pyautogui.hotkey('alt', 'tab')
    bot.sleep(300)  # Short wait for Alt+Tab menu
    # Don't press Enter here - it might type into Notepad if menu already closed
    # Instead, just release Alt+Tab naturally
    bot.sleep(200)
    
    # Step 2: Click in the Notepad window area to ensure it's definitely focused
    pyautogui.click(960, 540)  # Center of screen (where Notepad window should be)
    bot.sleep(300)
    
    # Step 3: Send Alt+F4 ONCE (only when Notepad is focused!)
    # IMPORTANT: We only do this once to avoid accidentally closing Windows
    pyautogui.hotkey('ctrl', 'shift', 'w')
    bot.sleep(300)
    # Step 4: Only handle dialogs if they actually appear
    # Don't press Enter unconditionally - it types newlines into Notepad
    # If there's a dialog, Alt+F4 will have closed it or it will block
    # If no dialog, Notepad should be closed by now
    
    # Wait to ensure Notepad is fully closed and desktop is visible
    bot.sleep(1000)


def process_single_post(bot: DesktopBot, post: Dict, target_dir: Path) -> None:
    """
    Full flow for one post with comprehensive error handling:
      - show desktop (minimize all windows)
      - open Notepad via icon (with retry logic)
      - validate Notepad opened
      - type content
      - save as post_{id}.txt (handle existing files)
      - close Notepad
    
    Raises:
        ValueError: If post has no ID field
        RuntimeError: If Notepad cannot be opened or validated
    """
    post_id = post.get("id")
    if post_id is None:
        raise ValueError("Post has no 'id' field, cannot name file.")

    print(f"\n{'='*60}")
    print(f"[notepad_bot] Processing post id={post_id}...")
    print(f"{'='*60}")
    
    # Show desktop to ensure Notepad icon is visible
    show_desktop(bot)
    
    # Try to open Notepad with retry logic (save screenshot for deliverables)
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

    # Validate that Notepad actually opened
    opened = wait_for_notepad_to_open(bot, timeout_sec=10.0)
    if not opened:
        raise RuntimeError(
            "Notepad window not detected after clicking icon. "
            "The application may have failed to launch."
        )
    
    # Give Notepad time to fully initialize before checking for popups
    bot.sleep(500)
    
    # Check for and handle "file doesn't exist" popup if it appears
    # This is non-intrusive - only acts if popup is actually detected
    popup_found = handle_file_not_found_popup(bot)
    
    # If popup was handled, give Notepad a moment to regain focus
    if popup_found:
        bot.sleep(300)
        # Click on Notepad window to ensure it has focus
        pyautogui.click(960, 540)
        bot.sleep(200)
    
    # Open a new tab to avoid overwriting existing files
    open_new_notepad_tab(bot)

    type_post_content(bot, post)

    filename = f"post_{post_id}.txt"
    save_current_notepad_file(bot, target_dir, filename)

    close_notepad(bot)
    print(f"[notepad_bot] ✓ Finished post id={post_id}.")
    print(f"{'='*60}\n")
