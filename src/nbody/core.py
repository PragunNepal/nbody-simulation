"""
Core Python interface for N-body simulation.

This module provides a Python interface to your existing C simulation code,
maintaining exact functionality while adding Python convenience features.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, Union, List
import pkg_resources
from . import _nbody_c


def run_nbody(input_file: Optional[Union[str, Path]] = None, 
              output_dir: Optional[Union[str, Path]] = None,
              verbose: bool = True) -> Dict[str, Any]:
    """
    Run N-body simulation - equivalent to your current: make nbody_comp && ./nbody_comp
    
    This function does EXACTLY what your current C code does:
    - Uses your input.nbody_comp file (built-in or custom)
    - Runs your simulation with FFTW
    - Generates output files in specified directory
    - Returns status and file information
    
    Parameters:
    -----------
    input_file : str, Path, or None
        Path to input.nbody_comp file. If None, uses built-in file from package.
    output_dir : str, Path, or None
        Directory for output files. If None, uses current directory.
    verbose : bool
        Whether to print progress messages.
    
    Returns:
    --------
    dict
        Dictionary containing:
        - 'status': 'success' or 'error'
        - 'return_code': Integer return code from C simulation
        - 'input_file': Path to input file used
        - 'output_directory': Path to output directory
        - 'output_files': List of output files created
        - 'message': Status message
        
    Examples:
    ---------
    >>> import nbody
    >>> 
    >>> # Use built-in input.nbody_comp file
    >>> result = nbody.run_nbody()
    >>> 
    >>> # Use custom input file
    >>> result = nbody.run_nbody("my_custom_input.nbody_comp")
    >>> 
    >>> # Specify output directory
    >>> result = nbody.run_nbody(output_dir="simulation_results/")
    """
    
    # Handle input file
    temp_input_file = None
    if input_file is None:
        # Use built-in input.nbody_comp file
        try:
            if verbose:
                print("Using built-in input.nbody_comp file...")
            
            # Get the package directory and find the data file
            import nbody
            package_dir = Path(nbody.__file__).parent
            built_in_file = package_dir / "data" / "input.nbody_comp"
            
            if built_in_file.exists():
                # Create temp directory
                temp_dir = Path.cwd() / ".nbody_temp"
                temp_dir.mkdir(exist_ok=True)
                temp_input_file = temp_dir / "input.nbody_comp"
                
                # Copy built-in file to temp location
                shutil.copy2(built_in_file, temp_input_file)
                input_file = temp_input_file
            else:
                raise FileNotFoundError(f"Built-in input.nbody_comp not found at {built_in_file}")
                    
        except Exception as e:
            raise FileNotFoundError(
                f"Cannot access built-in input.nbody_comp file. "
                f"Please specify input_file parameter. Error: {e}"
            )
    else:
        # Use provided input file
        input_file = Path(input_file)
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Handle output directory
    if output_dir is None:
        output_dir = Path.cwd()
        if verbose:
            print(f"Using current directory for output: {output_dir}")
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        if verbose:
            print(f"Output directory: {output_dir}")
    
    # Convert to absolute paths for C code
    input_file_str = str(input_file.resolve())
    output_dir_str = str(output_dir.resolve())
    
    if verbose:
        print(f"Input file: {input_file_str}")
        print("Starting simulation...")
    
    try:
        # Call your C extension (equivalent to ./nbody_comp)
        return_code = _nbody_c.run_nbody_simulation(input_file_str, output_dir_str)
        
        if verbose:
            print(f"Simulation completed with return code: {return_code}")
        
    except Exception as e:
        # Clean up temp file if created
        if temp_input_file and temp_input_file.exists():
            try:
                shutil.rmtree(temp_input_file.parent)
            except:
                pass
        raise RuntimeError(f"Simulation failed: {e}")
    
    # Find output files created
    output_files = []
    if output_dir.exists():
        # Look for common output file patterns (adjust based on what your C code creates)
        patterns = ['*.out', '*.dat', '*.txt', '*.csv', '*.log', '*.results', '*.output', 'pk.*', '*.zel', '*.nbody*']
        for pattern in patterns:
            output_files.extend(output_dir.glob(pattern))
    
    # Clean up temporary input file
    if temp_input_file and temp_input_file.exists():
        try:
            shutil.rmtree(temp_input_file.parent)
        except:
            pass  # Don't fail on cleanup errors
    
    # Prepare result
    success = (return_code == 0)
    result = {
        "status": "success" if success else "error",
        "return_code": return_code,
        "input_file": str(input_file),
        "output_directory": str(output_dir),
        "output_files": [str(f) for f in output_files],
        "message": f"Simulation {'completed successfully' if success else 'failed'} (code: {return_code})"
    }
    
    if verbose:
        print(result["message"])
        if output_files:
            print(f"Created {len(output_files)} output file(s):")
            for f in output_files[:5]:  # Show first 5 files
                print(f"  - {f.name}")
            if len(output_files) > 5:
                print(f"  ... and {len(output_files) - 5} more")
    
    return result


# Convenient aliases
def run_simulation(input_file: Optional[Union[str, Path]] = None, **kwargs) -> Dict[str, Any]:
    """Alias for run_nbody() - same functionality."""
    return run_nbody(input_file, **kwargs)


def run(input_file: Optional[Union[str, Path]] = None, **kwargs) -> Dict[str, Any]:
    """Short alias for run_nbody() - same functionality."""
    return run_nbody(input_file, **kwargs)


class NBodySimulation:
    """
    Object-oriented interface for N-body simulation.
    
    This class provides a convenient way to run multiple simulations,
    manage different input files, and organize results.
    """
    
    def __init__(self, default_input_file: Optional[str] = None, 
                 default_output_dir: Optional[str] = None,
                 verbose: bool = True):
        """
        Initialize simulation manager.
        
        Parameters:
        -----------
        default_input_file : str, optional
            Default input.nbody_comp file to use for all simulations
        default_output_dir : str, optional
            Default output directory for all simulations
        verbose : bool
            Whether to print progress messages
        """
        self.default_input_file = default_input_file
        self.default_output_dir = default_output_dir
        self.verbose = verbose
        self.results_history = []
    
    def run(self, input_file: Optional[str] = None, 
            output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Run simulation with specified or default parameters.
        """
        # Use instance defaults if not specified
        if input_file is None:
            input_file = self.default_input_file
        if output_dir is None:
            output_dir = self.default_output_dir
        
        # Run simulation
        result = run_nbody(input_file, output_dir, self.verbose)
        
        # Store result
        self.results_history.append(result)
        
        return result
    
    def get_last_result(self) -> Optional[Dict[str, Any]]:
        """Get the most recent simulation result."""
        return self.results_history[-1] if self.results_history else None
    
    def summary(self):
        """Print a summary of all runs."""
        if not self.results_history:
            print("No simulations have been run yet.")
            return
        
        successful = sum(1 for r in self.results_history if r['status'] == 'success')
        total = len(self.results_history)
        
        print(f"Simulation Summary:")
        print(f"  Total runs: {total}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {total - successful}")
        
        if self.results_history:
            latest = self.results_history[-1]
            print(f"  Latest status: {latest['status']}")
            print(f"  Latest output: {len(latest['output_files'])} files")


# Optional: Command line interface
def main():
    """Command line interface for the package."""
    import sys
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        result = run_nbody(input_file, output_dir)
        print(f"Command line run: {result['status']}")
        sys.exit(result['return_code'])
    else:
        result = run_nbody()
        print(f"Default run: {result['status']}")
        sys.exit(result['return_code'])
