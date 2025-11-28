# main.py
from botcity.core import DesktopBot

from json_api import fetch_first_posts, create_fallback_posts
from notepad_bot import ensure_target_dir, process_single_post


def main():
    print("[main] Starting Vision-Based Desktop Automation bot...")
    print("=" * 60)

    target_dir = ensure_target_dir()

    posts = fetch_first_posts(limit=10)
    
    if posts is None:
        print("\n" + "!" * 60)
        print("[main] API unavailable - using fallback posts for testing")
        print("!" * 60 + "\n")
        posts = create_fallback_posts(count=3)
    
    if not posts:
        print("[main] No posts available. Exiting.")
        return

    print(f"[main] Processing {len(posts)} posts...")
    print("=" * 60 + "\n")

    bot = DesktopBot()

    successful = 0
    failed = 0
    
    for post in posts:
        post_id = post.get('id', 'unknown')
        try:
            print(f"\n[main] --- Processing post {post_id} ({successful + failed + 1}/{len(posts)}) ---")
            process_single_post(bot, post, target_dir)
            successful += 1
            print(f"[main] ✓ Post {post_id} completed successfully")
            
        except Exception as e:
            failed += 1
            print(f"[main] ✗ Error processing post {post_id}: {e}")
            print(f"[main] Continuing with next post...")

    print("\n" + "=" * 60)
    print(f"[main] Processing complete!")
    print(f"[main] Successful: {successful}/{len(posts)}")
    print(f"[main] Failed: {failed}/{len(posts)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
