"""
Check Python environment
"""

import sys
import os
import platform

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

if __name__ == "__main__":
    main()
