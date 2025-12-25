import requests
import time
import sys

def test_api():
    url = "http://127.0.0.1:8000/analyze"
    payload = {
        "app_name": "TEST",
        "dates": ["2025-01-01", "2025-01-02"]
    }
    
    print(f"Sending POST to {url}...")
    try:
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            print("[SUCCESS] API returned 200 OK")
            print(resp.json())
        else:
            print(f"[FAIL] API returned {resp.status_code}")
            print(resp.text)
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Wait for server to boot
    time.sleep(3) 
    test_api()
