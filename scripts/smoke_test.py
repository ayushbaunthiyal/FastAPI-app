import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000"

async def test_health():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        try:
            response = await client.get("/health/live")
            print(f"Health Check: {response.status_code} {response.json()}")
            if response.status_code != 200:
                print("Health check failed!")
                return False
        except Exception as e:
            print(f"Health check connection failed: {e}")
            return False
    return True

async def main():
    print("Running Smoke Test...")
    health = await test_health()
    if not health:
        sys.exit(1)
    
    # Ideally checking other endpoints if relevant
    print("Smoke Test Passed!")

if __name__ == "__main__":
    asyncio.run(main())
