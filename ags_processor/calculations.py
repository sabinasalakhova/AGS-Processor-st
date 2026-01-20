"""
Geotechnical Calculations Module

Re-exports functions directly from legacy/AGS-Processor/ags_core.py
No duplication - uses original implementations.
"""

import sys
from pathlib import Path

# Add legacy directory to path
legacy_path = Path(__file__).parent.parent / "legacy" / "AGS-Processor"
if str(legacy_path) not in sys.path:
    sys.path.insert(0, str(legacy_path))

# Import calculation functions from legacy ags_core.py
try:
    from ags_core import (
        weth_grade_to_numeric,
        rock_material_criteria,
        calculate_rockhead,
        calculate_q_value
    )
except ImportError as e:
    print(f"Warning: Could not import from legacy ags_core: {e}")
    # Define stub functions if legacy not available
    def weth_grade_to_numeric(*args, **kwargs):
        raise NotImplementedError("Legacy ags_core module not found")
    def rock_material_criteria(*args, **kwargs):
        raise NotImplementedError("Legacy ags_core module not found")
    def calculate_rockhead(*args, **kwargs):
        raise NotImplementedError("Legacy ags_core module not found")
    def calculate_q_value(*args, **kwargs):
        raise NotImplementedError("Legacy ags_core module not found")

# Wrapper class for backwards compatibility
class GeotechnicalCalculations:
    """
    Wrapper class providing access to legacy geotechnical calculation functions.
    """
    
    def weth_grade_to_numeric(self, *args, **kwargs):
        """Convert weathering grade to numeric."""
        return weth_grade_to_numeric(*args, **kwargs)
    
    def rock_material_criteria(self, *args, **kwargs):
        """Apply rock material criteria."""
        return rock_material_criteria(*args, **kwargs)
    
    def calculate_rockhead(self, *args, **kwargs):
        """Calculate rockhead depth."""
        return calculate_rockhead(*args, **kwargs)
    
    def calculate_q_value(self, *args, **kwargs):
        """Calculate Q-value."""
        return calculate_q_value(*args, **kwargs)
    
    def calculate_q_value_bulk(self, *args, **kwargs):
        """Calculate Q-values for bulk data (alias for calculate_q_value)."""
        return calculate_q_value(*args, **kwargs)
    
    # Additional helper methods
    def detect_rockhead(self, df, **kwargs):
        """Simple wrapper for calculate_rockhead."""
        result = calculate_rockhead(df, **kwargs)
        if isinstance(result, dict) and 'rockhead_depths' in result:
            return result['rockhead_depths']
        return result
    
    def detect_corestones(self, df, min_thickness=0.5, **kwargs):
        """Detect corestones (placeholder - implement if needed)."""
        # This was not in legacy, so return empty for now
        return {}
    
    def interpret_q_value(self, q_value):
        """Interpret Q-value to rock quality category."""
        if q_value < 0.01:
            return "Exceptionally Poor"
        elif q_value < 0.1:
            return "Extremely Poor"
        elif q_value < 1:
            return "Very Poor"
        elif q_value < 4:
            return "Poor"
        elif q_value < 10:
            return "Fair"
        elif q_value < 40:
            return "Good"
        elif q_value < 100:
            return "Very Good"
        elif q_value < 400:
            return "Extremely Good"
        else:
            return "Exceptionally Good"

__all__ = [
    'weth_grade_to_numeric',
    'rock_material_criteria',
    'calculate_rockhead',
    'calculate_q_value',
    'GeotechnicalCalculations'
]
