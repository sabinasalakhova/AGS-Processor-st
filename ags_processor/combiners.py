"""
File Combination Module

Re-exports functions directly from legacy/AGS-Processor/ags_core.py
No duplication - uses original implementations.
"""

import sys
from pathlib import Path

# Add legacy directory to path
legacy_path = Path(__file__).parent.parent / "legacy" / "AGS-Processor"
if str(legacy_path) not in sys.path:
    sys.path.insert(0, str(legacy_path))

# Import combiner functions from legacy ags_core.py
try:
    from ags_core import (
        concat_ags_files,
        combine_ags_data
    )
except ImportError as e:
    print(f"Warning: Could not import from legacy ags_core: {e}")
    # Define stub functions if legacy not available
    def concat_ags_files(*args, **kwargs):
        raise NotImplementedError("Legacy ags_core module not found")
    def combine_ags_data(*args, **kwargs):
        raise NotImplementedError("Legacy ags_core module not found")

__all__ = [
    'concat_ags_files',
    'combine_ags_data'
]
