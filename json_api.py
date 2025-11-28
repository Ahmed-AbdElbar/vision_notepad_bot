# json_api.py
from typing import List, Dict, Optional
import requests

API_URL = "https://jsonplaceholder.typicode.com/posts"
REQUEST_TIMEOUT = 10


def fetch_first_posts(limit: int = 10) -> Optional[List[Dict]]:
    """Fetch posts from JSONPlaceholder API with error handling."""
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
        return None
        
    except requests.exceptions.HTTPError as e:
        print(f"[json_api] ERROR: HTTP error - {e}")
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
    """Create fallback posts when API is unavailable."""
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