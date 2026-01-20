"""Command-line interface for AGS Processor."""

import argparse
import os
import sys
from typing import List

from .processor import AGSProcessor
from .validator import AGSValidator
from .exporter import AGSExporter


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='AGS3/AGS4 Processor - Process and analyze geotechnical data files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single AGS file and export to Excel
  ags-processor input.ags -o output.xlsx
  
  # Process multiple AGS files
  ags-processor file1.ags file2.ags file3.ags -o consolidated.xlsx
  
  # Validate an AGS file
  ags-processor input.ags --validate-only
  
  # Process with verbose output
  ags-processor input.ags -o output.xlsx -v
        """
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        help='AGS file(s) to process'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (Excel) or directory (CSV)',
        default=None
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['excel', 'csv'],
        default='excel',
        help='Output format (default: excel)'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate files without exporting'
    )
    
    parser.add_argument(
        '--skip-invalid',
        action='store_true',
        default=True,
        help='Skip invalid files (default: True)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='Do not include summary sheet in Excel export'
    )
    
    args = parser.parse_args()
    
    # Validate input files
    for filepath in args.files:
        if not os.path.exists(filepath):
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
            
    # Initialize processor and validator
    processor = AGSProcessor()
    validator = AGSValidator()
    exporter = AGSExporter()
    
    if args.verbose:
        print(f"Processing {len(args.files)} file(s)...")
        
    # Validate files if requested
    if args.validate_only:
        validation_results = validate_files(args.files, validator, args.verbose)
        display_validation_results(validation_results, args.verbose)
        
        # Exit with error code if any files are invalid
        if not all(result['valid'] for result in validation_results):
            sys.exit(1)
        sys.exit(0)
        
    # Process files
    file_data = processor.read_multiple_files(args.files, skip_invalid=args.skip_invalid)
    
    if args.verbose:
        print(f"Successfully loaded {len(file_data)} file(s)")
        
    # Get file summary
    summary = processor.get_file_summary()
    
    if args.verbose:
        print(f"\nFile Summary:")
        print(f"  Total files: {summary['total_files']}")
        print(f"  Total tables: {summary['total_tables']}")
        print(f"  Files by version:")
        for version, count in summary['files_by_version'].items():
            print(f"    {version}: {count}")
            
    # Display errors
    errors = processor.get_errors()
    if errors:
        print(f"\nWarnings/Errors encountered:")
        for source, error_list in errors.items():
            print(f"  {source}:")
            for error in error_list:
                print(f"    - {error}")
                
    # Export if output path is provided
    if args.output:
        if args.verbose:
            print(f"\nExporting to {args.output}...")
            
        tables = processor.get_all_tables()
        
        if args.format == 'excel':
            success = exporter.export_to_excel(
                tables, 
                args.output,
                include_summary=not args.no_summary
            )
        else:  # csv
            success = exporter.export_to_csv(tables, args.output)
            
        if success:
            if args.verbose:
                print(f"Export successful: {args.output}")
        else:
            print(f"Export failed!", file=sys.stderr)
            for error in exporter.get_errors():
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)
    else:
        print("\nNo output path specified. Use -o/--output to export data.")
        print(f"Available tables: {', '.join(summary['table_names'])}")
        
    return 0


def validate_files(filepaths: List[str], validator: AGSValidator, verbose: bool = False) -> List[dict]:
    """Validate multiple AGS files."""
    results = []
    
    for filepath in filepaths:
        if verbose:
            print(f"\nValidating: {filepath}")
            
        result = validator.validate_file(filepath)
        results.append(result)
        
    return results


def display_validation_results(results: List[dict], verbose: bool = False):
    """Display validation results."""
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS")
    print("=" * 60)
    
    total_valid = sum(1 for r in results if r['valid'])
    total_invalid = len(results) - total_valid
    
    print(f"\nTotal files: {len(results)}")
    print(f"Valid: {total_valid}")
    print(f"Invalid: {total_invalid}")
    
    for result in results:
        print(f"\n{result['filepath']}")
        print(f"  Status: {'VALID' if result['valid'] else 'INVALID'}")
        
        if result['errors']:
            print(f"  Errors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"    - [{error['type']}] {error['message']}")
                
        if result['warnings'] and verbose:
            print(f"  Warnings ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"    - [{warning['type']}] {warning['message']}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    sys.exit(main())
