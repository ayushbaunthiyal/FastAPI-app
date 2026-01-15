
import httpx
import sys

BASE_URL = "http://localhost:8000/api/v1"

def verify_caching():
    # 1. Login
    login_data = {"username": "admin@example.com", "password": "admin123"}
    print(f"Logging in to {BASE_URL}...")
    try:
        r = httpx.post(f"{BASE_URL}/login/access-token", data=login_data)
        if r.status_code != 200:
            print(f"Login failed: {r.status_code} {r.text}")
            sys.exit(1)
        token = r.json()["access_token"]
        print("Login successful.")
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. First Request (Cache Miss)
    print("\nSending 1st Request (Expect Cache Miss/DB Hit)...")
    r1 = httpx.get(f"{BASE_URL}/users/1", headers=headers)
    print(f"Status: {r1.status_code}")
    if r1.status_code != 200:
        print(f"Body: {r1.text}")
    print(f"Response Time: {r1.headers.get('X-Response-Time')}")
    
    # 3. Second Request (Cache Hit)
    print("\nSending 2nd Request (Expect Cache Hit)...")
    r2 = httpx.get(f"{BASE_URL}/users/1", headers=headers)
    print(f"Status: {r2.status_code}")
    print(f"Response Time: {r2.headers.get('X-Response-Time')}")
    
    # Compare times (simple heuristic)
    t1 = float(r1.headers.get('X-Response-Time', '1.0').replace('s', ''))
    t2 = float(r2.headers.get('X-Response-Time', '1.0').replace('s', ''))
    
    print(f"\nTime 1: {t1:.4f}s")
    print(f"Time 2: {t2:.4f}s")
    
    if t2 < t1:
        print("\nSUCCESS: 2nd request was faster (likely cached).")
    else:
        print("\nWARNING: 2nd request was not faster. Check logs.")

if __name__ == "__main__":
    verify_caching()
