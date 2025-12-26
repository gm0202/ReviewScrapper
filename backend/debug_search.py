from scraper import search_app_id
from google_play_scraper import search
import sys

OUTPUT_FILE = "debug_result.txt"

def log(msg):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# Clear file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("--- Testing App Search ---\n")

app_name = "genshin Impact"
log(f"Searching for: '{app_name}'")

try:
    # 1. Test the function directly
    app_id = search_app_id(app_name)
    log(f"Result from search_app_id: {app_id}")

    # 2. Test the raw library call
    log("\n--- Raw Library Search Results ---")
    results = search(app_name, n_hits=5)
    for i, res in enumerate(results):
        log(f"{i+1}. {res['title']} ({res['appId']})")

except Exception as e:
    log(f"Error occurred: {e}")
