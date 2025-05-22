"""
Script to uninstall existing TensorFlow and install TensorFlow GPU version
"""

import subprocess
import sys
import os
import time
import platform

def print_header(message):
    """Print a header message"""
    print("\n" + "=" * 60)
    print(f" {message}")
    print("=" * 60)

def run_command(command, show_output=True):
    """Run a command and show output in real-time"""
    print(f"Running: {command}")
    
    # Start the process
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        universal_newlines=True
    )
    
    # Read and print output in real-time
    output_lines = []
    for line in process.stdout:
        if show_output:
            print(line, end='')
        output_lines.append(line)
    
    # Wait for the process to complete
    process.wait()
    
    # Return the output and return code
    return ''.join(output_lines), process.returncode

def check_python_environment():
    """Check Python environment"""
    print_header("Python Environment")
    print(f"Python version: {platform.python_version()}")
    print(f"Python executable: {sys.executable}")
    print(f"Platform: {platform.platform()}")

def uninstall_tensorflow():
    """Uninstall existing TensorFlow packages"""
    print_header("Uninstalling Existing TensorFlow")
    
    # List of packages to uninstall
    packages = [
        "tensorflow",
        "tensorflow-cpu",
        "tensorflow-gpu",
        "tensorflow-io-gcs-filesystem"
    ]
    
    for package in packages:
        print(f"\nUninstalling {package}...")
        output, return_code = run_command(f"{sys.executable} -m pip uninstall -y {package}")
        if return_code != 0:
            print(f"Warning: Failed to uninstall {package}, it might not be installed.")

def check_gpu():
    """Check if GPU is available"""
    print_header("Checking GPU Availability")
    
    # Check for NVIDIA GPU using nvidia-smi
    output, return_code = run_command("nvidia-smi", show_output=True)
    
    if return_code == 0:
        print("\nNVIDIA GPU detected!")
        return True
    else:
        print("\nNo NVIDIA GPU detected or drivers not installed.")
        return False

def install_tensorflow(gpu_available):
    """Install TensorFlow"""
    print_header("Installing TensorFlow")
    
    if gpu_available:
        print("Installing TensorFlow with GPU support...")
        # Install TensorFlow with GPU support
        run_command(f"{sys.executable} -m pip install tensorflow[and-cuda]")
    else:
        print("Installing standard TensorFlow...")
        # Install standard TensorFlow
        run_command(f"{sys.executable} -m pip install tensorflow")

def verify_installation():
    """Verify TensorFlow installation"""
    print_header("Verifying TensorFlow Installation")
    
    # Check installed packages
    output, _ = run_command(f"{sys.executable} -m pip list | findstr tensor")
    print("\nInstalled TensorFlow packages:")
    print(output)
    
    # Try to import TensorFlow
    print("\nImporting TensorFlow...")
    try:
        import tensorflow as tf
        print(f"TensorFlow version: {tf.__version__}")
        
        # Check build information
        build_info = tf.sysconfig.get_build_info()
        print(f"Is CUDA build: {build_info.get('is_cuda_build', False)}")
        
        # Check GPU availability
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            print(f"Number of GPUs available: {len(gpus)}")
            for gpu in gpus:
                print(f"  {gpu}")
        else:
            print("No GPUs available to TensorFlow")
        
        # Run a simple test
        print("\nRunning a simple test...")
        a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
        b = tf.constant([[5.0, 6.0], [7.0, 8.0]])
        c = tf.matmul(a, b)
        print(f"Matrix multiplication result: {c}")
        
        return True
    except ImportError:
        print("Failed to import TensorFlow. It might not be installed correctly.")
        return False
    except Exception as e:
        print(f"Error when using TensorFlow: {e}")
        return False

def main():
    """Main function"""
    print_header("TensorFlow GPU Installation Script")
    
    # Check Python environment
    check_python_environment()
    
    # Uninstall existing TensorFlow
    uninstall_tensorflow()
    
    # Check for GPU
    gpu_available = check_gpu()
    
    # Install TensorFlow
    install_tensorflow(gpu_available)
    
    # Verify installation
    success = verify_installation()
    
    if success:
        print_header("Installation Completed Successfully")
    else:
        print_header("Installation Completed with Issues")
        print("Please check the output above for errors.")

if __name__ == "__main__":
    main()