"""
Test the /upload_eye_data endpoint directly
"""
import requests
import json

# Make sure Flask app is running on port 5000
BASE_URL = "http://localhost:5000"

# Get an existing test (we know test 169 exists)
test_id = 169

payload = {
    "test_id": test_id,
    "samples": [
        {"n": 1, "x": 100.0, "y": 200.0, "lx": 50.0, "ly": 75.0, "rx": 150.0, "ry": 225.0},
        {"n": 2, "x": 110.0, "y": 210.0, "lx": 55.0, "ly": 80.0, "rx": 155.0, "ry": 230.0},
    ]
}

print(f"Testing upload to test_id: {test_id}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        f"{BASE_URL}/upload_eye_data",
        json=payload,
        timeout=5
    )
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
    print("\nMake sure Flask app is running!")
    print("Run: python app.py")
