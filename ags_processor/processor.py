"""
AGS File Processing Module

Re-exports parsing functions from legacy files and provides AGSProcessor wrapper class.
- AGS4_to_dict, AGS4_to_dataframe from legacy/AGS-Processor/ags_core.py
- parse_ags_file from legacy/ags3_all_data_to_excel/ags_3_reader.py
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
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
# AGS PROCESSOR CLASS
# ============================================================================

class AGSProcessor:
    """
    Main AGS file processor class that provides a unified interface for
    parsing and managing AGS files.
    
    This class wraps the legacy parsing functions and provides a stateful
    interface for processing multiple files and tracking results.
    """
    
    def __init__(self):
        """Initialize the AGS processor."""
        self.tables = {}
        self.file_data = {}
        self.errors = {}
        self.processed_files = []
        
    def clear(self):
        """Clear all processed data."""
        self.tables = {}
        self.file_data = {}
        self.errors = {}
        self.processed_files = []
        
    def read_file(self, filepath: str, prefix_hole_id: bool = False) -> Dict[str, pd.DataFrame]:
        """
        Read a single AGS file using legacy parser.
        
        Parameters
        ----------
        filepath : str
            Path to the AGS file
        prefix_hole_id : bool, optional
            Whether to prefix HOLE_ID with first 5 chars of filename
            
        Returns
        -------
        dict
            Dictionary of group name -> DataFrame
        """
        try:
            # Read file as bytes for parse_ags_file
            with open(filepath, 'rb') as f:
                file_bytes = f.read()
            
            # Use the legacy parser
            groups = parse_ags_file(file_bytes)
            
            # Store the data
            filename = Path(filepath).name
            self.file_data[filename] = groups
            self.processed_files.append(filename)
            
            # Merge into tables
            for group_name, df in groups.items():
                if group_name in self.tables:
                    # Concatenate with existing data
                    self.tables[group_name] = pd.concat(
                        [self.tables[group_name], df],
                        ignore_index=True
                    )
                else:
                    self.tables[group_name] = df.copy()
                    
            return groups
            
        except Exception as e:
            self.errors[filepath] = [str(e)]
            logger.error(f"Error reading {filepath}: {e}")
            return {}
            
    def read_multiple_files(self, filepaths: List[str], skip_invalid: bool = True) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Read multiple AGS files.
        
        Parameters
        ----------
        filepaths : list of str
            List of paths to AGS files
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
                    results[Path(filepath).name] = groups
            except Exception as e:
                if not skip_invalid:
                    raise
                self.errors[filepath] = [str(e)]
                logger.warning(f"Skipped {filepath}: {e}")
                
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
        
        return {
            'total_files': len(self.processed_files),
            'total_groups': len(self.tables),
            'total_records': total_records,
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
