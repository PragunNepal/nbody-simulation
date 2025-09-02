#!/usr/bin/env python3
"""
Basic test to verify the Python interface works.
"""

# Test basic import
try:
    import sys
    sys.path.insert(0, 'src')  # Add src to path for development
    import nbody
    print("✅ Successfully imported nbody package")
    print(f"Version: {nbody.__version__}")
except ImportError as e:
    print(f"❌ Failed to import nbody: {e}")
    sys.exit(1)

# Test that we can access the functions
try:
    assert hasattr(nbody, 'run_nbody')
    assert hasattr(nbody, 'run')
    assert hasattr(nbody, 'NBodySimulation')
    print("✅ All main functions are available")
except AssertionError:
    print("❌ Missing required functions")
    sys.exit(1)

# Test data file exists
try:
    from pathlib import Path
    data_file = Path("src/nbody/data/input.nbody_comp")
    if data_file.exists():
        print("✅ Input data file found")
        print(f"   File size: {data_file.stat().st_size} bytes")
    else:
        print("❌ Input data file not found")
        print(f"   Looking for: {data_file.absolute()}")
except Exception as e:
    print(f"❌ Error checking data file: {e}")

print("\n🎉 Phase 4 Python interface setup complete!")
print("Next: Phase 5 - Build Configuration")
