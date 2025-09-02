import os
import platform
from pathlib import Path
from setuptools import setup, Extension
import numpy

def get_macos_extension():
    """Create macOS-compatible extension without static FFTW."""
    
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

    print("Building N-body simulation C extension for macOS...")
    print("Using system FFTW libraries...")
    
    # Try to find system FFTW
    include_dirs = [numpy.get_include(), "src/nbody/_nbody_c"]
    libraries = []
    library_dirs = []
    
    # Check common macOS paths for FFTW
    fftw_paths = [
        "/opt/homebrew/lib",  # Apple Silicon Homebrew
        "/usr/local/lib",     # Intel Homebrew
        "/opt/local/lib",     # MacPorts
    ]
    
    fftw_include_paths = [
        "/opt/homebrew/include",
        "/usr/local/include", 
        "/opt/local/include",
    ]
    
    # Add FFTW paths if they exist
    for path in fftw_include_paths:
        if os.path.exists(path + "/fftw3.h"):
            include_dirs.append(path)
            print(f"Found FFTW headers at: {path}")
            break
    
    for path in fftw_paths:
        if os.path.exists(path + "/libfftw3f.dylib") or os.path.exists(path + "/libfftw3f.a"):
            library_dirs.append(path)
            libraries.extend(["fftw3f", "fftw3f_omp", "fftw3f_threads"])
            print(f"Found FFTW libraries at: {path}")
            break
    
    if not libraries:
        print("Warning: System FFTW not found. Building minimal version...")
        # Build without FFTW for now - you'll need to install FFTW separately
        libraries = ["m"]
    
    # Compile args for macOS
    compile_args = ["-O3", "-std=c99", "-Wall", "-Wno-unused-variable", "-Wno-unused-function"]
    link_args = ["-lm"]
    
    # Try to add OpenMP if available
    try:
        # Check if libomp is available
        for path in fftw_paths:
            if os.path.exists(path + "/libomp.dylib"):
                compile_args.append("-fopenmp")
                link_args.append("-lomp")
                print("OpenMP support enabled")
                break
    except:
        print("Building without OpenMP support")
    
    return Extension(
        "nbody._nbody_c",
        sources=source_files,
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        extra_compile_args=compile_args,
        extra_link_args=link_args,
        define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")]
    )

if __name__ == "__main__":
    setup(ext_modules=[get_macos_extension()])
