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
    try:
        results = search(
            app_name,
            lang="en",
            country="in",
            n_hits=1
        )
        if results:
            return results[0]['appId']
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
