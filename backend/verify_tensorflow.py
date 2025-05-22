"""
Verify TensorFlow installation and GPU availability
"""

import os
import sys
import platform
import subprocess

def print_section(title):
    """Print a section title"""
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)

def run_command(command):
    """Run a command and return its output"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               universal_newlines=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error message: {e.stderr}")
        return None

print_section("System Information")
print(f"Python version: {platform.python_version()}")
print(f"Platform: {platform.platform()}")

print_section("TensorFlow Installation")
try:
    import tensorflow as tf
    print(f"TensorFlow version: {tf.__version__}")
    print(f"TensorFlow path: {tf.__path__}")
    
    # Check build information
    build_info = tf.sysconfig.get_build_info()
    print(f"Is CUDA build: {build_info.get('is_cuda_build', False)}")
    print(f"Is ROCm build: {build_info.get('is_rocm_build', False)}")
    print(f"Is TensorRT build: {build_info.get('is_tensorrt_build', False)}")
    
    # Check GPU availability
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"Number of GPUs available: {len(gpus)}")
        for gpu in gpus:
            print(f"  {gpu}")
    else:
        print("No GPUs available")
    
    # Test GPU with a simple operation
    if gpus:
        print("\nRunning a test computation on GPU...")
        with tf.device('/GPU:0'):
            a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
            b = tf.constant([[5.0, 6.0], [7.0, 8.0]])
            c = tf.matmul(a, b)
            print(f"Matrix multiplication result: {c}")
    
except ImportError:
    print("TensorFlow is not installed")
except Exception as e:
    print(f"Error importing TensorFlow: {e}")

print_section("CUDA Information")
nvcc_version = run_command("nvcc --version")
if nvcc_version:
    print("NVCC version:")
    print(nvcc_version)
else:
    print("NVCC not found or not in PATH")

nvidia_smi = run_command("nvidia-smi")
if nvidia_smi:
    print("NVIDIA-SMI output:")
    print(nvidia_smi)
else:
    print("NVIDIA-SMI not found or no GPU available")

print_section("Python Packages")
pip_list = run_command("pip list | findstr tensor")
if pip_list:
    print("TensorFlow related packages:")
    print(pip_list)
else:
    print("No TensorFlow packages found")

print_section("Environment Variables")
for var in ['CUDA_HOME', 'CUDNN_HOME', 'PATH', 'LD_LIBRARY_PATH']:
    value = os.environ.get(var)
    if value:
        print(f"{var}: {value}")
    else:
        print(f"{var} not set")

print("\nVerification completed!")
