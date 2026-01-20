# AGS-Processor-st

A comprehensive Python tool for processing AGS3 and AGS4 geotechnical data files with a focus on data quality and consolidation.

## Features

- **Multi-Version Support**: Process both AGS3 and AGS4 format files
- **Batch Processing**: Handle multiple AGS files simultaneously
- **Data Validation**: Built-in quality checks and AGS format validation
- **Multiple Export Formats**: Export to Excel (multi-sheet) or CSV
- **Data Consolidation**: Merge data from multiple AGS files into a single output
- **Error Handling**: Skip invalid files and continue processing
- **Command-Line Interface**: Easy-to-use CLI for automation

## Installation

### From Source

```bash
git clone https://github.com/sabinasalakhova/AGS-Processor-st.git
cd AGS-Processor-st
pip install -e .
```

### Requirements

- Python >= 3.9
- python-ags4 >= 0.4.0
- pandas >= 1.3.0
- openpyxl >= 3.0.0
- xlsxwriter >= 3.0.0

## Quick Start

### Command Line Usage

#### Process a single AGS file

```bash
ags-processor input.ags -o output.xlsx
```

#### Process multiple AGS files

```bash
ags-processor file1.ags file2.ags file3.ags -o consolidated.xlsx
```

#### Validate an AGS file

```bash
ags-processor input.ags --validate-only
```

#### Export to CSV format

```bash
ags-processor input.ags -o output_dir -f csv
```

### Python API Usage

```python
from ags_processor import AGSProcessor, AGSValidator, AGSExporter

# Initialize components
processor = AGSProcessor()
validator = AGSValidator()
exporter = AGSExporter()

# Read AGS files
file_data = processor.read_file('input.ags')

# Or read multiple files
files = ['file1.ags', 'file2.ags', 'file3.ags']
all_data = processor.read_multiple_files(files)

# Get consolidated tables
tables = processor.get_all_tables()

# Validate a file
validation_result = validator.validate_file('input.ags')
if validation_result['valid']:
    print("File is valid!")
else:
    print("Errors:", validation_result['errors'])

# Export to Excel
exporter.export_to_excel(tables, 'output.xlsx')

# Get summary
summary = processor.get_file_summary()
print(f"Total tables: {summary['total_tables']}")
print(f"Table names: {summary['table_names']}")
```

## AGS Format Support

### Supported Versions

- **AGS3**: Legacy format support for existing projects
- **AGS4**: Current standard (AGS 4.0, 4.1, 4.2)

### Common AGS Groups Supported

- `PROJ` - Project information
- `LOCA` - Location details
- `GEOL` - Geological descriptions
- `SAMP` - Sample information
- `HOLE` - Borehole information (AGS3)
- And many more standard AGS groups

## Data Quality Features

### Validation Checks

- AGS format compliance
- Required field validation
- Data type checking
- Null value detection in key columns
- Cross-file consistency checks

### Error Handling

- Skip invalid files option
- Detailed error reporting
- Warning vs. error categorization
- Continue processing on non-critical errors

## Output Formats

### Excel Export

- Multi-sheet workbook (one sheet per AGS group)
- Optional summary sheet with table statistics
- Preserves data types and formatting

### CSV Export

- Separate CSV file for each AGS group
- Maintains original column structure
- Easy integration with other tools

## CLI Reference

```
usage: ags-processor [-h] [-o OUTPUT] [-f {excel,csv}] [--validate-only]
                      [--skip-invalid] [-v] [--no-summary]
                      files [files ...]

positional arguments:
  files                 AGS file(s) to process

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file path (Excel) or directory (CSV)
  -f {excel,csv}, --format {excel,csv}
                        Output format (default: excel)
  --validate-only       Only validate files without exporting
  --skip-invalid        Skip invalid files (default: True)
  -v, --verbose         Verbose output
  --no-summary          Do not include summary sheet in Excel export
```

## Examples

### Example 1: Basic Processing

```bash
# Process a single AGS file with verbose output
ags-processor borehole_data.ags -o output.xlsx -v
```

### Example 2: Batch Processing

```bash
# Process all AGS files in a directory
ags-processor data/*.ags -o consolidated_output.xlsx
```

### Example 3: Validation Only

```bash
# Validate files without exporting
ags-processor *.ags --validate-only -v
```

### Example 4: Python Script

```python
from ags_processor import AGSProcessor, AGSExporter

# Initialize
processor = AGSProcessor()

# Process multiple files
files = ['site1.ags', 'site2.ags', 'site3.ags']
processor.read_multiple_files(files, skip_invalid=True)

# Get summary
summary = processor.get_file_summary()
print(f"Processed {summary['total_files']} files")
print(f"Found {summary['total_tables']} unique table types")

# Export consolidated data
tables = processor.get_all_tables()
exporter = AGSExporter()
exporter.export_to_excel(tables, 'consolidated.xlsx')
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Acknowledgments

This project consolidates functionality from:
- sabinasalakhova/AGS-Processor
- sabinasalakhova/agsfileanalysis  
- sabinasalakhova/ags3_all_data_to_excel

Built with the excellent [python-ags4](https://pypi.org/project/python-AGS4/) library by the AGS Data Format Working Group.