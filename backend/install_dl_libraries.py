"""
Script to install deep learning libraries
"""

import subprocess
import sys
import os
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

def install_libraries(gpu_available):
    """Install deep learning libraries"""
    print_header("Installing Deep Learning Libraries")
    
    # List of libraries to install
    libraries = [
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
        "scikit-learn",
        "h5py",
        "pillow",
        "tqdm"
    ]
    
    # Install base libraries
    print("Installing base libraries...")
    for lib in libraries:
        run_command(f"{sys.executable} -m pip install {lib}")
    
    # Install TensorFlow
    print("\nInstalling TensorFlow...")
    if gpu_available:
        run_command(f"{sys.executable} -m pip install tensorflow[and-cuda]")
    else:
        run_command(f"{sys.executable} -m pip install tensorflow")
    
    # Install PyTorch
    print("\nInstalling PyTorch...")
    if gpu_available:
        run_command(f"{sys.executable} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    else:
        run_command(f"{sys.executable} -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu")
    
    # Install Keras
    print("\nInstalling Keras...")
    run_command(f"{sys.executable} -m pip install keras")
    
    # Install Transformers
    print("\nInstalling Hugging Face Transformers...")
    run_command(f"{sys.executable} -m pip install transformers")
    
    # Install other useful libraries
    print("\nInstalling other useful libraries...")
    other_libs = [
        "nltk",
        "gensim",
        "spacy",
        "opencv-python",
        "tensorflow-hub",
        "tensorboard"
    ]
    
    for lib in other_libs:
        run_command(f"{sys.executable} -m pip install {lib}")

def verify_installation():
    """Verify installation of deep learning libraries"""
    print_header("Verifying Installation")
    
    libraries = [
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
        "sklearn",
        "tensorflow",
        "torch",
        "keras",
        "transformers"
    ]
    
    for lib in libraries:
        try:
            module = __import__(lib)
            print(f"{lib}: {module.__version__ if hasattr(module, '__version__') else 'Installed'}")
        except ImportError:
            print(f"{lib}: Not installed")
        except Exception as e:
            print(f"{lib}: Error - {e}")

def main():
    """Main function"""
    print_header("Deep Learning Libraries Installation")
    
    # Check Python environment
    check_python_environment()
    
    # Check for GPU
    gpu_available = check_gpu()
    
    # Install libraries
    install_libraries(gpu_available)
    
    # Verify installation
    verify_installation()
    
    print_header("Installation Completed")
    print("Please check the output above for any errors.")

if __name__ == "__main__":
    main()