# AGS Processor - Comprehensive Implementation

This document describes the comprehensive AGS processor implementation integrating functions from multiple legacy repositories.

## Overview

The AGS Processor now includes five new modules that provide complete AGS file processing capabilities for both AGS3 and AGS4 formats:

1. **processor.py** - Core AGS file parsing
2. **triaxial.py** - Triaxial test data processing
3. **cleaners.py** - Data cleaning utilities
4. **search.py** - Search and query functions
5. **combiners.py** - File combination and rock engineering calculations

## Module Details

### 1. processor.py - Core AGS File Parsing

Primary module for parsing AGS files with support for both AGS3 and AGS4 formats.

**Main Functions:**

- `parse_ags_file(file_bytes)` - **Primary parser** from ags3_all_data_to_excel
  - Handles AGS3 and AGS4 formats
  - Supports continuation lines, quoted fields
  - Returns: `Dict[str, pd.DataFrame]` - Group name to DataFrame mapping

- `AGS4_to_dict(filepath_or_buffer, encoding='utf-8')` - Dictionary-based parser
  - Returns raw dictionary structure
  - Preserves field order and empty fields
  - Returns: `(data, headings)` tuple

- `AGS4_to_dataframe(filepath_or_buffer, encoding='utf-8')` - DataFrame parser
  - Converts AGS to pandas DataFrames
  - Handles special group name mappings (e.g., ?ETH -> WETH)
  - Returns: `(df_dict, headings)` tuple

**Helper Functions:**

- `find_hole_id_column(columns)` - Identify borehole ID column variants
- `process_files_to_combined_groups(input_dir)` - Batch process directory of AGS files
- `write_groups_to_excel(groups, output_path)` - Export to Excel with multiple sheets

**Usage Example:**

```python
from pathlib import Path
import ags_processor.processor as proc

# Parse AGS file (primary method)
file_bytes = Path('data.ags').read_bytes()
groups = proc.parse_ags_file(file_bytes)

# Access groups
hole_data = groups['HOLE']
samp_data = groups['SAMP']

# Process directory of files
combined = proc.process_files_to_combined_groups(Path('ags_files/'))
proc.write_groups_to_excel(combined, Path('output.xlsx'))
```

### 2. triaxial.py - Triaxial Test Processing

Comprehensive triaxial test data processing from legacy agsfileanalysis.

**Main Functions:**

- `generate_triaxial_table(groups)` - Build triaxial summary table
  - Merges SAMP, CLSS, TRIG, TREG, TRIX, TRET groups
  - Normalizes column names across AGS3/AGS4
  - Expands pipe-separated values
  - Returns: `pd.DataFrame` with triaxial summary

- `generate_triaxial_with_lithology(groups)` - Add lithology mapping
  - Maps lithology from GIU group based on depth ranges
  - Optimized for large datasets
  - Returns: `pd.DataFrame` with LITHOLOGY column

- `calculate_s_t_values(df)` - Calculate stress parameters
  - Computes total and effective principal stresses (σ1, σ3)
  - Calculates s (mean stress) and t (shear stress)
  - Prefers effective stresses when pore pressure available
  - Returns: `pd.DataFrame` with s, t, and validity flags

- `remove_duplicate_tests(df)` - Remove duplicate test entries
  - Deduplicates based on HOLE_ID, SPEC_DEPTH, CELL, DEVF, PWPF
  - Returns: `pd.DataFrame` with duplicates removed

**Usage Example:**

```python
import ags_processor.processor as proc
import ags_processor.triaxial as tri

# Parse AGS file
groups = proc.parse_ags_file(file_bytes)

# Generate triaxial summary
triaxial_summary = tri.generate_triaxial_table(groups)

# Add lithology
triaxial_with_litho = tri.generate_triaxial_with_lithology(groups)

# Calculate s-t values
st_values = tri.calculate_s_t_values(triaxial_summary)

# Remove duplicates
clean_data = tri.remove_duplicate_tests(st_values)
```

### 3. cleaners.py - Data Cleaning Utilities

Essential data cleaning functions for AGS processing.

**Functions:**

- `normalize_columns(df)` - Uppercase and strip column names
- `drop_singleton_rows(df)` - Remove rows with ≤1 non-null value
- `deduplicate_cell(cell)` - Remove duplicate pipe-separated values
- `expand_rows(df)` - Expand rows with pipe-separated values
- `combine_groups(all_group_dfs)` - Combine groups across files
- `coalesce_columns(df, candidates, new_name)` - Merge alternate column names
- `to_numeric_safe(df, cols)` - Safe numeric conversion

**Usage Example:**

```python
import ags_processor.cleaners as clean

# Normalize column names
df = clean.normalize_columns(df)

# Remove singleton rows
df = clean.drop_singleton_rows(df)

# Deduplicate cell values
cell = "clay | sand | clay"  # -> "clay | sand"
clean_cell = clean.deduplicate_cell(cell)

# Expand rows with pipe-separated values
expanded_df = clean.expand_rows(df)

# Coalesce alternate column names
clean.coalesce_columns(df, ['SPEC_DEPTH', 'SPEC_DPTH'], 'SPEC_DEPTH')

# Safe numeric conversion
clean.to_numeric_safe(df, ['DEPTH', 'RQD', 'TCR'])
```

### 4. search.py - Search and Query Functions

Functions for searching and querying geological data.

**Functions:**

- `search_keyword(df, keyword_list)` - Search GEOL_DESC and Details for keywords
  - Creates boolean columns for each keyword
  - Special handling for "no recovery"
  - Returns: `pd.DataFrame` with keyword columns

- `match_soil_types(df, soil_type_list, grain_size_list)` - Match soil classifications
  - Matches weathering grades (IV, V, VI)
  - Matches geological formations (TOPSOIL, MARINE DEPOSIT, ALLUVIUM, etc.)
  - Matches grain sizes (CLAY, SILT, SAND, GRAVEL, etc.)
  - Returns: `pd.DataFrame` with classification columns

- `search_depth(df_data, df_depth, is_single_depth=True)` - Extract data at depths
  - Single depth or depth range queries
  - Returns: `pd.DataFrame` with matched intervals

**Usage Example:**

```python
import ags_processor.search as search

# Search for keywords
keywords = ['granite', 'weathered', 'fractured']
df = search.search_keyword(df, keywords)

# Match soil types and grain sizes
soil_types = ['IV', 'V', 'VI (RESIDUAL SOIL)', 'FILL']
grain_sizes = ['CLAY', 'SILT', 'SAND', 'GRAVEL']
df = search.match_soil_types(df, soil_types, grain_sizes)

# Search at specific depth
depth_query = pd.DataFrame({
    'GIU_HOLE_ID': ['BH1', 'BH2'],
    'DEPTH': [5.0, 10.0]
})
result = search.search_depth(combined_data, depth_query, is_single_depth=True)
```

### 5. combiners.py - File Combination and Rock Engineering

Functions for combining AGS files and rock engineering calculations.

**Main Functions:**

- `concat_ags_files(uploaded_files, giu_number)` - Concatenate multiple AGS files
  - Assigns unique GIU_NO to each file
  - Creates GIU_HOLE_ID for tracking
  - Returns: `dict` of combined DataFrames by group

- `combine_ags_data(uploaded_excel_files, selected_groups=None)` - Combine Excel files
  - Merges HOLE, CORE, DETL, WETH, FRAC, GEOL groups
  - Creates unified depth intervals
  - Returns: `pd.DataFrame` with combined data

**Rock Engineering Functions:**

- `weth_grade_to_numeric(df)` - Convert weathering grades to numeric (I=1, II=2, etc.)
- `rock_material_criteria(df, include_weak_zones=False)` - Determine rock material
- `calculate_rockhead(df, core_run=1.0, tcr_threshold=85, continuous_length=5, include_weak=False)` - Calculate rockhead depth
- `calculate_q_value(df, rqd_col='RQD', jn=9, jr=1, ja=1, jw=1, srf=1)` - Calculate Q-value for rock mass classification

**Usage Example:**

```python
import ags_processor.combiners as comb

# Concatenate AGS files
combined = comb.concat_ags_files(uploaded_files, giu_number='GIU001')

# Combine Excel files
unified_data = comb.combine_ags_data(excel_files, selected_groups=['CORE', 'GEOL', 'WETH'])

# Rock engineering calculations
df = comb.weth_grade_to_numeric(df)
df = comb.rock_material_criteria(df, include_weak_zones=False)

# Calculate rockhead
rockhead_result = comb.calculate_rockhead(
    df, 
    tcr_threshold=85, 
    continuous_length=5.0
)
print(rockhead_result['summary'])

# Calculate Q-value
df = comb.calculate_q_value(df, rqd_col='RQD', jn=9, jr=1, ja=1, jw=1, srf=1)
```

## Legacy Integration

This implementation integrates functions from three legacy repositories:

1. **AGS-Processor** (`/tmp/ags_core_full.py`)
   - `AGS4_to_dict`, `AGS4_to_dataframe`
   - `concat_ags_files`, `combine_ags_data`
   - `search_keyword`, `match_soil_types`, `search_depth`
   - Rock engineering functions

2. **ags3_all_data_to_excel** (`/tmp/ags3_all_data_to_excel/ags_3_reader.py`)
   - `parse_ags_file` - **Primary parser** (handles AGS3 & AGS4)

3. **agsfileanalysis** (`/tmp/triaxial_full.py`, `/tmp/cleaners_full.py`)
   - Triaxial processing functions
   - Data cleaning utilities

## Backward Compatibility

All legacy functions are preserved with their original signatures to ensure backward compatibility. The `parse_ags_file` function is designated as the primary parser while `AGS4_to_dict` and `AGS4_to_dataframe` remain available as alternatives.

## Testing

All modules have been tested with real AGS files:
- ✅ AGS3 and AGS4 parsing
- ✅ Triaxial table generation
- ✅ Data cleaning functions
- ✅ Search and query operations
- ✅ Rock engineering calculations

## Installation

Required dependencies:
```bash
pip install pandas numpy xlsxwriter
```

## Import Examples

```python
# Import specific modules
import ags_processor.processor as proc
import ags_processor.triaxial as tri
import ags_processor.cleaners as clean
import ags_processor.search as search
import ags_processor.combiners as comb

# Or import from main package
from ags_processor import processor, triaxial, cleaners, search, combiners
```
