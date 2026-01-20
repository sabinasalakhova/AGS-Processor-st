# Streamlit UI Screenshots and Usage Guide

## Application Interface

The AGS Processor Streamlit UI provides a modern, intuitive web interface for processing geotechnical AGS files.

### Main Interface Components

#### 1. Upload & Process Tab
**Features:**
- Drag-and-drop file upload
- Multiple file selection
- Real-time processing status
- File summary with metrics (total files, tables, errors)
- Version breakdown (AGS3/AGS4)
- Processing error display

**Workflow:**
1. Click "Browse files" or drag AGS files into the upload area
2. Click "Process Files" button
3. View file summary with statistics
4. Check any processing warnings/errors in the expandable section

#### 2. Validation Tab
**Features:**
- Individual file validation results
- Color-coded status indicators (✅ valid, ❌ invalid)
- Detailed error messages with error types
- Collapsible warning sections
- AGS format compliance checking

**Information Displayed:**
- File validation status
- Error count and details
- Warning count (expandable)
- Error types (FORMAT_ERROR, VALIDATION_ERROR, etc.)

#### 3. Data Tables Tab
**Features:**
- Table selector dropdown
- Row and column count metrics
- Interactive data table viewer
- Data quality checks section
  - Null value detection by column
  - Duplicate row identification
- Scrollable table display

**Capabilities:**
- Browse all extracted AGS groups (PROJ, LOCA, GEOL, SAMP, etc.)
- View complete table contents
- Analyze data quality issues
- Sort and filter table data

#### 4. Export Tab
**Features:**
- Format selection (Excel XLSX or CSV ZIP)
- Summary sheet option for Excel
- One-click download buttons
- Success/error notifications
- Progress indicators during export

**Export Options:**
- **Excel**: Single file with multiple sheets, optional summary
- **CSV**: ZIP archive with separate CSV per table

### Sidebar Information

The sidebar provides:
- **About**: Quick overview of features
- **Supported Formats**: AGS3 and AGS4 version info
- **Quick Guide**: Step-by-step usage instructions

### Color Coding

- **Green** (Success): Valid files, successful operations
- **Red** (Error): Invalid files, critical errors
- **Yellow** (Warning): Non-critical warnings, data quality issues
- **Blue** (Info): General information, tips

### Metrics Display

Three key metrics are displayed prominently:
1. **Total Files**: Number of successfully processed files
2. **Total Tables**: Number of unique AGS groups found
3. **Errors**: Count of processing errors (inverse color for warning)

### Data Quality Features

Automatic checks include:
- **Null Values**: Column-by-column null count
- **Duplicates**: Total duplicate row count
- **Data Types**: Format compliance validation

## Running the Application

### Method 1: Direct Streamlit Command
```bash
streamlit run app.py
```

### Method 2: Launch Script
```bash
./run_app.sh
```

### Method 3: With Custom Port
```bash
streamlit run app.py --server.port=8502
```

## Browser Access

Once started, the application is accessible at:
- **Local**: http://localhost:8501
- **Network**: http://[your-ip]:8501

## Example Usage Scenario

### Processing Multiple Borehole Files

1. **Upload**: Select 3 AGS files from a site investigation
2. **Process**: Click "Process Files" to parse and consolidate
3. **Validate**: Check validation tab for any format issues
4. **Explore**: 
   - View LOCA table for borehole locations
   - Check GEOL table for geological descriptions
   - Review SAMP table for sample information
5. **Quality Check**: Review null values and duplicates
6. **Export**: Download as Excel with summary sheet

### Validation-Only Workflow

1. **Upload**: Add AGS files to check
2. **Navigate**: Go directly to Validation tab
3. **Review**: Check each file's validation status
4. **Fix Issues**: Download error report, fix in source
5. **Re-upload**: Verify fixes with green status

## Technical Details

### File Handling
- Files are stored temporarily during processing
- Automatic cleanup after session
- Secure temporary file management
- Support for large files (configurable limit)

### Performance
- Efficient DataFrame operations with pandas
- Lazy loading for large tables
- Streaming export for memory efficiency

### Security
- No permanent file storage
- Session-isolated processing
- Temporary directory cleanup
- Input validation

## Tips for Best Results

1. **File Naming**: Use descriptive names for easier identification
2. **Batch Size**: Process 10-20 files at a time for best performance
3. **Validation First**: Always check validation before exporting
4. **Data Review**: Use quality checks before finalizing
5. **Export Early**: Download results before uploading new files

## Troubleshooting

### App Won't Start
- Check Python version (>=3.9 required)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check port availability: Use `--server.port` flag

### Upload Fails
- Check file extension (.ags)
- Verify file size (default 200MB limit)
- Ensure valid AGS format

### Processing Errors
- Review validation tab for details
- Check AGS format compliance
- Verify file encoding (UTF-8 recommended)

### Export Issues
- Ensure tables are loaded (process files first)
- Check available disk space
- Try different export format

## Accessibility

The interface includes:
- High contrast colors for readability
- Clear visual indicators for status
- Keyboard navigation support
- Responsive layout for different screen sizes

## Future Enhancements

Potential additions:
- Real-time collaboration
- Database storage option
- Advanced filtering
- Custom validation rules
- API integration
- Report generation
