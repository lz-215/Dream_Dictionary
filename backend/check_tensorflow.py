"""
Check TensorFlow installation
"""

import importlib.util
import sys

def check_module(module_name):
    """Check if a module is installed"""
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"{module_name} is NOT installed")
        return False
    else:
        print(f"{module_name} is installed")
        return True

def main():
    """Main function"""
    print("Checking TensorFlow installation...")
    
    # Check if TensorFlow is installed
    if check_module("tensorflow"):
        # Try to import TensorFlow
        try:
            import tensorflow as tf
            print(f"TensorFlow version: {tf.__version__}")
            
            # Check if GPU is available
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                print(f"GPU is available: {gpus}")
            else:
                print("No GPU available")
                
            # Check build information
            build_info = tf.sysconfig.get_build_info()
            print(f"Build information: {build_info}")
            
        except Exception as e:
            print(f"Error importing TensorFlow: {e}")
    
    # Check other common deep learning libraries
    libraries = [
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
        "sklearn",
        "keras",
        "torch",
        "transformers"
    ]
    
    print("\nChecking other libraries...")
    for lib in libraries:
        check_module(lib)

if __name__ == "__main__":
    main()