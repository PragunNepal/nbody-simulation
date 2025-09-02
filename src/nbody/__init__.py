"""
N-body Simulation Package

A high-performance N-body simulation package that works across all platforms.
Automatically compiles and runs C-based simulation code.
"""

from .core import (
    run_nbody, 
    run_simulation, 
    run,
    NBodySimulation,
    __version__
)

__all__ = [
    'run_nbody',
    'run_simulation', 
    'run',
    'NBodySimulation',
    '__version__'
]
