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

    def export_multiple_to_excel(
        self,
        file_paths: List[str],
        giu_numbers: List[str],
        output_path: str,
        ignore_hole_types: Optional[List[str]] = None
    ) -> bool:
        """
        Export multiple AGS files to single consolidated Excel file with GIU numbering.
        
        This implements the legacy Concat_AGS.py functionality from AGS-Processor.
        
        Args:
            file_paths: List of AGS file paths to consolidate
            giu_numbers: List of unique GIU numbers for each file (for tracking)
            output_path: Path to output Excel file
            ignore_hole_types: Optional list of hole types to ignore (e.g., ['CP', 'TP', 'RC'])
            
        Returns:
            True if successful, False otherwise
            
        Example:
            exporter = AGSExporter()
            success = exporter.export_multiple_to_excel(
                ['site1.ags', 'site2.ags', 'site3.ags'],
                ['001', '002', '003'],
                'consolidated.xlsx',
                ignore_hole_types=['CP', 'TP']
            )
        """
        try:
            import sys
            from pathlib import Path
            
            # Add legacy directory to path
            ags_processor_legacy = Path(__file__).parent.parent / "legacy" / "AGS-Processor"
            if str(ags_processor_legacy) not in sys.path:
                sys.path.insert(0, str(ags_processor_legacy))
            
            from ags_core import AGS4_to_dataframe
            
            if len(file_paths) != len(giu_numbers):
                raise ValueError("file_paths and giu_numbers must have same length")
            
            # Initialize containers for consolidated data
            concat_df = {}
            concat_headings = {}
            
            # Define groups to include (based on legacy Concat_AGS)
            group_list = ['PROJ', 'HOLE', 'CORE', 'DETL', 'WETH', 'FRAC', 'GEOL', 
                         'SAMP', 'CLSS', 'DISC', 'LOCA', 'TRIG', 'TREG', 'TRIX', 'TRET']
            
            for i, (file_path, giu_no) in enumerate(zip(file_paths, giu_numbers)):
                try:
                    # Read AGS file using legacy parser
                    df, headings = AGS4_to_dataframe(file_path)
                    
                    # Handle exceptions from legacy code
                    for d in list(df):
                        # Remove <UNITS> row if present
                        if len(df[d]) > 0 and df[d].iloc[0, 0] in ["<UNIT>", "<UNITS>"]:
                            df[d] = df[d].drop([0])
                            
                        # Clean column names with '?'
                        df[d].columns = [c.split("?")[-1] if "?" in c else c for c in df[d].columns]
                        
                        # Handle special group names
                        if d == "?ETH":
                            df["WETH"] = df.pop("?ETH")
                            headings["WETH"] = headings.pop("?ETH")
                        elif d == "?LEGD":
                            df["LEGD"] = df.pop("?LEGD")
                            headings["LEGD"] = headings.pop("?LEGD")
                        elif d == "?HORN":
                            df["HORN"] = df.pop("?HORN")
                            headings["HORN"] = headings.pop("?HORN")
                    
                    # Create empty DataFrames for missing groups
                    for group in group_list:
                        if group not in df.keys():
                            headings[group] = pd.DataFrame()
                            df[group] = pd.DataFrame({"HOLE_ID": []})
                    
                    # Filter out ignored hole types if specified
                    if ignore_hole_types and 'HOLE' in df and 'HOLE_TYPE' in df['HOLE'].columns:
                        if "Any hole type that contains 'RC'" in ignore_hole_types:
                            ignore_holes = df['HOLE'].loc[
                                (df['HOLE']['HOLE_TYPE'].isin(ignore_hole_types)) |
                                (df['HOLE']['HOLE_TYPE'].str.contains("RC", na=False))
                            ].HOLE_ID
                        else:
                            ignore_holes = df['HOLE'].loc[
                                df['HOLE']['HOLE_TYPE'].isin(ignore_hole_types)
                            ].HOLE_ID
                        
                        # Remove ignored holes from all groups
                        for d in list(df):
                            if 'HOLE_ID' in df[d].columns:
                                df[d] = df[d].loc[~(df[d]['HOLE_ID'].isin(ignore_holes)), :]
                    
                    # Add GIU_NO column to all groups
                    for d in list(df):
                        df[d].insert(loc=0, column='GIU_NO', value=giu_no)
                    
                    # Add AGS_FILE column to PROJ group
                    if 'PROJ' in df:
                        df['PROJ'].insert(loc=0, column='AGS_FILE', value=os.path.basename(file_path))
                    
                    # Consolidate with existing data
                    if i == 0:
                        concat_df = df
                        concat_headings = headings
                    else:
                        for d in list(df):
                            if d in concat_df:
                                concat_df[d] = pd.concat([concat_df[d], df[d]], ignore_index=True)
                            else:
                                concat_df[d] = df[d]
                                
                except Exception as e:
                    self.export_errors.append(f"Failed to process {file_path}: {str(e)}")
                    continue
            
            # Write to Excel
            if concat_df:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    for key in list(concat_df):
                        try:
                            # Sanitize sheet name (Excel limit: 31 chars, no special chars)
                            new_key = key
                            if '?' in key:
                                new_key = new_key.replace('?', '_')
                            sheet_name = new_key[:31] if len(new_key) > 31 else new_key
                            
                            concat_df[key].to_excel(writer, sheet_name=sheet_name, index=False)
                        except ValueError as e:
                            self.export_errors.append(f'Failed to export group {key}: {str(e)}')
                
                return True
            else:
                self.export_errors.append("No data to export")
                return False
                
        except Exception as e:
            self.export_errors.append(f"Export multiple files failed: {str(e)}")
            return False

