"""
Check and manage TensorFlow versions
"""

import sys
import subprocess
import pkg_resources

def get_installed_packages():
    """Get all installed packages"""
    return {pkg.key: pkg.version for pkg in pkg_resources.working_set}

def check_tensorflow():
    """Check TensorFlow versions"""
    packages = get_installed_packages()

    tf_packages = {}
    for pkg_name, version in packages.items():
        if 'tensorflow' in pkg_name:
            tf_packages[pkg_name] = version

    print("Installed TensorFlow packages:")
    for pkg_name, version in tf_packages.items():
        print(f"  {pkg_name}: {version}")

    return tf_packages

def uninstall_package(package_name):
    """Uninstall a package"""
    print(f"Uninstalling {package_name}...")
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", package_name])
    print(f"{package_name} uninstalled successfully.")

def install_package(package_name, version=None):
    """Install a package"""
    pkg_spec = package_name
    if version:
        pkg_spec = f"{package_name}=={version}"

    print(f"Installing {pkg_spec}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_spec])
    print(f"{pkg_spec} installed successfully.")

def main():
    """Main function"""
    print("Checking TensorFlow versions...")
    tf_packages = check_tensorflow()

    # If both tensorflow and tensorflow_cpu are installed
    if 'tensorflow' in tf_packages and 'tensorflow-cpu' in tf_packages:
        print("\nBoth tensorflow and tensorflow-cpu are installed.")
        print("Keeping tensorflow and removing tensorflow-cpu...")
        uninstall_package('tensorflow-cpu')

    # If only tensorflow_cpu is installed
    elif 'tensorflow-cpu' in tf_packages and 'tensorflow' not in tf_packages:
        print("\nOnly tensorflow-cpu is installed.")
        print("Replacing tensorflow-cpu with tensorflow...")
        version = tf_packages['tensorflow-cpu']
        uninstall_package('tensorflow-cpu')
        install_package('tensorflow', version)

    # Check final state
    print("\nFinal TensorFlow packages:")
    check_tensorflow()

if __name__ == "__main__":
    main()