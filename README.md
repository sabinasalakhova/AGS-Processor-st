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
- **Web Interface**: Streamlit-based UI for interactive processing
- **Geotechnical Calculations**: 
  - Rockhead detection (soil-rock interface)
  - Corestone identification  
  - Q-value calculation (NGI rock mass classification)
- **Example Files**: Sample AGS files included for testing

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
- streamlit >= 1.28.0 (for web UI)

## Quick Start

### Web Interface (Streamlit)

Launch the interactive web application:

```bash
streamlit run app.py
```

The app will open in your browser with features for:
- File upload and processing
- Real-time validation
- Interactive data exploration
- One-click export to Excel/CSV

See [STREAMLIT_README.md](STREAMLIT_README.md) for detailed UI documentation.

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
from ags_processor import AGSProcessor, AGSValidator, AGSExporter, GeotechnicalCalculations

# Initialize components
processor = AGSProcessor()
validator = AGSValidator()
exporter = AGSExporter()
calc = GeotechnicalCalculations()

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

# Geotechnical calculations
if 'GEOL' in tables:
    # Detect rockhead
    rockhead_depths = calc.detect_rockhead(tables['GEOL'])
    print(f"Rockhead depths: {rockhead_depths}")
    
    # Identify corestones
    corestones = calc.detect_corestones(tables['GEOL'], min_thickness=0.5)
    print(f"Found {len(corestones)} corestones")
    
# Calculate Q-value
q_value = calc.calculate_q_value(rqd=90, jn=3, jr=3, ja=1, jw=1, srf=1)
quality = calc.interpret_q_value(q_value)
print(f"Q-value: {q_value:.2f} ({quality})")

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

### Example 1: Process Sample File

```bash
# Try with the included sample file
ags-processor data/examples/sample_borehole.ags -o output.xlsx -v
```

### Example 2: Basic Processing

```bash
# Process a single AGS file with verbose output
ags-processor borehole_data.ags -o output.xlsx -v
```

### Example 3: Batch Processing

```bash
# Process all AGS files in a directory
ags-processor data/*.ags -o consolidated_output.xlsx
```

### Example 4: Validation Only

```bash
# Validate files without exporting
ags-processor *.ags --validate-only -v
```

### Example 5: Python Script

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

## Example Files

Sample AGS files are included in the `data/examples/` directory:
- `sample_borehole.ags` - A programmatically generated AGS4 file with borehole data

Additional example files can be obtained from:
- **AGS Official Website**: https://www.ags.org.uk/data-format/
- **Referenced repositories**: sabinasalakhova/ags3_all_data_to_excel (contains AGS3 examples)

See `data/examples/README.md` for more information on obtaining and using example files.

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