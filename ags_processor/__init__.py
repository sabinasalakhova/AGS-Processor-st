"""AGS Processor - A tool for processing AGS3 and AGS4 geotechnical data files."""

__version__ = "0.1.0"

# Import functions from legacy AGS-Processor ags_core.py
import sys
from pathlib import Path

# Add legacy directory to path
legacy_path = Path(__file__).parent.parent / "legacy" / "AGS-Processor"
if str(legacy_path) not in sys.path:
    sys.path.insert(0, str(legacy_path))

# Import from legacy ags_core module
try:
    from ags_core import (
        AGS4_to_dict,
        AGS4_to_dataframe,
        concat_ags_files,
        combine_ags_data,
        search_keyword,
        match_soil_types,
        search_depth,
        calculate_rockhead,
        calculate_q_value,
        weth_grade_to_numeric,
        rock_material_criteria
    )
except ImportError as e:
    print(f"Warning: Could not import from legacy ags_core: {e}")
    # Fallback to local implementations
    from .processor import AGS4_to_dict, AGS4_to_dataframe
    from .search import search_keyword, match_soil_types, search_depth
    from .combiners import concat_ags_files, combine_ags_data
    from .calculations import calculate_rockhead, calculate_q_value, weth_grade_to_numeric, rock_material_criteria

# Import AGSProcessor class wrapper
from .processor import AGSProcessor

# Import other modules
from .validator import AGSValidator
from .exporter import AGSExporter
from .calculations import GeotechnicalCalculations

# Import comprehensive modules
from . import processor
from . import triaxial
from . import cleaners
from . import search
from . import combiners

__all__ = [
    # Core class
    "AGSProcessor",
    # Legacy functions from ags_core
    "AGS4_to_dict",
    "AGS4_to_dataframe",
    "concat_ags_files",
    "combine_ags_data",
    "search_keyword",
    "match_soil_types",
    "search_depth",
    "calculate_rockhead",
    "calculate_q_value",
    "weth_grade_to_numeric",
    "rock_material_criteria",
    # Other classes
    "AGSValidator", 
    "AGSExporter", 
    "GeotechnicalCalculations",
    # Modules
    "processor",
    "triaxial",
    "cleaners",
    "search",
    "combiners"
]
