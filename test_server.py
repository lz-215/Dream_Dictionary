import requests
import sys

def test_server():
    """Test if the server is responding"""
    try:
        response = requests.get('http://127.0.0.1:5000')
        print(f"Status code: {response.status_code}")
        print(f"Response length: {len(response.text)} bytes")
        print(f"Response headers: {response.headers}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
