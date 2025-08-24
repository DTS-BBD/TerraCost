#!/usr/bin/env python3
"""
TerraCost Release Script
Automates the process of releasing to PyPI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command and return the result"""
    print(f"🔄 Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"❌ Command failed: {command}")
        print(f"Error: {result.stderr}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return result
    
    print(f"✅ Command completed: {command}")
    return result

def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        if os.path.exists(pattern):
            shutil.rmtree(pattern)
            print(f"   Removed: {pattern}")

def build_package():
    """Build the package distribution"""
    print("🔨 Building package distribution...")
    
    # Build source distribution and wheel
    run_command("python -m build")
    
    # List what was created
    if os.path.exists("dist"):
        print("📦 Created distribution files:")
        for file in os.listdir("dist"):
            print(f"   - {file}")

def test_installation():
    """Test installing the package locally"""
    print("🧪 Testing local installation...")
    
    # Install in a test environment (Windows compatible)
    if os.name == 'nt':  # Windows
        # Find the wheel file
        wheel_files = [f for f in os.listdir("dist") if f.endswith(".whl")]
        if wheel_files:
            wheel_file = os.path.join("dist", wheel_files[0])
            run_command(f"pip install \"{wheel_file}\" --force-reinstall")
        else:
            print("❌ No wheel file found in dist directory")
            return False
    else:  # Unix/Linux/Mac
        run_command("pip install dist/*.whl --force-reinstall")
    
    # Test the CLI
    try:
        result = subprocess.run(["terracost", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CLI test successful!")
            print(f"   Version: {result.stdout.strip()}")
        else:
            print("❌ CLI test failed!")
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"❌ CLI test failed with exception: {e}")

def upload_to_test_pypi():
    """Upload to Test PyPI first"""
    print("🚀 Uploading to Test PyPI...")
    
    # Check if credentials are available
    username = os.getenv("TWINE_USERNAME")
    password = os.getenv("TWINE_PASSWORD")
    
    if not (username and password):
        print("⚠️  Credentials not found in environment variables")
        print("   Please set TWINE_USERNAME and TWINE_PASSWORD")
        print("   Or create a .pypirc file in your home directory")
        
        # Try to prompt for credentials
        print("\n🔑 Enter your Test PyPI credentials:")
        username = input("Username (use '__token__' for API token): ").strip()
        password = input("Password/Token: ").strip()
        
        if not (username and password):
            print("❌ No credentials provided")
            return False
    
    # Set environment variables for this session
    os.environ["TWINE_USERNAME"] = username
    os.environ["TWINE_PASSWORD"] = password
    
    result = run_command("python -m twine upload --repository testpypi dist/*")
    if result.returncode == 0:
        print("✅ Uploaded to Test PyPI successfully!")
        return True
    else:
        print("❌ Failed to upload to Test PyPI")
        return False

def upload_to_pypi():
    """Upload to production PyPI"""
    print("🚀 Uploading to production PyPI...")
    
    # Check if credentials are available
    username = os.getenv("TWINE_USERNAME")
    password = os.getenv("TWINE_PASSWORD")
    
    if not (username and password):
        print("⚠️  Credentials not found in environment variables")
        print("   Please set TWINE_USERNAME and TWINE_PASSWORD")
        print("   Or create a .pypirc file in your home directory")
        
        # Try to prompt for credentials
        print("\n🔑 Enter your PyPI credentials:")
        username = input("Username (use '__token__' for API token): ").strip()
        password = input("Password/Token: ").strip()
        
        if not (username and password):
            print("❌ No credentials provided")
            return False
    
    # Set environment variables for this session
    os.environ["TWINE_USERNAME"] = username
    os.environ["TWINE_PASSWORD"] = password
    
    # Ask for confirmation
    response = input("⚠️  Are you sure you want to upload to PRODUCTION PyPI? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Upload cancelled")
        return False
    
    result = run_command("python -m twine upload dist/*")
    if result.returncode == 0:
        print("✅ Uploaded to PyPI successfully!")
        return True
    else:
        print("❌ Failed to upload to PyPI")
        return False

def main():
    """Main release process"""
    print("🎉 TerraCost Release Process")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("terracost") or not os.path.exists("setup.py"):
        print("❌ Error: Must run from the TerraCost root directory")
        sys.exit(1)
    
    # Check if required tools are installed
    try:
        import build
        import twine
    except ImportError:
        print("❌ Required packages not installed. Installing...")
        run_command("pip install build twine")
    
    # Clean previous builds
    clean_build()
    
    # Build the package
    build_package()
    
    # Test the installation
    test_installation()
    
    # Ask user what to do next
    print("\n🎯 Release Options:")
    print("1. Upload to Test PyPI (recommended first)")
    print("2. Upload to production PyPI")
    print("3. Exit without uploading")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        upload_to_test_pypi()
    elif choice == "2":
        upload_to_pypi()
    elif choice == "3":
        print("👋 Exiting without uploading")
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    print("\n🎉 Release process completed!")

if __name__ == "__main__":
    main()
