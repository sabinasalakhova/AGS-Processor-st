# Example AGS Files

This directory is for storing example AGS files for testing and demonstration purposes.

## Sources for Example AGS Files

### Official AGS Sources

1. **AGS Data Format Website**
   - Visit: https://www.ags.org.uk/data-format/
   - Download official AGS3 and AGS4 example files
   - Access the full AGS specification documents

2. **British Geological Survey**
   - AGS file utilities and sample datasets
   - Visit: https://www.bgs.ac.uk/

### Referenced Repositories

The AGS-Processor-st consolidates functionality from:

1. **sabinasalakhova/ags3_all_data_to_excel**
   - Repository: https://github.com/sabinasalakhova/ags3_all_data_to_excel
   - Contains AGS 3.1 parsing logic
   - Check repository for any included example files

2. **sabinasalakhova/AGS-Processor**
   - Original AGS processor implementation
   - May contain example files

3. **sabinasalakhova/agsfileanalysis**
   - AGS file analysis tools
   - May contain test/example files

## Using Example Files

### Quick Test

Place your AGS files in this directory and run:

```bash
# Single file
ags-processor data/examples/your_file.ags -o output.xlsx

# Multiple files
ags-processor data/examples/*.ags -o consolidated.xlsx

# Validation only
ags-processor data/examples/*.ags --validate-only -v
```

### Python API

```python
from ags_processor import AGSProcessor
import glob

# Process all example files
processor = AGSProcessor()
files = glob.glob('data/examples/*.ags')
processor.read_multiple_files(files)

# Get summary
summary = processor.get_file_summary()
print(f"Processed {summary['total_files']} files")
```

## Sample Data Included

For testing purposes, the repository includes programmatically generated sample AGS4 data in `tests/sample_data.py`. This can be used to create test files:

```python
from tests.sample_data import create_sample_ags4_file

# Create a sample file
create_sample_ags4_file('data/examples/sample_test.ags')
```

## File Format

AGS files are plain text files with a `.ags` extension containing:
- Project information (PROJ group)
- Location data (LOCA group)
- Geological descriptions (GEOL group)
- Sample information (SAMP group)
- Laboratory test results
- And many other standardized data groups

Example structure:
```
"GROUP","PROJ"
"HEADING","PROJ_ID","PROJ_NAME","PROJ_LOC"
"UNIT","","",""
"TYPE","X","X","X"
"DATA","123456","Sample Project","Sample Location"
```

## Notes

- AGS3 files use `HOLE_ID` for borehole identification
- AGS4 files use `LOCA_ID` instead
- The processor automatically detects the version
- Multiple files can be processed and consolidated
- Invalid files can be skipped with the `--skip-invalid` flag
