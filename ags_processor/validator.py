"""AGS data validator for quality checking."""

from typing import Dict, List, Optional
import pandas as pd

try:
    from python_ags4 import AGS4
except ImportError:
    AGS4 = None


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
        Validate an AGS file.
        
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
        
        if AGS4 is None:
            results['valid'] = False
            results['errors'].append({
                'type': 'DEPENDENCY_ERROR',
                'message': 'python-ags4 library not available'
            })
            return results
            
        try:
            # Use python-ags4 validation
            error_list = AGS4.check_file(filepath)
            
            if error_list:
                for error in error_list:
                    # Categorize errors and warnings
                    if 'error' in error.lower() or 'invalid' in error.lower():
                        results['errors'].append({
                            'type': 'FORMAT_ERROR',
                            'message': error
                        })
                        results['valid'] = False
                    else:
                        results['warnings'].append({
                            'type': 'FORMAT_WARNING',
                            'message': error
                        })
                        
        except Exception as e:
            results['valid'] = False
            results['errors'].append({
                'type': 'VALIDATION_ERROR',
                'message': f'Validation failed: {str(e)}'
            })
            
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
