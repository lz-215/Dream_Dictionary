@echo off
echo ============================================================
echo  Deep Learning Libraries Installation
echo ============================================================

echo.
echo Installing NumPy...
pip install numpy

echo.
echo Installing SciPy...
pip install scipy

echo.
echo Installing Pandas...
pip install pandas

echo.
echo Installing Matplotlib...
pip install matplotlib

echo.
echo Installing scikit-learn...
pip install scikit-learn

echo.
echo Installing TensorFlow...
pip install tensorflow

echo.
echo Installing Keras...
pip install keras

echo.
echo Installing PyTorch...
pip install torch torchvision torchaudio

echo.
echo Installing Transformers...
pip install transformers

echo.
echo Installation completed!
echo Checking installed libraries...
pip list | findstr "numpy scipy pandas matplotlib scikit-learn tensorflow keras torch transformers"
