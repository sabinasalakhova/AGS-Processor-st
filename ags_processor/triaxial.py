"""
Triaxial Test Processing Module

Re-exports functions directly from legacy/agsfileanalysis/triaxial.py
No duplication - uses original implementations.
"""

import sys
from pathlib import Path

# Add legacy directory to path
legacy_path = Path(__file__).parent.parent / "legacy" / "agsfileanalysis"
if str(legacy_path) not in sys.path:
    sys.path.insert(0, str(legacy_path))

# Import all functions from legacy triaxial.py
try:
    from triaxial import (
        generate_triaxial_table,
        generate_triaxial_with_lithology,
        calculate_s_t_values,
        remove_duplicate_tests
    )
except ImportError as e:
    print(f"Warning: Could not import from legacy triaxial: {e}")
    # Define stub functions if legacy not available
    def generate_triaxial_table(*args, **kwargs):
        raise NotImplementedError("Legacy triaxial module not found")
    def generate_triaxial_with_lithology(*args, **kwargs):
        raise NotImplementedError("Legacy triaxial module not found")
    def calculate_s_t_values(*args, **kwargs):
        raise NotImplementedError("Legacy triaxial module not found")
    def remove_duplicate_tests(*args, **kwargs):
        raise NotImplementedError("Legacy triaxial module not found")

__all__ = [
    'generate_triaxial_table',
    'generate_triaxial_with_lithology',
    'calculate_s_t_values',
    'remove_duplicate_tests'
]
