#!/usr/bin/env python3
"""
macOS Installation Script for N-body Simulation
"""
import subprocess
import sys
import os
import tempfile
import shutil

def run_command(cmd, capture=True):
    """Run a command and return result."""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)

def install_dependencies():
    """Install required dependencies for macOS."""
    print("🍎 Installing dependencies for macOS...")
    
    # Try to install FFTW via conda/mamba first
    success, _, _ = run_command("conda install -c conda-forge fftw -y")
    if success:
        print("✅ FFTW installed via conda")
        return True
    
    # Try via pip
    success, _, _ = run_command(f"{sys.executable} -m pip install pyfftw")
    if success:
        print("✅ PyFFTW installed via pip")
    
    # Try to install OpenMP
    success, _, _ = run_command(f"{sys.executable} -m pip install llvm-openmp")
    if success:
        print("✅ OpenMP support installed")
    
    return True

def install_nbody():
    """Install the N-body simulation package."""
    print("📦 Installing N-body simulation...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        # Clone repository
        success, _, _ = run_command("git clone https://github.com/PragunNepal/nbody-simulation.git")
        if not success:
            print("❌ Failed to clone repository")
            return False
        
        os.chdir("nbody-simulation")
        
        # Use macOS setup if available
        if os.path.exists("setup_macos.py"):
            print("🔧 Using macOS-specific setup...")
            shutil.copy("setup_macos.py", "setup.py")
        
        # Install the package
        success, stdout, stderr = run_command(f"{sys.executable} -m pip install .")
        
        if success:
            print("✅ Installation successful!")
            return True
        else:
            print("❌ Installation failed:")
            print(stderr[-500:])  # Last 500 chars
            return False

def test_installation():
    """Test the installation."""
    try:
        import nbody
        print(f"✅ Import successful! Version: {nbody.__version__}")
        
        # Quick test
        result = nbody.run()
        if result.get('status') == 'success':
            print("🎉 N-body simulation is working!")
            return True
        else:
            print(f"⚠️  Test result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🚀 N-body Simulation - macOS Installer")
    print("=" * 50)
    
    # Step 1: Install dependencies
    install_dependencies()
    
    # Step 2: Install package
    if install_nbody():
        # Step 3: Test
        if test_installation():
            print("\n🎉 SUCCESS! N-body simulation is ready to use!")
            print("\n📖 Usage in Jupyter:")
            print("   import nbody")
            print("   result = nbody.run()")
        else:
            print("\n⚠️  Installation completed but testing failed")
    else:
        print("\n❌ Installation failed")

if __name__ == "__main__":
    main()
