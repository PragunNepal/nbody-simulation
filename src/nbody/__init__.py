"""
N-body Simulation Package

High-performance N-body simulation library using FFTW.
Transform your existing C simulation into a Python library.
"""

from .core import run_nbody, run_simulation, run, NBodySimulation

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "N-body simulation with FFTW - converted from C to Python library"

# Main functions available to users
__all__ = [
    "run_nbody",      # Main function 
    "run_simulation", # Alias
    "run",           # Short alias
    "NBodySimulation" # Class interface
]

# Quick usage info
print(f"N-body simulation library v{__version__} loaded successfully!")
print("Quick start: import nbody; nbody.run()")
