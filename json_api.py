# json_api.py
from typing import List, Dict, Optional
import requests

API_URL = "https://jsonplaceholder.typicode.com/posts"
REQUEST_TIMEOUT = 10  # seconds


def fetch_first_posts(limit: int = 10) -> Optional[List[Dict]]:
    """
    Fetch the first `limit` posts from JSONPlaceholder.
    Returns a list of dicts with keys: userId, id, title, body.
    
    Implements graceful error handling:
    - Network errors (connection, timeout)
    - HTTP errors (4xx, 5xx)
    - Invalid JSON responses
    
    Returns:
        List of posts on success, None on any error.
    """
    print("[json_api] Fetching posts from JSONPlaceholder...")
    
    try:
        resp = requests.get(API_URL, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        
        all_posts = resp.json()
        
        if not isinstance(all_posts, list):
            print(f"[json_api] ERROR: Expected list, got {type(all_posts)}")
            return None
        
        posts = all_posts[:limit]
        print(f"[json_api] Successfully retrieved {len(posts)} posts.")
        return posts
        
    except requests.exceptions.Timeout:
        print(f"[json_api] ERROR: Request timed out after {REQUEST_TIMEOUT}s")
        return None
        
    except requests.exceptions.ConnectionError as e:
        print(f"[json_api] ERROR: Connection failed - {e}")
        print("[json_api] Please check your internet connection.")
        return None
        
    except requests.exceptions.HTTPError as e:
        print(f"[json_api] ERROR: HTTP error - {e}")
        print(f"[json_api] Status code: {e.response.status_code}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"[json_api] ERROR: Request failed - {e}")
        return None
        
    except ValueError as e:
        print(f"[json_api] ERROR: Invalid JSON response - {e}")
        return None
        
    except Exception as e:
        print(f"[json_api] ERROR: Unexpected error - {e}")
        return None


def create_fallback_posts(count: int = 3) -> List[Dict]:
    """
    Create fallback posts when API is unavailable.
    These are minimal test posts that allow the bot to continue operating.
    
    Args:
        count: Number of fallback posts to create
    
    Returns:
        List of fallback post dictionaries
    """
    print(f"[json_api] Creating {count} fallback posts for testing...")
    
    fallback_posts = []
    for i in range(1, count + 1):
        post = {
            "userId": 1,
            "id": i,
            "title": f"Fallback Post {i}",
            "body": f"This is a fallback post created because the API was unavailable.\n"
                   f"Post ID: {i}\n"
                   f"The bot continues to operate using this test data."
        }
        fallback_posts.append(post)
    
    print(f"[json_api] Created {len(fallback_posts)} fallback posts.")
    return fallback_posts