import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
import pkg_resources

__version__ = "0.1.0"

def get_data_file():
    """Get path to built-in input.nbody_comp file."""
    try:
        return pkg_resources.resource_filename('nbody', 'data/input.nbody_comp')
    except:
        # Fallback
        return Path(__file__).parent / 'data' / 'input.nbody_comp'

def compile_nbody_executable(temp_dir):
    """Compile the N-body executable in temp directory."""
    import platform
    
    print("🔧 Compiling N-body simulation...")
    
    # Get source files from package
    source_dir = Path(__file__).parent / '_nbody_c'
    
    source_files = [
        'nbody_comp.c', 'nbody_funcs.c', 'allotarrays.c', 
        'funcs.c', 'powerspec.c', 'tf_fit.c'
    ]
    
    # Copy source files to temp directory
    temp_src = Path(temp_dir) / 'src'
    temp_src.mkdir(exist_ok=True)
    
    for src_file in source_files:
        src_path = source_dir / src_file
        if src_path.exists():
            shutil.copy2(src_path, temp_src / src_file)
    
    # Copy headers
    for header in ['nbody.h', 'power1.h']:
        header_path = source_dir / header
        if header_path.exists():
            shutil.copy2(header_path, temp_src / header)
    
    # Platform-specific compilation
    system = platform.system()
    exe_name = 'nbody_comp.exe' if system == 'Windows' else 'nbody_comp'
    exe_path = Path(temp_dir) / exe_name
    
    # Compilation command
    if system == "Windows":
        compile_cmd = [
            "gcc", "-O3", "-std=c99", "-fopenmp",
            "-o", str(exe_path)
        ] + [str(temp_src / f) for f in source_files] + [
            "-lm", "-lfftw3f", "-lfftw3f_omp"
        ]
    elif system == "Darwin":  # macOS
        compile_cmd = [
            "gcc", "-O3", "-std=c99", 
            "-I/opt/homebrew/include", "-I/usr/local/include",
            "-L/opt/homebrew/lib", "-L/usr/local/lib",
            "-o", str(exe_path)
        ] + [str(temp_src / f) for f in source_files] + [
            "-lm", "-lfftw3f", "-lfftw3f_omp", "-lomp"
        ]
    else:  # Linux
        compile_cmd = [
            "gcc", "-O3", "-std=c99", "-fopenmp",
            "-o", str(exe_path)
        ] + [str(temp_src / f) for f in source_files] + [
            "-lm", "-lfftw3f", "-lfftw3f_omp"
        ]
    
    try:
        result = subprocess.run(compile_cmd, 
                              capture_output=True, text=True, 
                              cwd=temp_dir)
        
        if result.returncode == 0 and exe_path.exists():
            print("✅ Compilation successful!")
            return str(exe_path)
        else:
            print(f"⚠️  Compilation failed: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("⚠️  Compiler not found. Please install gcc.")
        return None
    except Exception as e:
        print(f"⚠️  Compilation error: {e}")
        return None

def run_nbody_simulation(input_file=None, output_dir="."):
    """Run N-body simulation using compiled executable."""
    
    # Use built-in data if no input file provided
    if input_file is None:
        input_file = get_data_file()
    
    # Convert to absolute paths
    input_file = Path(input_file).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(exist_ok=True)
    
    if not input_file.exists():
        return {
            "status": "error",
            "message": f"Input file not found: {input_file}",
            "output_files": [],
            "return_code": -1
        }
    
    print(f"🚀 Running N-body simulation...")
    print(f"📁 Input: {input_file}")
    print(f"📁 Output: {output_dir}")
    
    # Create temporary directory for compilation and execution
    with tempfile.TemporaryDirectory() as temp_dir:
        
        # Try to compile executable
        executable = compile_nbody_executable(temp_dir)
        
        if executable is None:
            return {
                "status": "error", 
                "message": "Failed to compile N-body executable. Please install gcc and FFTW.",
                "output_files": [],
                "return_code": -1
            }
        
        # Copy input file to working directory  
        work_input = Path(temp_dir) / "input.nbody_comp"
        shutil.copy2(input_file, work_input)
        
        # Run simulation
        try:
            result = subprocess.run([executable], 
                                  cwd=temp_dir,
                                  capture_output=True, 
                                  text=True)
            
            print(f"📊 Simulation completed with return code: {result.returncode}")
            
            # Copy output files to destination
            output_files = []
            for output_file in Path(temp_dir).glob("*"):
                if (output_file.is_file() and 
                    output_file.name not in ["input.nbody_comp", "nbody_comp", "nbody_comp.exe"] and
                    not output_file.name.endswith(('.c', '.h', '.o'))):
                    
                    dest_file = output_dir / output_file.name
                    shutil.copy2(output_file, dest_file)
                    output_files.append(str(dest_file))
            
            return {
                "status": "success" if result.returncode == 0 else "warning",
                "message": f"Simulation completed. Generated {len(output_files)} output files.",
                "output_files": output_files,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Execution failed: {e}",
                "output_files": [],
                "return_code": -1
            }

def run_nbody(input_file=None, output_dir=".", **kwargs):
    """Run N-body simulation (main interface)."""
    return run_nbody_simulation(input_file, output_dir)

def run_simulation(input_file=None, **kwargs):
    """Alias for run_nbody."""
    return run_nbody(input_file, **kwargs)

def run(input_file=None, **kwargs):
    """Simple run interface."""
    return run_nbody(input_file, **kwargs)

class NBodySimulation:
    """Object-oriented interface for N-body simulation."""
    
    def __init__(self):
        self.last_result = None
    
    def run(self, input_file=None, output_dir="nbody_output"):
        """Run simulation and store result."""
        self.last_result = run_nbody_simulation(input_file, output_dir)
        return self.last_result
    
    def summary(self):
        """Print summary of last simulation."""
        if self.last_result:
            print(f"Status: {self.last_result['status']}")
            print(f"Output files: {len(self.last_result['output_files'])}")
            print(f"Message: {self.last_result['message']}")
        else:
            print("No simulation run yet.")

# Module initialization
print(f"N-body simulation library v{__version__} loaded successfully!")
print("Quick start: import nbody; nbody.run()")

# Installation check
try:
    import subprocess
    result = subprocess.run(["gcc", "--version"], capture_output=True)
    if result.returncode != 0:
        print("⚠️  Warning: gcc not found. You may need to install a C compiler.")
        print("   macOS: xcode-select --install")
        print("   Windows: Install MinGW or Visual Studio")
        print("   Linux: sudo apt install gcc")
except:
    print("⚠️  Warning: C compiler check failed.")
