"""
Install TensorFlow GPU version
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and print output"""
    print(f"Running: {command}")
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        universal_newlines=True
    )
    
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    print(f"Command completed with return code: {process.returncode}")
    return process.returncode

def main():
    """Main function"""
    print("Uninstalling existing TensorFlow versions...")
    run_command("pip uninstall -y tensorflow tensorflow_cpu tensorflow-io-gcs-filesystem")
    
    print("\nInstalling TensorFlow with GPU support...")
    run_command("pip install tensorflow==2.19.0")
    
    print("\nInstalling CUDA support packages...")
    run_command("pip install nvidia-cudnn-cu12")
    
    print("\nVerifying installation...")
    run_command("pip list | findstr tensorflow")
    
    print("\nChecking TensorFlow GPU availability...")
    verify_script = """
import tensorflow as tf
print(f"TensorFlow version: {tf.__version__}")
print(f"GPU available: {tf.config.list_physical_devices('GPU')}")
"""
    
    with open("verify_tf_gpu.py", "w") as f:
        f.write(verify_script)
    
    run_command("python verify_tf_gpu.py")
    
    print("\nInstallation completed!")

if __name__ == "__main__":
    main()