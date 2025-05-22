"""
Verify TensorFlow GPU installation
"""

import tensorflow as tf
print(f"TensorFlow version: {tf.__version__}")
print(f"GPU available: {tf.config.list_physical_devices('GPU')}")

# Check if TensorFlow can see the GPU
if tf.config.list_physical_devices('GPU'):
    print("GPU is available for TensorFlow!")
    
    # Test GPU with a simple operation
    with tf.device('/GPU:0'):
        a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
        b = tf.constant([[5.0, 6.0], [7.0, 8.0]])
        c = tf.matmul(a, b)
        print(f"Matrix multiplication result: {c}")
else:
    print("No GPU available for TensorFlow.")
    print("This could be because:")
    print("1. Your system doesn't have a compatible NVIDIA GPU")
    print("2. CUDA and cuDNN are not properly installed")
    print("3. You're using a CPU-only version of TensorFlow")
    
    # Check if we're using CPU version
    print("\nChecking TensorFlow build information:")
    print(tf.sysconfig.get_build_info())