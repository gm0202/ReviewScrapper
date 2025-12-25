from scraper import search_app_id
import sys

def test_search():
    print("Testing App Search...")
    app_name = "Instagram"
    try:
        app_id = search_app_id(app_name)
        if app_id:
            print(f"[SUCCESS] Found app_id: {app_id}")
        else:
            print(f"[FAIL] app_id is None. Search returned no results.")
    except Exception as e:
        print(f"[ERROR] Exception during search: {e}")

if __name__ == "__main__":
    test_search()
