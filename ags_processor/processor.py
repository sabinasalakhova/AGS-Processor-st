"""
AGS File Processing Module

Re-exports parsing functions from legacy files and provides AGSProcessor wrapper class.
- AGS4_to_dict, AGS4_to_dataframe from legacy/AGS-Processor/ags_core.py
- parse_ags_file from legacy/ags3_all_data_to_excel/ags_3_reader.py
"""

import sys
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from io import StringIO
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Add legacy directories to path
ags_processor_legacy = Path(__file__).parent.parent / "legacy" / "AGS-Processor"
ags3_reader_legacy = Path(__file__).parent.parent / "legacy" / "ags3_all_data_to_excel"

if str(ags_processor_legacy) not in sys.path:
    sys.path.insert(0, str(ags_processor_legacy))
if str(ags3_reader_legacy) not in sys.path:
    sys.path.insert(0, str(ags3_reader_legacy))

# Import from legacy files
try:
    from ags_core import AGS4_to_dict, AGS4_to_dataframe, is_file_like
except ImportError as e:
    print(f"Warning: Could not import from legacy ags_core: {e}")
    def AGS4_to_dict(*args, **kwargs):
        raise NotImplementedError("Legacy ags_core module not found")
    def AGS4_to_dataframe(*args, **kwargs):
        raise NotImplementedError("Legacy ags_core module not found")
    def is_file_like(*args, **kwargs):
        return False

try:
    from ags_3_reader import parse_ags_file, find_hole_id_column
except ImportError as e:
    print(f"Warning: Could not import from legacy ags_3_reader: {e}")
    def parse_ags_file(*args, **kwargs):
        raise NotImplementedError("Legacy ags_3_reader module not found")
    def find_hole_id_column(*args, **kwargs):
        return None


# ============================================================================
# AGS PROCESSOR CLASS - Thin wrapper using legacy functions directly
# ============================================================================

class AGSProcessor:
    """
    Main AGS file processor class that provides a unified interface for
    parsing and managing AGS files using legacy parsing functions.
    
    Uses legacy functions directly:
    - parse_ags_file() from ags_3_reader.py for AGS3 files
    - AGS4_to_dataframe() from ags_core.py for AGS4 files
    """
    
    def __init__(self):
        """Initialize the AGS processor."""
        self.tables = {}
        self.file_data = {}
        self.errors = {}
        self.processed_files = []
        self.file_versions = {}  # Track AGS version for each file
        self.skip_mismatched_rows = False  # Default: pad rows instead of skipping
        
    def clear(self):
        """Clear all processed data."""
        self.tables = {}
        self.file_data = {}
        self.errors = {}
        self.processed_files = []
        
    def read_file(self, filepath, prefix_hole_id: bool = False, skip_mismatched_rows: bool = None) -> Dict[str, pd.DataFrame]:
        """
        Read a single AGS file using legacy parsers with enhanced validation.
        
        Parameters
        ----------
        filepath : str or file-like
            Path to the AGS file or file-like object
        prefix_hole_id : bool, optional
            Whether to prefix HOLE_ID with first 5 chars of filename
        skip_mismatched_rows : bool, optional
            If True, skip rows with mismatched column counts (default: True)
            
        Returns
        -------
        dict
            Dictionary of group name -> DataFrame
        """
        if skip_mismatched_rows is not None:
            self.skip_mismatched_rows = skip_mismatched_rows
        try:
            filename = Path(filepath).name if hasattr(filepath, '__fspath__') or isinstance(filepath, str) else 'uploaded_file'
            file_warnings = []
            
            # Detect AGS version first
            ags_version = self._detect_ags_version(filepath)
            
            # Use appropriate parser based on version
            if ags_version == 'AGS3':
                # Use parse_ags_file for AGS3
                try:
                    if isinstance(filepath, (str, Path)):
                        with open(filepath, 'rb') as f:
                            file_bytes = f.read()
                    elif hasattr(filepath, 'read'):
                        file_bytes = filepath.read()
                        if isinstance(file_bytes, str):
                            file_bytes = file_bytes.encode('utf-8')
                    else:
                        raise ValueError(f"Invalid filepath type: {type(filepath)}")
                    
                    groups, parse_warnings = self._parse_ags3_with_validation(file_bytes, filename)
                    file_warnings.extend(parse_warnings)
                except Exception as e:
                    raise Exception(f"AGS3 parser failed: {e}")
            else:
                # Use AGS4_to_dataframe for AGS4
                try:
                    groups, parse_warnings = self._parse_with_validation(filepath, filename)
                    file_warnings.extend(parse_warnings)
                except Exception as e:
                    raise Exception(f"AGS4 parser failed: {e}")
            
            # Store warnings if any
            if file_warnings:
                if filename not in self.errors:
                    self.errors[filename] = []
                self.errors[filename].extend(file_warnings)
            
            # Store the data
            self.file_data[filename] = groups
            if filename not in self.processed_files:
                self.processed_files.append(filename)
            
            # Merge into consolidated tables
            for group_name, df in groups.items():
                if group_name in self.tables:
                    # Concatenate with existing data
                    self.tables[group_name] = pd.concat(
                        [self.tables[group_name], df],
                        ignore_index=True
                    )
                else:
                    self.tables[group_name] = df.copy()
                    
            # Store version info
            if not hasattr(self, 'file_versions'):
                self.file_versions = {}
            self.file_versions[filename] = ags_version
            
            return groups
            
        except Exception as e:
            filepath_str = str(filepath) if isinstance(filepath, (str, Path)) else 'file'
            self.errors[filepath_str] = [str(e)]
            logger.error(f"Error reading {filepath_str}: {e}")
            return {}
    
    def _parse_with_validation(self, filepath, parser_name='AGS4_to_dataframe'):
        """
        Parse AGS file and validate row/heading consistency.
        
        Returns
        -------
        tuple
            (groups dict, warnings list)
        """
        import csv
        from io import StringIO
        
        warnings = []
        
        # First, do a validation pass to detect mismatches
        if isinstance(filepath, (str, Path)):
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        elif hasattr(filepath, 'read'):
            if hasattr(filepath, 'seek'):
                filepath.seek(0)
            content = filepath.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            if hasattr(filepath, 'seek'):
                filepath.seek(0)
        else:
            content = str(filepath)
        
        # Parse and validate
        reader = csv.reader(StringIO(content), delimiter=',', quotechar='"')
        current_group = None
        headings = []
        line_num = 0
        
        for row in reader:
            line_num += 1
            if not row or len(row) == 0:
                continue
            
            first = row[0]
            
            if first.startswith('**'):
                current_group = first[2:]
                headings = []
            elif first.startswith('*'):
                # Heading row
                headings.extend([h[1:] for h in row])
            elif first == '<CONT>':
                # Continuation line
                continue
            elif current_group and headings:
                # Data row - check length
                if len(row) != len(headings):
                    warning_msg = (
                        f"WARNING: Line {line_num} in group {current_group}: "
                        f"Row has {len(row)} items but {len(headings)} headings expected. "
                        f"Row data: {row[:min(5, len(row))]}..."
                    )
                    if self.skip_mismatched_rows:
                        warning_msg += " - SKIPPED"
                    warnings.append(warning_msg)
        
        # Now call the actual parser
        try:
            df_dict, headings_dict = AGS4_to_dataframe(filepath)
        except Exception as e:
            # If parser fails, add error to warnings
            error_msg = str(e)
            if "does not have the same number of entries" in error_msg:
                # Extract line number and group from error message
                warnings.append(f"PARSER ERROR: {error_msg}")
            else:
                warnings.append(f"ERROR: Failed to parse file - {error_msg}")
            # Return empty dict if parsing fails
            df_dict = {}
        
        return df_dict, warnings
    
    def _parse_ags3_with_validation(self, file_bytes, filename):
        """
        Parse AGS3 file with row padding and unit row skipping.
        
        Skips <UNITS> rows and pads data rows to match heading count.
        
        Returns
        -------
        tuple
            (groups dict, warnings list)
        """
        warnings = []
        text = file_bytes.decode("latin-1", errors="ignore")
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        
        current_group = None
        headings = []
        groups = {}
        line_num = 0
        group_data = []
        
        import re
        def _split_line(line: str):
            parts = re.split(r',(?=(?:[^"]*"[^"]*")*[^"]*$)', line)
            return [p.strip().strip('"') for p in parts]
        
        for line in lines:
            line_num += 1
            parts = _split_line(line)
            first_field = parts[0]
            
            if first_field.startswith("**"):
                current_group = first_field.strip("*?")
                headings = []
            elif first_field.startswith("*"):
                new_headings = [h.lstrip("*?") for h in parts]
                headings.extend(new_headings)
            elif first_field == "<UNITS>" or first_field == "<CONT>":
                continue
            elif current_group and headings and parts:
                # Data row - check length
                if len(parts) != len(headings):
                    warnings.append(
                        f"WARNING: Line {line_num} in group {current_group}: "
                        f"Row has {len(parts)} items but {len(headings)} headings expected. "
                        f"Row data: {parts[:min(5, len(parts))]}..."
                    )
        
        # Now call the actual parser
        groups = parse_ags_file(file_bytes)
        
        return groups, warnings
            
    def read_multiple_files(self, filepaths: List, skip_invalid: bool = True) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Read multiple AGS files.
        
        Parameters
        ----------
        filepaths : list
            List of file paths or file-like objects
        skip_invalid : bool, optional
            Whether to skip files that fail to parse
            
        Returns
        -------
        dict
            Dictionary of filename -> {group_name -> DataFrame}
        """
        results = {}
        
        for filepath in filepaths:
            try:
                groups = self.read_file(filepath)
                if groups:
                    filename = Path(filepath).name if isinstance(filepath, (str, Path)) else 'uploaded_file'
                    results[filename] = groups
            except Exception as e:
                if not skip_invalid:
                    raise
                filepath_str = str(filepath) if isinstance(filepath, (str, Path)) else 'file'
                self.errors[filepath_str] = [str(e)]
                logger.warning(f"Skipped {filepath_str}: {e}")
                
        return results
        
    def get_all_tables(self) -> Dict[str, pd.DataFrame]:
        """
        Get all consolidated tables.
        
        Returns
        -------
        dict
            Dictionary of group name -> consolidated DataFrame
        """
        return self.tables
        
    def get_table(self, group_name: str) -> Optional[pd.DataFrame]:
        """
        Get a specific table by group name.
        
        Parameters
        ----------
        group_name : str
            Name of the AGS group (e.g., 'PROJ', 'LOCA', 'SAMP')
            
        Returns
        -------
        DataFrame or None
            The requested table, or None if not found
        """
        return self.tables.get(group_name)
        
    def get_file_summary(self) -> Dict:
        """
        Get summary statistics about processed files.
        
        Returns
        -------
        dict
            Summary information including total files, groups, records
        """
        total_records = sum(len(df) for df in self.tables.values())
        total_errors = sum(len(msgs) for msgs in self.errors.values())
        
        # Count files by version (basic detection)
        files_by_version = {}
        for filename in self.processed_files:
            # This is a simple heuristic - could be improved
            files_by_version['AGS4'] = files_by_version.get('AGS4', 0) + 1
        
        return {
            'total_files': len(self.processed_files),
            'total_tables': len(self.tables),  # Use 'total_tables' instead of 'total_groups'
            'total_groups': len(self.tables),  # Keep for backwards compatibility
            'total_records': total_records,
            'total_errors': total_errors,
            'files_by_version': files_by_version,
            'group_names': list(self.tables.keys()),
            'files': self.processed_files
        }
        
    def get_errors(self) -> Dict[str, List[str]]:
        """
        Get any errors that occurred during processing.
        
        Returns
        -------
        dict
            Dictionary of filepath -> list of error messages
        """
        return self.errors
        
    def get_group_names(self) -> List[str]:
        """
        Get list of all group names in processed data.
        
        Returns
        -------
        list
            List of group names
        """
        return list(self.tables.keys())


__all__ = [
    'AGSProcessor',
    'AGS4_to_dict',
    'AGS4_to_dataframe',
    'parse_ags_file',
    'find_hole_id_column',
    'is_file_like'
]
