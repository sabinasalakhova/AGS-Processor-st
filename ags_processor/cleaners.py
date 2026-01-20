"""
Data Cleaning Module

Re-exports functions directly from legacy/agsfileanalysis/cleaners.py
No duplication - uses original implementations.
"""

import sys
from pathlib import Path

# Add legacy directory to path
legacy_path = Path(__file__).parent.parent / "legacy" / "agsfileanalysis"
if str(legacy_path) not in sys.path:
    sys.path.insert(0, str(legacy_path))

# Import all functions from legacy cleaners.py
try:
    from cleaners import (
        normalize_columns,
        drop_singleton_rows,
        deduplicate_cell,
        expand_rows,
        combine_groups,
        coalesce_columns,
        to_numeric_safe
    )
except ImportError as e:
    print(f"Warning: Could not import from legacy cleaners: {e}")
    # Define stub functions if legacy not available
    def normalize_columns(*args, **kwargs):
        raise NotImplementedError("Legacy cleaners module not found")
    def drop_singleton_rows(*args, **kwargs):
        raise NotImplementedError("Legacy cleaners module not found")
    def deduplicate_cell(*args, **kwargs):
        raise NotImplementedError("Legacy cleaners module not found")
    def expand_rows(*args, **kwargs):
        raise NotImplementedError("Legacy cleaners module not found")
    def combine_groups(*args, **kwargs):
        raise NotImplementedError("Legacy cleaners module not found")
    def coalesce_columns(*args, **kwargs):
        raise NotImplementedError("Legacy cleaners module not found")
    def to_numeric_safe(*args, **kwargs):
        raise NotImplementedError("Legacy cleaners module not found")

__all__ = [
    'normalize_columns',
    'drop_singleton_rows',
    'deduplicate_cell',
    'expand_rows',
    'combine_groups',
    'coalesce_columns',
    'to_numeric_safe'
]
