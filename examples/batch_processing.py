"""
Example: Batch processing multiple AGS files

This script demonstrates how to process multiple AGS files and consolidate them
into a single Excel output.
"""

from ags_processor import AGSProcessor, AGSExporter
import glob


def main():
    """Process multiple AGS files and consolidate into one output."""
    
    # Find all AGS files in a directory (replace with your path)
    ags_files = glob.glob('data/*.ags')
    
    if not ags_files:
        print("No AGS files found in data/ directory")
        return
        
    print("=" * 60)
    print("Batch AGS File Processor")
    print("=" * 60)
    print(f"\nFound {len(ags_files)} AGS file(s)")
    
    # Initialize processor and exporter
    processor = AGSProcessor()
    exporter = AGSExporter()
    
    # Process all files
    print("\nProcessing files...")
    file_data = processor.read_multiple_files(ags_files, skip_invalid=True)
    
    print(f"Successfully loaded {len(file_data)} file(s)")
    
    # Show any errors
    errors = processor.get_errors()
    if errors:
        print("\nWarnings/Errors:")
        for source, error_list in errors.items():
            print(f"  {source}:")
            for error in error_list:
                print(f"    - {error}")
                
    # Get summary
    summary = processor.get_file_summary()
    print("\nSummary:")
    print(f"  Total files: {summary['total_files']}")
    print(f"  Total tables: {summary['total_tables']}")
    print(f"  Files by version:")
    for version, count in summary['files_by_version'].items():
        print(f"    {version}: {count}")
        
    # Get consolidated tables
    tables = processor.get_all_tables()
    
    print("\nConsolidated tables:")
    for table_name, df in tables.items():
        print(f"  {table_name}: {len(df)} total rows")
        
    # Export to Excel
    output_file = 'consolidated_output.xlsx'
    print(f"\nExporting to {output_file}...")
    
    success = exporter.export_to_excel(tables, output_file, include_summary=True)
    
    if success:
        print("✓ Export successful!")
        print(f"  Output: {output_file}")
    else:
        print("✗ Export failed")
        for error in exporter.get_errors():
            print(f"  - {error}")
            
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
