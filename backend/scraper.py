import json
import os
import datetime
from google_play_scraper import Sort, reviews, search
from datetime import datetime, timedelta

DATA_DIR = "data"

def search_app_id(app_name: str) -> str:
    """
    Searches for the app by name and returns the top result's appId.
    """
    COMMON_APPS = {
        "instagram": "com.instagram.android",
        "insta": "com.instagram.android",
        "swiggy": "in.swiggy.android",
        "zomato": "com.application.zomato",
        "uber": "com.ubercab",
        "blinkit": "com.grofers.customerapp", 
        "zepto": "com.zeptonow.customer",
        "whatsapp": "com.whatsapp",
        "snapchat": "com.snapchat.android",
        "facebook": "com.facebook.katana",
        "twitter": "com.twitter.android",
        "x": "com.twitter.android",
        "linkedin": "com.linkedin.android",
        "youtube": "com.google.android.youtube",
        "netflix": "com.netflix.mediaclient",
        "spotify": "com.spotify.music"
    }
    
    name_clean = app_name.lower().strip()
    
    # 1. Instant match = fastest + safest (bypasses network/throttling)
    if name_clean in COMMON_APPS:
        print(f"[SEARCH] Using hardcoded ID for '{app_name}': {COMMON_APPS[name_clean]}")
        return COMMON_APPS[name_clean]
        
    try:
        print(f"[SEARCH] Looking for app: '{app_name}' (Global)...")
        # 2. Global Search (No country restriction, higher n_hits)
        results = search(
            app_name,
            n_hits=5
        )
        if results:
            # Iterate to find the first valid appId (sometimes top result is None)
            for res in results:
                if res['appId']:
                    print(f"[SEARCH] Found: {res['appId']}")
                    return res['appId']
            
        print("[SEARCH] No valid results found globally.")
        return None
        
    except Exception as e:
        print(f"[ERROR] App search failed: {e}")
        return None

def fetch_reviews_for_date_range(app_id: str, start_date_str: str, end_date_str: str) -> list:
    """
    Fetches reviews for a given date range [start_date, end_date].
    Returns a list of review dicts.
    """
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    
    print(f"[FETCHING] Reviews for {app_id} from {start_date} to {end_date}...")
    
    all_reviews = []
    continuation_token = None
    
    # Safety break
    MAX_QUERIES = 200
    query_count = 0
    done = False
    
    while not done and query_count < MAX_QUERIES:
        result, continuation_token = reviews(
            app_id,
            lang='en',
            country='in',
            sort=Sort.NEWEST,
            count=200,
            continuation_token=continuation_token
        )
        query_count += 1
        
        if not result:
            break
            
        for r in result:
            review_date = r['at'].date()
            
            # Check if within range
            if start_date <= review_date <= end_date:
                all_reviews.append({
                    'reviewId': r['reviewId'],
                    'content': r['content'],
                    'score': r['score'],
                    'at': r['at'].isoformat(),
                    'date': review_date.strftime("%Y-%m-%d") # Add date field for easier grouping
                })
            elif review_date < start_date:
                # We went too far back
                done = True
                
        # If the batch end is older than start_date, stop
        if result and result[-1]['at'].date() < start_date:
            done = True
            
    print(f"[DONE] Fetched {len(all_reviews)} reviews.")
    return all_reviews

if __name__ == "__main__":
    # Quick Test
    name = "Instagram"
    app_id = search_app_id(name)
    print(f"App ID for {name}: {app_id}")
    
    if app_id:
        today = datetime.now().strftime("%Y-%m-%d")
        # Fetch just today/yesterday for test
        res = fetch_reviews_for_date_range(app_id, today, today)
        print(f"Fetched {len(res)} reviews for today.")
