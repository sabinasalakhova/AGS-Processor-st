# AGS Processor - Streamlit UI

A web-based interface for processing AGS3 and AGS4 geotechnical data files.

## Features

- **File Upload**: Upload one or multiple AGS files
- **Real-time Validation**: Instant validation results with detailed error/warning messages
- **Data Exploration**: Browse and analyze data tables with quality checks
- **Export Options**: Download processed data as Excel or CSV
- **Multi-file Processing**: Consolidate data from multiple AGS files
- **Data Quality Checks**: Automatic null value and duplicate detection

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Running the App

```bash
# Start the Streamlit app
streamlit run app.py
```

The app will automatically open in your default web browser at `http://localhost:8501`

## Usage Guide

### 1. Upload & Process Tab
- Upload one or more AGS files (`.ags` extension)
- Click "Process Files" to parse and consolidate the data
- View file summary with version information and statistics

### 2. Validation Tab
- Review validation results for each uploaded file
- See detailed error and warning messages
- Check AGS format compliance

### 3. Data Tables Tab
- Browse all extracted data tables
- Select different tables from the dropdown
- View row/column counts
- Check data quality (null values, duplicates)

### 4. Export Tab
- Choose export format (Excel or CSV)
- Include summary sheet option for Excel
- Download consolidated data

## Features Overview

### File Processing
- Automatic AGS3/AGS4 version detection
- Multiple file support with data consolidation
- Skip invalid files option
- Detailed error reporting

### Data Validation
- AGS format compliance checking
- Required field validation
- Data type verification
- Warning categorization

### Data Quality Checks
- Null value detection per column
- Duplicate row identification
- Column-level statistics

### Export Options
- **Excel**: Multi-sheet workbook with optional summary
- **CSV**: ZIP file containing all tables as separate CSVs

## Supported AGS Versions

- **AGS3**: Legacy format (HOLE_ID identifier)
- **AGS4**: Current standard (LOCA_ID identifier)
  - AGS 4.0
  - AGS 4.1
  - AGS 4.2

## Keyboard Shortcuts

- `Ctrl+R` or `Cmd+R`: Refresh the app
- `Ctrl+K` or `Cmd+K`: Clear cache and refresh

## Configuration

The app uses Streamlit's default configuration. You can customize settings by creating a `.streamlit/config.toml` file:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 200
```

## Troubleshooting

### Large Files
If you're processing large AGS files, increase the upload size limit:

```bash
streamlit run app.py --server.maxUploadSize=500
```

### Port Already in Use
If port 8501 is already in use, specify a different port:

```bash
streamlit run app.py --server.port=8502
```

### Memory Issues
For processing many large files, increase Python's memory limit or process files in smaller batches.

## Development

To run in development mode with auto-reload:

```bash
streamlit run app.py --server.runOnSave=true
```

## Example Workflow

1. **Upload Files**: Use the sample file at `data/examples/sample_borehole.ags` or your own AGS files
2. **Process**: Click the "Process Files" button
3. **Validate**: Check the Validation tab for any issues
4. **Explore**: Browse data tables and check data quality
5. **Export**: Download the consolidated data in your preferred format

## Technical Details

- **Framework**: Streamlit 1.28+
- **Backend**: AGS Processor library (python-ags4, pandas)
- **Export**: openpyxl (Excel), CSV with ZIP compression
- **File Handling**: Temporary file storage for security

## Links

- [Streamlit Documentation](https://docs.streamlit.io)
- [AGS Data Format](https://www.ags.org.uk/data-format/)
- [python-ags4 Library](https://pypi.org/project/python-AGS4/)
