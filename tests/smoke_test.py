import time
import sys
import requests

BASE_URL = "http://127.0.0.1:8000"
HEALTH_URL = f"{BASE_URL}/health"
PREDICT_URL = f"{BASE_URL}/predict"

def wait_for_service(timeout=20, interval=1):
    start = time.time()
    while time.time() - start < timeout:
        try:
            if requests.get(HEALTH_URL, timeout=2).status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(interval)
    print("Health check failed: service did not become healthy in time")
    sys.exit(1)

def predict_test():
    resp = requests.post(
        PREDICT_URL,
        json={"user_id": "smoke_user", "num_buckets": 10},
        timeout=5,
    )
    resp.raise_for_status()
    print(f"Smoke test passed: {resp.json()}")

def main():
    try:
        wait_for_service()
        predict_test()
        return 0
    except requests.HTTPError as e:
        print(f"Smoke test failed: HTTP {e}")
    except requests.RequestException as e:
        print(f"Smoke test failed: Request error - {e}")
    except Exception as e:
        print(f"Smoke test failed: Unexpected error - {e}")
    return 1

if __name__ == "__main__":
    sys.exit(main())
