# Legacy Function Files

This directory contains the **original, unmodified source files** from the three legacy repositories that were integrated into this project.

## Purpose

These files are preserved as reference material to:
1. Document the original implementations
2. Provide source attribution for integrated functions
3. Enable comparison between original and integrated code
4. Maintain version history and provenance

## Repository Sources

### AGS-Processor/
**Repository**: https://github.com/sabinasalakhova/AGS-Processor

**Files**:
- `ags_core.py` (989 lines) - Core AGS processing functions including:
  - AGS4_to_dict, AGS4_to_dataframe
  - search_keyword, search_depth, match_soil_types
  - concat_ags_files, combine_ags_data
  - calculate_rockhead, calculate_q_value, weth_grade_to_numeric
- `AGS_Excel.py` - AGS to Excel conversion utility
- `Combine_AGS.py` - AGS file combination script
- `Concat_AGS.py` - AGS file concatenation script
- `Info_Extract.py` - Information extraction utilities
- `Match_Soil.py` - Soil type matching script
- `Search_Depth.py` - Depth search script
- `Search_KeyWord.py` - Keyword search script
- `View_single_AGS.py` - Single AGS file viewer
- `streamlit_app.py` - Original Streamlit application
- `app.py` - Alternative Streamlit interface

### ags3_all_data_to_excel/
**Repository**: https://github.com/sabinasalakhova/ags3_all_data_to_excel

**Files**:
- `ags_3_reader.py` - AGS3 file parser with:
  - parse_ags_file() - PRIMARY AGS3 parser
  - Support for **GROUP, *HEADING, <UNITS>, <CONT> format
  - Quoted CSV field handling
  - HOLE_ID prefixing
  - Multi-file batch processing

### agsfileanalysis/
**Repository**: https://github.com/sabinasalakhova/agsfileanalysis

**Files**:
- `triaxial.py` - Triaxial test processing:
  - generate_triaxial_table()
  - generate_triaxial_with_lithology()
  - calculate_s_t_values()
  - remove_duplicate_tests()
- `cleaners.py` - Data cleaning utilities:
  - coalesce_columns()
  - to_numeric_safe()
  - drop_singleton_rows()
  - deduplicate_cell()
  - expand_rows()
- `agsparser.py` - AGS parsing utilities
- `excel_util.py` - Excel output utilities
- `charts.py` - Charting functions
- `MAINcode.py` - Main processing script
- `CodeMain.py` - Alternative main script

## Integration Status

All functions from these legacy files have been integrated into the modern `ags_processor/` package:

- **processor.py** - AGS parsing functions from ags_core.py and ags_3_reader.py
- **triaxial.py** - Triaxial processing from agsfileanalysis/triaxial.py
- **cleaners.py** - Data cleaning from agsfileanalysis/cleaners.py
- **search.py** - Search functions from ags_core.py
- **combiners.py** - File combination from ags_core.py
- **calculations.py** - Geotechnical calculations from ags_core.py

## Modifications

The integrated versions in `ags_processor/` include:
- Modernized pandas API (deprecated functions updated)
- Security improvements (bounds checking, input validation)
- Consistent error handling
- Comprehensive docstrings
- Type hints where appropriate
- Code review fixes

## License

These files retain their original licenses from their respective repositories. Please refer to each repository for license information.

## Attribution

Original authors and contributors:
- Sabina Salakhova (@sabinasalakhova)
- Contributors to AGS-Processor, ags3_all_data_to_excel, and agsfileanalysis repositories

## Usage

These files are for **reference only**. For active development, use the integrated versions in `ags_processor/`.

To use the legacy files directly (not recommended):
```python
import sys
sys.path.insert(0, 'legacy/AGS-Processor')
import ags_core

# Not recommended - use ags_processor package instead
```

For modern usage:
```python
from ags_processor import AGSProcessor, GeotechnicalCalculations
from ags_processor.triaxial import generate_triaxial_with_lithology
from ags_processor.search import search_keyword
```

---

**Last Updated**: 2026-01-20
**Integration Commit**: 5af43fb
