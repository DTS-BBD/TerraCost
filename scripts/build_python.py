#!/usr/bin/env python3
"""
Build script for creating standalone TerraCost executables using PyInstaller.
This creates platform-specific executables that will be bundled with the VSCode extension.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✓ PyInstaller already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✓ PyInstaller installed successfully")

def build_platform_executable():
    """Build TerraCost executable for current platform"""
    platform_name = platform.system().lower()
    arch = platform.machine()
    
    print(f"Building for platform: {platform_name} ({arch})")
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    # Create build directory
    build_dir = script_dir / "python" / platform_name
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--distpath", str(build_dir),
        "--workpath", str(script_dir / "build"),
        "--specpath", str(script_dir / "build"),
        "--hidden-import", "terracost",
        "--hidden-import", "boto3",
        "--hidden-import", "openai",
        "--hidden-import", "langchain",
        "--hidden-import", "terraform",
        "--hidden-import", "yaml",
        "--hidden-import", "json",
        "--hidden-import", "pathlib",
        "--hidden-import", "typing",
        "--hidden-import", "asyncio",
        "--hidden-import", "aiohttp",
        "--hidden-import", "requests",
        "--name", "terracost",
        "terracost/main.py"
    ]
    
    print(f"Running PyInstaller: {' '.join(cmd)}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ PyInstaller completed successfully")
        
        # Check if executable was created
        if platform_name == "windows":
            executable_path = build_dir / "terracost.exe"
        else:
            executable_path = build_dir / "terracost"
        
        if executable_path.exists():
            print(f"✓ Executable created: {executable_path}")
            
            # Make executable on Unix systems
            if platform_name != "windows":
                os.chmod(executable_path, 0o755)
                print("✓ Executable permissions set")
            
            # Test the executable
            print("Testing executable...")
            test_result = subprocess.run([str(executable_path), "--help"], 
                                       capture_output=True, text=True, timeout=10)
            
            if test_result.returncode == 0:
                print("✓ Executable test passed")
            else:
                print(f"⚠ Executable test failed: {test_result.stderr}")
                
        else:
            print(f"❌ Executable not found at {executable_path}")
            print("PyInstaller output:")
            print(result.stdout)
            print("PyInstaller errors:")
            print(result.stderr)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller failed: {e}")
        print("Stdout:", e.stdout)
        print("Stderr:", e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

def clean_build_files():
    """Clean up temporary build files"""
    script_dir = Path(__file__).parent.parent
    build_dirs = ["build", "dist", "__pycache__"]
    
    for dir_name in build_dirs:
        dir_path = script_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"✓ Cleaned {dir_name}")

def main():
    """Main build process"""
    print("🚀 Building TerraCost Python Runtime for VSCode Extension")
    print("=" * 60)
    
    try:
        # Install PyInstaller
        install_pyinstaller()
        
        # Build executable
        build_platform_executable()
        
        # Clean up
        clean_build_files()
        
        print("\n🎉 Build completed successfully!")
        print("The executable is ready in the python/ directory")
        
    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
