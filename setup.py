import os
import platform
from pathlib import Path
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir
import pybind11
from setuptools import setup, Extension
import numpy

def get_fftw_paths():
    """Get FFTW static library paths."""
    base_dir = Path("src/nbody/_nbody_c/fftw_static")
    
    include_dir = base_dir / "include"
    lib_dir = base_dir / "lib"
    
    # Single-precision FFTW libraries
    fftw_libs = []
    required_libs = ["libfftw3f.a", "libfftw3f_omp.a", "libfftw3f_threads.a"]
    
    for lib_name in required_libs:
        lib_file = lib_dir / lib_name
        if lib_file.exists():
            fftw_libs.append(str(lib_file.absolute()))
        else:
            print(f"Warning: {lib_name} not found at {lib_file}")
    
    return str(include_dir.absolute()), str(lib_dir.absolute()), fftw_libs

def get_compile_args():
    """Get platform-specific compile arguments."""
    system = platform.system()
    args = ["-O3", "-std=c99", "-Wall", "-Wno-unused-variable", "-Wno-unused-function"]
    
    if system == "Darwin":  # macOS
        # Use different OpenMP flags for macOS
        args.extend(["-Xpreprocessor", "-fopenmp"])
    elif system == "Windows":
        # Windows-specific flags
        args.extend(["-fopenmp"])  # MinGW supports this
    else:  # Linux
        args.extend(["-fopenmp"])
    
    return args

def get_link_args():
    """Get platform-specific link arguments."""
    system = platform.system()
    args = ["-lm"]
    
    if system == "Darwin":  # macOS
        # macOS OpenMP linking
        args.extend(["-lomp"])
    elif system == "Windows":
        # Windows linking
        args.extend(["-fopenmp", "-lpthread"])
    else:  # Linux
        args.extend(["-fopenmp", "-lpthread"])
    
    return args

# Get FFTW paths and libraries
fftw_include, fftw_lib_dir, fftw_libs = get_fftw_paths()

# Source files
source_files = [
    "src/nbody/_nbody_c/nbody_wrapper.c",
    "src/nbody/_nbody_c/nbody_comp.c", 
    "src/nbody/_nbody_c/nbody_funcs.c",
    "src/nbody/_nbody_c/allotarrays.c",
    "src/nbody/_nbody_c/funcs.c",
    "src/nbody/_nbody_c/powerspec.c",
    "src/nbody/_nbody_c/tf_fit.c"
]

print("Building N-body simulation C extension...")
print(f"Source files: {source_files}")
print(f"FFTW include: {fftw_include}")
print(f"FFTW libraries: {fftw_libs}")
print(f"Platform: {platform.system()}")

# Create extension
ext_modules = [
    Extension(
        "nbody._nbody_c",
        sources=source_files,
        include_dirs=[
            numpy.get_include(),
            fftw_include,
            "src/nbody/_nbody_c"
        ],
        library_dirs=[fftw_lib_dir],
        extra_objects=fftw_libs,
        extra_compile_args=get_compile_args(),
        extra_link_args=get_link_args(),
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
    )
]

if __name__ == "__main__":
    setup(ext_modules=ext_modules)
