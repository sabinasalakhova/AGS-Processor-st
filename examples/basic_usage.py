"""
Example: Basic AGS file processing

This script demonstrates basic AGS file processing with validation and export.
"""

from ags_processor import AGSProcessor, AGSValidator, AGSExporter


def main():
    """Process a single AGS file with validation and export."""
    
    # File to process (replace with your file path)
    ags_file = 'your_file.ags'
    
    # Initialize components
    processor = AGSProcessor()
    validator = AGSValidator()
    exporter = AGSExporter()
    
    print("=" * 60)
    print("AGS File Processor Example")
    print("=" * 60)
    
    # Step 1: Validate the file
    print(f"\n1. Validating {ags_file}...")
    validation_result = validator.validate_file(ags_file)
    
    if validation_result['valid']:
        print("   ✓ File is valid")
    else:
        print("   ✗ File has errors:")
        for error in validation_result['errors']:
            print(f"     - {error['message']}")
        return
    
    # Show warnings if any
    if validation_result['warnings']:
        print(f"   ⚠ {len(validation_result['warnings'])} warning(s)")
        
    # Step 2: Read the file
    print(f"\n2. Reading {ags_file}...")
    file_data = processor.read_file(ags_file)
    
    if file_data is None:
        print("   ✗ Failed to read file")
        return
        
    print(f"   ✓ File loaded successfully")
    print(f"   Version: {file_data['version']}")
    
    # Step 3: Get file summary
    print("\n3. File Summary:")
    summary = processor.get_file_summary()
    print(f"   Tables found: {summary['total_tables']}")
    print(f"   Table names: {', '.join(summary['table_names'][:5])}...")
    
    # Step 4: Get tables
    print("\n4. Processing tables...")
    tables = processor.get_all_tables()
    
    for table_name, df in tables.items():
        print(f"   - {table_name}: {len(df)} rows, {len(df.columns)} columns")
        
    # Step 5: Export to Excel
    output_file = 'output.xlsx'
    print(f"\n5. Exporting to {output_file}...")
    success = exporter.export_to_excel(tables, output_file)
    
    if success:
        print(f"   ✓ Export successful")
    else:
        print(f"   ✗ Export failed")
        for error in exporter.get_errors():
            print(f"     - {error}")
            
    print("\n" + "=" * 60)
    print("Processing complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
