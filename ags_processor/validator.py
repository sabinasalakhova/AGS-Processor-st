"""AGS data validator for quality checking."""

from typing import Dict, List, Optional
import pandas as pd
import logging

# Import our custom parser with padding fix instead of python_ags4
import sys
from pathlib import Path

# Add legacy directories to path to import custom parser
ags_processor_legacy = Path(__file__).parent.parent / "legacy" / "AGS-Processor"
if str(ags_processor_legacy) not in sys.path:
    sys.path.insert(0, str(ags_processor_legacy))

try:
    from ags_core import AGS4_to_dataframe
except ImportError:
    AGS4_to_dataframe = None

logger = logging.getLogger(__name__)


class AGSValidator:
    """
    Validator for AGS files with data quality checks.
    
    Provides validation for:
    - AGS format compliance
    - Data quality checks
    - Required fields
    - Data types
    """
    
    def __init__(self):
        """Initialize the validator."""
        self.validation_errors: List[Dict] = []
        self.validation_warnings: List[Dict] = []
        
    def validate_file(self, filepath: str) -> Dict:
        """
        Validate an AGS file using custom parser with padding fix.
        
        Args:
            filepath: Path to the AGS file
            
        Returns:
            Dictionary containing validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'filepath': filepath
        }
        
        if AGS4_to_dataframe is None:
            results['valid'] = False
            error_dict = {
                'type': 'DEPENDENCY_ERROR',
                'message': 'AGS parser not available'
            }
            results['errors'].append(error_dict)
            self.validation_errors.append(error_dict)
            return results
            
        try:
            # Use our custom parser with padding fix
            # This will pad mismatched rows instead of raising errors
            df_dict, headings = AGS4_to_dataframe(filepath)
            
            if not df_dict:
                results['valid'] = False
                error_dict = {
                    'type': 'PARSE_ERROR',
                    'message': 'Failed to parse AGS file - no data found'
                }
                results['errors'].append(error_dict)
                self.validation_errors.append(error_dict)
            else:
                # File parsed successfully
                # Add informational message about groups found
                warning_dict = {
                    'type': 'INFO',
                    'message': f'Successfully parsed {len(df_dict)} group(s): {", ".join(df_dict.keys())}'
                }
                results['warnings'].append(warning_dict)
                self.validation_warnings.append(warning_dict)
                
        except Exception as e:
            results['valid'] = False
            error_dict = {
                'type': 'VALIDATION_ERROR',
                'message': f'Validation failed: {str(e)}'
            }
            results['errors'].append(error_dict)
            self.validation_errors.append(error_dict)
            
        return results
        
    def validate_dataframe(self, df: pd.DataFrame, table_name: str) -> Dict:
        """
        Validate a DataFrame for data quality.
        
        Args:
            df: DataFrame to validate
            table_name: Name of the table
            
        Returns:
            Dictionary containing validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'table_name': table_name
        }
        
        # Check for empty DataFrame
        if df.empty:
            results['warnings'].append({
                'type': 'EMPTY_TABLE',
                'message': f'Table {table_name} is empty'
            })
            
        # Check for required columns based on table type
        required_columns = self._get_required_columns(table_name)
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            results['errors'].append({
                'type': 'MISSING_COLUMNS',
                'message': f'Missing required columns: {", ".join(missing_columns)}',
                'columns': missing_columns
            })
            results['valid'] = False
            
        # Check for null values in key columns
        key_columns = self._get_key_columns(table_name)
        for col in key_columns:
            if col in df.columns:
                null_count = df[col].isna().sum()
                if null_count > 0:
                    results['warnings'].append({
                        'type': 'NULL_VALUES',
                        'message': f'Column {col} has {null_count} null values',
                        'column': col,
                        'count': int(null_count)
                    })
                    
        return results
        
    def _get_required_columns(self, table_name: str) -> List[str]:
        """Get required columns for a table."""
        # Common required columns for different table types
        required_map = {
            'PROJ': ['PROJ_ID'],
            'LOCA': ['LOCA_ID'],
            'GEOL': ['LOCA_ID', 'GEOL_TOP'],
            'SAMP': ['LOCA_ID', 'SAMP_ID'],
            'HOLE': ['HOLE_ID'],  # AGS3
        }
        return required_map.get(table_name, [])
        
    def _get_key_columns(self, table_name: str) -> List[str]:
        """Get key columns that should not have null values."""
        # These are critical columns that should be populated
        key_map = {
            'PROJ': ['PROJ_ID', 'PROJ_NAME'],
            'LOCA': ['LOCA_ID', 'LOCA_TYPE'],
            'GEOL': ['LOCA_ID', 'GEOL_TOP', 'GEOL_BASE'],
            'SAMP': ['LOCA_ID', 'SAMP_ID', 'SAMP_TOP', 'SAMP_BASE'],
            'HOLE': ['HOLE_ID'],  # AGS3
        }
        return key_map.get(table_name, [])
        
    def get_summary(self) -> Dict:
        """Get validation summary."""
        return {
            'total_errors': len(self.validation_errors),
            'total_warnings': len(self.validation_warnings),
            'errors': self.validation_errors,
            'warnings': self.validation_warnings
        }
