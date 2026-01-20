"""Core AGS file processor supporting AGS3 and AGS4 formats."""

import os
from typing import Dict, List, Optional, Tuple
import pandas as pd

try:
    from python_ags4 import AGS4
except ImportError:
    raise ImportError(
        "python-ags4 is required but not installed. "
        "Please install it with: pip install python-ags4"
    )


class AGSProcessor:
    """
    AGS file processor that handles both AGS3 and AGS4 formats.
    
    This class provides functionality to:
    - Read AGS files (both AGS3 and AGS4)
    - Validate data quality
    - Process multiple files
    - Extract and consolidate data
    """
    
    def __init__(self):
        """Initialize the AGS processor."""
        self.files_data: Dict[str, Dict] = {}
        self.errors: Dict[str, List] = {}
        
    def read_file(self, filepath: str, skip_invalid: bool = True) -> Optional[Dict]:
        """
        Read an AGS file and return its data.
        
        Args:
            filepath: Path to the AGS file
            skip_invalid: If True, skip files that fail validation
            
        Returns:
            Dictionary containing tables and headings, or None if invalid and skip_invalid is True
        """
        if not os.path.exists(filepath):
            error_msg = f"File not found: {filepath}"
            self._add_error(filepath, error_msg)
            return None
            
        try:
            # Detect AGS version
            version = self._detect_ags_version(filepath)
            
            # Read the AGS file
            tables, headings = AGS4.AGS4_to_dataframe(filepath)
            
            # Store file data
            file_data = {
                'filepath': filepath,
                'version': version,
                'tables': tables,
                'headings': headings,
                'filename': os.path.basename(filepath)
            }
            
            self.files_data[filepath] = file_data
            return file_data
            
        except Exception as e:
            error_msg = f"Error reading file: {str(e)}"
            self._add_error(filepath, error_msg)
            if skip_invalid:
                return None
            raise
            
    def read_multiple_files(self, filepaths: List[str], skip_invalid: bool = True) -> Dict[str, Dict]:
        """
        Read multiple AGS files.
        
        Args:
            filepaths: List of paths to AGS files
            skip_invalid: If True, skip files that fail validation
            
        Returns:
            Dictionary mapping filepaths to their data
        """
        results = {}
        for filepath in filepaths:
            data = self.read_file(filepath, skip_invalid=skip_invalid)
            if data is not None:
                results[filepath] = data
        return results
        
    def _detect_ags_version(self, filepath: str) -> str:
        """
        Detect the AGS version from the file.
        
        Args:
            filepath: Path to the AGS file
            
        Returns:
            Version string (e.g., "AGS3", "AGS4")
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                # Read first few lines
                for _ in range(20):
                    line = f.readline()
                    if not line:
                        break
                    # Look for TRAN group which contains version info
                    if line.startswith('"GROUP","TRAN"') or line.startswith('GROUP,TRAN'):
                        # Continue reading to find version
                        for _ in range(10):
                            line = f.readline()
                            if 'AGS4' in line or '4.' in line:
                                return "AGS4"
                            elif 'AGS3' in line or '3.' in line:
                                return "AGS3"
                                
            # Default to AGS4 if version not explicitly found
            return "AGS4"
        except Exception:
            return "Unknown"
            
    def get_all_tables(self) -> Dict[str, pd.DataFrame]:
        """
        Get all tables from all loaded files.
        
        Returns:
            Dictionary mapping table names to DataFrames
        """
        all_tables = {}
        for file_data in self.files_data.values():
            tables = file_data.get('tables', {})
            for table_name, table_df in tables.items():
                if table_name not in all_tables:
                    all_tables[table_name] = []
                all_tables[table_name].append(table_df)
                
        # Concatenate tables with the same name
        consolidated = {}
        for table_name, dfs in all_tables.items():
            if len(dfs) == 1:
                consolidated[table_name] = dfs[0]
            else:
                try:
                    consolidated[table_name] = pd.concat(dfs, ignore_index=True)
                except Exception as e:
                    # If concatenation fails, keep the first one
                    consolidated[table_name] = dfs[0]
                    self._add_error(f"table_{table_name}", f"Failed to concatenate tables: {str(e)}")
                    
        return consolidated
        
    def get_table_list(self) -> List[str]:
        """
        Get list of all unique table names across all files.
        
        Returns:
            List of table names
        """
        table_names = set()
        for file_data in self.files_data.values():
            tables = file_data.get('tables', {})
            table_names.update(tables.keys())
        return sorted(list(table_names))
        
    def get_file_summary(self) -> Dict:
        """
        Get summary information about loaded files.
        
        Returns:
            Dictionary containing summary statistics
        """
        summary = {
            'total_files': len(self.files_data),
            'total_errors': sum(len(errors) for errors in self.errors.values()),
            'files_by_version': {},
            'total_tables': len(self.get_table_list()),
            'table_names': self.get_table_list()
        }
        
        for file_data in self.files_data.values():
            version = file_data.get('version', 'Unknown')
            summary['files_by_version'][version] = summary['files_by_version'].get(version, 0) + 1
            
        return summary
        
    def _add_error(self, source: str, error: str):
        """Add an error message."""
        if source not in self.errors:
            self.errors[source] = []
        self.errors[source].append(error)
        
    def get_errors(self) -> Dict[str, List]:
        """Get all errors encountered during processing."""
        return self.errors
        
    def clear(self):
        """Clear all loaded data and errors."""
        self.files_data.clear()
        self.errors.clear()
