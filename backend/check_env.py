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
    
    print("\nInstalled packages:")
    try:
        import pkg_resources
        for pkg in sorted([i.key for i in pkg_resources.working_set]):
            print(f"  {pkg}")
    except ImportError:
        print("  pkg_resources not available")
    
    print("\nChecking for TensorFlow:")
    try:
        import tensorflow as tf
        print(f"  TensorFlow version: {tf.__version__}")
    except ImportError:
        print("  TensorFlow not installed")
    except Exception as e:
        print(f"  Error importing TensorFlow: {e}")

if __name__ == "__main__":
    main()