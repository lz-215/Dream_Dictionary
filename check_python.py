"""
Check Python environment
"""

import sys
import os
import platform

def list_browser_cache():
    """List common browser cache directories"""
    home_dir = os.path.expanduser("~")
    cache_dirs = {
        "Chrome": os.path.join(home_dir, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Cache"),
        "Firefox": os.path.join(home_dir, "AppData", "Local", "Mozilla", "Firefox", "Profiles"),
    }

    for browser, path in cache_dirs.items():
        print(f"{browser} cache directory: {path}")
        if os.path.exists(path):
            print(f"  Exists: Yes")
        else:
            print(f"  Exists: No")

def main():
    """Main function"""
    print("Python version:", platform.python_version())
    print("Python executable:", sys.executable)
    print("Platform:", platform.platform())
    print("Current directory:", os.getcwd())
    
    print("\nPython path:")
    for path in sys.path:
        print(f"  {path}")
    
    print("\nEnvironment variables:")
    for key, value in os.environ.items():
        print(f"  {key}: {value}")

    print("\nBrowser cache directories:")
    list_browser_cache()

if __name__ == "__main__":
    main()
