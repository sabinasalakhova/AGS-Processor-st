"""AGS Processor - A tool for processing AGS3 and AGS4 geotechnical data files."""

__version__ = "0.1.0"

# Import functions from legacy AGS-Processor ags_core.py
import sys
from pathlib import Path

# Add legacy directories to path
ags_processor_legacy = Path(__file__).parent.parent / "legacy" / "AGS-Processor"
ags3_reader_legacy = Path(__file__).parent.parent / "legacy" / "ags3_all_data_to_excel"

if str(ags_processor_legacy) not in sys.path:
    sys.path.insert(0, str(ags_processor_legacy))
if str(ags3_reader_legacy) not in sys.path:
    sys.path.insert(0, str(ags3_reader_legacy))

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
        rock_material_criteria,
        is_file_like
    )
except ImportError as e:
    print(f"Warning: Could not import from legacy ags_core: {e}")
    # Fallback to local implementations
    from .processor import AGS4_to_dict, AGS4_to_dataframe, is_file_like
    from .search import search_keyword, match_soil_types, search_depth
    from .combiners import concat_ags_files, combine_ags_data
    from .calculations import calculate_rockhead, calculate_q_value, weth_grade_to_numeric, rock_material_criteria

# Import from legacy ags_3_reader module
try:
    from ags_3_reader import parse_ags_file, find_hole_id_column
except ImportError as e:
    print(f"Warning: Could not import from legacy ags_3_reader: {e}")
    from .processor import parse_ags_file, find_hole_id_column

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
    "is_file_like",
    # Legacy functions from ags_3_reader
    "parse_ags_file",
    "find_hole_id_column",
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
