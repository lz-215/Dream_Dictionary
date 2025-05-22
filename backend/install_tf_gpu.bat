@echo off
echo ============================================================
echo  TensorFlow GPU Installation Script
echo ============================================================

echo.
echo Uninstalling existing TensorFlow packages...
pip uninstall -y tensorflow tensorflow-cpu tensorflow-gpu tensorflow-io-gcs-filesystem
echo Uninstallation completed.

echo.
echo Checking for NVIDIA GPU...
nvidia-smi
if %ERRORLEVEL% NEQ 0 (
    echo No NVIDIA GPU detected or drivers not installed.
    echo Installing standard TensorFlow...
    pip install tensorflow
) else (
    echo NVIDIA GPU detected!
    echo Installing TensorFlow with GPU support...
    pip install tensorflow[and-cuda]
)

echo.
echo Verifying installation...
pip list | findstr tensor

echo.
echo Installation completed!
echo Please run 'python -c "import tensorflow as tf; print(tf.__version__)"' to verify.
