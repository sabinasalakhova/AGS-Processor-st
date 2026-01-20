"""AGS data exporter to various formats."""

import os
from typing import Dict, List, Optional
import pandas as pd


class AGSExporter:
    """
    Export AGS data to various formats.
    
    Supports:
    - Excel export (single or multi-sheet)
    - CSV export
    - Consolidated data from multiple AGS files
    """
    
    def __init__(self):
        """Initialize the exporter."""
        self.export_errors: List[str] = []
        
    def export_to_excel(
        self, 
        tables: Dict[str, pd.DataFrame], 
        output_path: str,
        include_summary: bool = True
    ) -> bool:
        """
        Export tables to Excel file.
        
        Args:
            tables: Dictionary mapping table names to DataFrames
            output_path: Path to output Excel file
            include_summary: If True, add a summary sheet
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Create Excel writer
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                
                # Add summary sheet if requested
                if include_summary:
                    summary_df = self._create_summary_sheet(tables)
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Write each table to a separate sheet
                for table_name, df in tables.items():
                    # Excel sheet names have a 31 character limit
                    sheet_name = table_name[:31] if len(table_name) > 31 else table_name
                    
                    try:
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                    except Exception as e:
                        self.export_errors.append(
                            f"Failed to export table {table_name}: {str(e)}"
                        )
                        
            return True
            
        except Exception as e:
            self.export_errors.append(f"Export to Excel failed: {str(e)}")
            return False
            
    def export_to_csv(
        self, 
        tables: Dict[str, pd.DataFrame], 
        output_dir: str,
        prefix: str = ""
    ) -> bool:
        """
        Export tables to separate CSV files.
        
        Args:
            tables: Dictionary mapping table names to DataFrames
            output_dir: Directory to save CSV files
            prefix: Optional prefix for filenames
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Export each table to CSV
            for table_name, df in tables.items():
                filename = f"{prefix}{table_name}.csv" if prefix else f"{table_name}.csv"
                filepath = os.path.join(output_dir, filename)
                
                try:
                    df.to_csv(filepath, index=False)
                except Exception as e:
                    self.export_errors.append(
                        f"Failed to export table {table_name} to CSV: {str(e)}"
                    )
                    
            return True
            
        except Exception as e:
            self.export_errors.append(f"Export to CSV failed: {str(e)}")
            return False
            
    def export_consolidated(
        self,
        tables: Dict[str, pd.DataFrame],
        output_path: str,
        format: str = 'excel'
    ) -> bool:
        """
        Export consolidated data from multiple files.
        
        Args:
            tables: Dictionary mapping table names to DataFrames
            output_path: Path to output file or directory
            format: Export format ('excel' or 'csv')
            
        Returns:
            True if successful, False otherwise
        """
        if format.lower() == 'excel':
            return self.export_to_excel(tables, output_path, include_summary=True)
        elif format.lower() == 'csv':
            return self.export_to_csv(tables, output_path)
        else:
            self.export_errors.append(f"Unsupported format: {format}")
            return False
            
    def _create_summary_sheet(self, tables: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        Create a summary sheet for the Excel export.
        
        Args:
            tables: Dictionary of DataFrames
            
        Returns:
            DataFrame containing summary information
        """
        summary_data = []
        
        for table_name, df in tables.items():
            summary_data.append({
                'Table Name': table_name,
                'Row Count': len(df),
                'Column Count': len(df.columns),
                'Columns': ', '.join(df.columns.tolist()[:5])  # First 5 columns
            })
            
        return pd.DataFrame(summary_data)
        
    def get_errors(self) -> List[str]:
        """Get export errors."""
        return self.export_errors
        
    def clear_errors(self):
        """Clear export errors."""
        self.export_errors.clear()
