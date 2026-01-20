"""
AGS File Processing Module

Integrates AGS parsing from multiple legacy sources:
- AGS4_to_dict, AGS4_to_dataframe from AGS-Processor
- parse_ags_file from ags3_all_data_to_excel (primary parser)

This module provides comprehensive AGS file parsing for both AGS3 and AGS4 formats.
"""

import pandas as pd
import numpy as np
import csv
import re
import logging
from io import BytesIO, StringIO
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def is_file_like(obj):
    """
    Check if object is file like.
    
    Returns
    -------
    bool
        Return True if obj is file like, otherwise return False
    """
    if not (hasattr(obj, 'read') or hasattr(obj, 'write')):
        return False
    if not hasattr(obj, "__iter__"):
        return False
    return True


# ============================================================================
# PRIMARY PARSER - parse_ags_file (from ags3_all_data_to_excel)
# ============================================================================

def _split_quoted_csv(s: str) -> List[str]:
    """Splits a CSV string, respecting quoted fields"""
    return [p.strip().strip('"') for p in re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', s)]


def parse_ags_file(file_bytes: bytes) -> Dict[str, pd.DataFrame]:
    """
    Parse AGS file from bytes to dictionary of DataFrames.
    
    Primary parser supporting AGS3 and AGS4 formats with comprehensive
    handling of continuation lines, quoted fields, and group structures.
    
    Parameters
    ----------
    file_bytes : bytes
        Raw bytes of AGS file
    
    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary mapping group names to DataFrames
    """
    text = file_bytes.decode("latin-1", errors="ignore")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    group_data: Dict[str, List[Dict[str, str]]] = {}
    current_group: Optional[str] = None
    headings: List[str] = []
    is_header_continuation = False

    def _split_line(line: str) -> List[str]:
        """Split a CSV line, handling quoted fields."""
        parts = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', line)
        return [p.strip().strip('"') for p in parts]

    for line in lines:
        parts = _split_line(line)
        first_field = parts[0]
        
        # Start of a new GROUP (e.g., "**HOLE")
        if first_field.startswith("**"):
            current_group = first_field.strip("*?")
            group_data.setdefault(current_group, [])
            headings = []
            is_header_continuation = False
            continue

        if not current_group:
            continue

        # HEADING line (e.g., "*HOLE_ID") or continuation
        if first_field.startswith("*") or is_header_continuation:
            new_headings = [h.lstrip("*?") for h in parts]
            headings.extend(new_headings)
            continue

        # UNITS line - ignore for data parsing
        if first_field == "<UNITS>":
            continue

        # Data continuation line handling
        if first_field == "<CONT>":
            cont_values = parts[1:]  # skip <CONT>
            last_row = group_data[current_group][-1]

            filled_count = 1  # first column skipped in <CONT>
            while filled_count < len(headings) and headings[filled_count] in last_row:
                filled_count += 1

            for v in cont_values:
                if filled_count < len(headings):
                    last_row[headings[filled_count]] = v
                    filled_count += 1
                else:
                    break
            continue

        # Data Row
        if headings and parts:
            row_values = parts[:len(headings)]
            if len(row_values) < len(headings):
                row_values.extend([''] * (len(headings) - len(row_values)))
            
            row_dict = dict(zip(headings, row_values))
            group_data[current_group].append(row_dict)
    
    # Convert to DataFrames and replace empty values with "-"
    group_dfs = {}
    for g, rows in group_data.items():
        if not rows:
            continue
        df = pd.DataFrame(rows)
        df = df.replace(r'^\s*$', '-', regex=True).fillna('-')
        group_dfs[g] = df
    
    return group_dfs


# ============================================================================
# SECONDARY PARSERS - AGS4_to_dict and AGS4_to_dataframe
# ============================================================================

def AGS4_to_dict(filepath_or_buffer, encoding: str = 'utf-8'):
    """
    Load all the data in an AGS file to dictionaries.
    Preserves field order and includes empty fields (including trailing empties).

    Parameters
    ----------
    filepath_or_buffer : File path (str, pathlib.Path), or a file-like object.
        Path to AGS4/AGS3 file or any object with a read() method.
    encoding : str
        Character encoding (default: 'utf-8')

    Returns
    -------
    data : dict[str, dict[str, list[str]]]
        Python dictionary populated with data from the AGS file.
    headings : dict[str, list[str]]
        Dictionary with the headings in each GROUP.
    """
    close_file = False

    # Handle file-like inputs vs paths
    if is_file_like(filepath_or_buffer) or hasattr(filepath_or_buffer, 'read'):
        need_to_read = False
        if isinstance(filepath_or_buffer, BytesIO):
            need_to_read = True
        elif hasattr(filepath_or_buffer, 'mode') and 'b' in getattr(filepath_or_buffer, 'mode', ''):
            need_to_read = True
        elif not hasattr(filepath_or_buffer, 'mode'):
            need_to_read = True

        if need_to_read:
            if hasattr(filepath_or_buffer, 'seek'):
                filepath_or_buffer.seek(0)
            content = filepath_or_buffer.read()
            if isinstance(content, bytes):
                content = content.decode(encoding, errors="replace")
            if hasattr(filepath_or_buffer, 'seek'):
                filepath_or_buffer.seek(0)
            f = StringIO(content)
        else:
            f = filepath_or_buffer
    else:
        f = open(filepath_or_buffer, "r", encoding=encoding, errors="replace")
        close_file = True

    try:
        data: dict[str, dict[str, list[str]]] = {}
        headings: dict[str, list[str]] = {}
        group = None
        row = 0

        reader = csv.reader(f, delimiter=",", quotechar='"', skipinitialspace=False)
        for lineno, temp in enumerate(reader, start=1):
            # Skip completely empty lines
            if temp is None or len(temp) == 0:
                continue

            first = temp[0]

            # GROUP line (AGS4: "**", AGS3: "**")
            if first.startswith("**"):
                row = 0
                group = first[2:]
                data[group] = {}

            # HEADING line (starts with "*")
            elif first.startswith("*"):
                if group is None:
                    raise ValueError(f"Heading before GROUP at line {lineno}")
                row += 1
                cleaned_headings = [item[1:] for item in temp]

                if row == 1:
                    headings[group] = cleaned_headings
                else:
                    headings[group].extend(cleaned_headings)

                # Deduplicate headings by suffixing with _n
                seen = {}
                for idx, item in enumerate(headings[group]):
                    seen[item] = seen.get(item, -1) + 1
                    if seen[item]:
                        headings[group][idx] = f"{item}_{seen[item]}"

                for h in headings[group]:
                    data[group].setdefault(h, [])

            # Continuation line
            elif first == "<CONT>":
                if group is None:
                    raise ValueError(f"Continuation before GROUP at line {lineno}")
                for j in range(1, len(temp)):
                    if j >= len(headings[group]):
                        raise ValueError(f"Continuation column index {j} exceeds headings for group {group} at line {lineno}")
                    col = headings[group][j]
                    if not data[group][col]:
                        raise ValueError(f"No previous row for continuation in column '{col}' at line {lineno}")
                    data[group][col][-1] += temp[j]

            # Group breaks (blank line with one empty field)
            elif first == "" and len(temp) == 1:
                continue

            # DATA / UNITS lines
            else:
                if group is None:
                    raise ValueError(f"Data before GROUP at line {lineno}")
                for j in range(len(temp)):
                    col = headings[group][j]
                    data[group][col].append(temp[j])
    finally:
        if close_file:
            f.close()

    return data, headings


def AGS4_to_dataframe(filepath_or_buffer, encoding='utf-8'):
    """
    Load all the tables in a AGS4 file to Pandas dataframes.
    
    Parameters
    ----------
    filepath_or_buffer : str, file-like object
        Path to AGS4 file or any file like object
    encoding : str
        Character encoding (default: 'utf-8')
    
    Returns
    -------
    data : dict
        Dictionary of Pandas dataframes, one per AGS GROUP
    headings : dict
        Dictionary with the headings in each GROUP
    """
    # Extract AGS4 file into a dictionary of dictionaries
    data, headings = AGS4_to_dict(filepath_or_buffer, encoding=encoding)

    # Convert to dictionary of Pandas dataframes
    df = {}
    for key in data:
        try:
            table = pd.DataFrame(data[key])
            table[1:] = table[1:].apply(pd.to_numeric, errors='ignore')
            df[key] = table
        except ValueError:
            print(f'Warning: {key} is not exported')
            continue
    
   
    # Handle exceptions for group names
    rename_map = {
        "?ETH": "WETH",
        "?ETH_TOP": "WETH_TOP",
        "?ETH_BASE": "WETH_BASE",
        "?ETH_GRAD": "WETH_GRAD",
        "?LEGD": "LEGD",
        "?HORN": "HORN",
    }
    for old, new in rename_map.items():
        if old in df:
            df[new] = df.pop(old)
        if old in headings:
            headings[new] = headings.pop(old)
    
    return df, headings


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def find_hole_id_column(columns: List[str]) -> Optional[str]:
    """
    Identify HOLE_ID or common variants in a list of columns.
    
    Parameters
    ----------
    columns : List[str]
        List of column names
    
    Returns
    -------
    Optional[str]
        The identified HOLE_ID column name, or None
    """
    uc_map = {str(c).upper(): c for c in columns}
    
    candidates = [
        "HOLE_ID", "HOLEID", "HOLE", "LOCA_ID", "LOCATION_ID"
    ]
    
    for cand in candidates:
        if cand in uc_map:
            return uc_map[cand]
            
    return None


def process_files_to_combined_groups(input_dir: Path) -> Dict[str, pd.DataFrame]:
    """
    Process all .ags files in a directory, combine them by group.
    
    Parameters
    ----------
    input_dir : Path
        Directory containing AGS files
    
    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary of combined DataFrames by group
    """
    all_groups_data: Dict[str, List[pd.DataFrame]] = {}
    ags_files = sorted(list(input_dir.glob("*.ags")) + list(input_dir.glob("*.AGS")))

    if not ags_files:
        logger.warning(f"No .ags files found in {input_dir}")
        return {}

    logger.info(f"Found {len(ags_files)} AGS files to process.")

    for file_path in ags_files:
        logger.info(f"Processing file: {file_path.name}")
        try:
            file_bytes = file_path.read_bytes()
            groups = parse_ags_file(file_bytes)

            if not groups:
                logger.warning(f"No data groups parsed from {file_path.name}.")
                continue

            # Get prefix from filename (first 5 chars)
            filename_prefix = file_path.stem[:5]

            for group_name, df in groups.items():
                if df.empty:
                    continue
                
                df_copy = df.copy()
                
                # Add source file column
                df_copy["SOURCE_FILE"] = file_path.name

                # Find and prefix HOLE_ID
                hole_id_col = find_hole_id_column(df_copy.columns)
                if hole_id_col:
                    df_copy[hole_id_col] = df_copy[hole_id_col].astype(str).str.strip()
                    df_copy[hole_id_col] = f"{filename_prefix}_" + df_copy[hole_id_col]
                
                # Store the processed dataframe
                if group_name not in all_groups_data:
                    all_groups_data[group_name] = []
                all_groups_data[group_name].append(df_copy)

        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")

    # Combine all dataframes for each group
    logger.info("Combining data from all files...")
    combined_dfs: Dict[str, pd.DataFrame] = {}
    for group_name, df_list in all_groups_data.items():
        if df_list:
            try:
                combined_dfs[group_name] = pd.concat(df_list, ignore_index=True)
            except Exception as e:
                logger.error(f"Could not combine data for group '{group_name}': {e}")
    
    return combined_dfs


def write_groups_to_excel(groups: Dict[str, pd.DataFrame], output_path: Path):
    """
    Write a dictionary of DataFrames to a single Excel file with multiple sheets.
    
    Parameters
    ----------
    groups : Dict[str, pd.DataFrame]
        Dictionary of DataFrames by group name
    output_path : Path
        Path to output Excel file
    """
    if not groups:
        logger.warning("No data to write to Excel.")
        return
    
    logger.info(f"Writing combined data to {output_path}...")
    try:
        with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
            for group_name, df in sorted(groups.items()):
                if df is None or df.empty:
                    continue
                
                # Sanitize sheet name: remove invalid chars and limit to 31 chars
                sanitized_name = re.sub(r'[\\/*?:\[\]]', '_', group_name)
                sheet_name = sanitized_name[:31]
                
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        logger.info("Successfully created Excel file.")
    except Exception as e:
        logger.error(f"Failed to write Excel file: {e}")
