# AGS Processor - Streamlit Version

A comprehensive Streamlit application for processing and analyzing AGS (Association of Geotechnical and Geoenvironmental Specialists) data files.

## Overview

This application recreates all functionalities of the original PySimpleGUI-based AGS Processor in a modern, web-based Streamlit framework. It provides tools for converting, combining, and extracting information from AGS geological data files.

## Features

### 1. AGS to Excel
Convert and concatenate AGS files to Excel format
- Upload multiple AGS files
- View individual AGS files before processing
- Preserves all data groups
- Handles exceptions (<UNITS>, <CONT> rows)
- Download concatenated Excel file

### 2. Combine Data
Combine data from different groups into a single Excel file
- Merge multiple Excel files
- Select specific groups to combine (CORE, DETL, WETH, FRAC, GEOL)
- Generate comprehensive combined dataset
- Download combined Excel file

### 3. Information Extraction

#### Search Keyword
- Search for keywords in geological descriptions (GEOL_DESC and Details columns)
- Manage keyword lists
- Special handling for "no recovery" searches
- Download results with boolean columns for each keyword

#### Match Soil Type & Grain Size
- Match soil types (IV, V, VI, TOPSOIL, MARINE DEPOSIT, etc.)
- Match grain sizes (CLAY, SILT, SAND, GRAVEL, etc.)
- Automatic classification based on geological descriptions
- Download results with soil type/grain size classifications

#### Query Data at Specific Depths
- Extract data at single depth points
- Extract data for depth ranges
- Flexible depth query interface
- Download extracted data

### 4. Calculate Rockhead
Calculate rockhead depth based on weathering grade and TCR criteria
- Configure core run length
- Set TCR (Total Core Recovery) threshold
- Specify continuous length requirement
- Option to include/exclude weak zones
- View summary and detailed results
- Statistics on rockhead findings
- Download summary and detailed data

### 5. Calculate Q-value
Calculate Q-value for rock mass classification
- Upload data with RQD values
- Configure Q-value parameters:
  - Jn (Joint set number)
  - Jr (Joint roughness number)
  - Ja (Joint alteration number)
  - Jw (Joint water reduction factor)
  - SRF (Stress reduction factor)
- Automatic rock quality classification
- Statistics and distribution visualization
- Download Q-value results

### 6. Future Features (Placeholders)
- Corestone Percentage
- Define Weak Seam

## Installation

### Requirements
- Python 3.7+
- pip (Python package manager)

### Install Dependencies

```bash
pip install -r requirements.txt
```

The required packages are:
- streamlit>=1.28.0
- pandas>=2.0.0
- numpy>=1.24.0
- openpyxl>=3.1.0

## Usage

### Running the Application

```bash
streamlit run streamlit_app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Workflow

1. **Start with AGS to Excel**: Convert your AGS files to Excel format
2. **Combine Data**: Merge multiple Excel files into a single combined dataset
3. **Extract Information**: Use various extraction tools to analyze your data
4. **Advanced Analysis**: Calculate rockhead depths or Q-values as needed

### File Format Requirements

#### AGS Files
- Standard AGS format (.ags extension)
- AGS3 or AGS4 format supported

#### Excel Files for Combination
- Must be outputs from the "AGS to Excel" function
- Contains standard AGS groups (PROJ, HOLE, GEOL, WETH, etc.)

#### Depth Query Files
For single depth points:
- Columns: GIU_HOLE_ID, DEPTH

For depth ranges:
- Columns: GIU_HOLE_ID, DEPTH_FROM, DEPTH_TO

## File Structure

```
AGS-Processor/
├── streamlit_app.py       # Main Streamlit application
├── ags_core.py            # Core processing functions
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── app.py                # Original PySimpleGUI app (legacy)
└── [other legacy files]
```

## Core Functions (ags_core.py)

### AGS File Processing
- `AGS4_to_dict()` - Parse AGS file to dictionary
- `AGS4_to_dataframe()` - Parse AGS file to pandas DataFrames
- `concat_ags_files()` - Concatenate multiple AGS files

### Data Combination
- `combine_ags_data()` - Combine data from multiple Excel files

### Information Extraction
- `search_keyword()` - Search for keywords in geological descriptions
- `match_soil_types()` - Match soil types and grain sizes
- `search_depth()` - Extract data at specific depths

### Advanced Calculations
- `calculate_rockhead()` - Calculate rockhead depths
- `weth_grade_to_numeric()` - Convert weathering grades to numeric
- `rock_material_criteria()` - Determine rock material criteria
- `calculate_q_value()` - Calculate Q-values for rock mass classification

## Credits

**Original Ideas**: Philip Wu @Aurecon  
**AGS_Concat**: Regine Tsui @Aurecon  
**AGS_Combine**: Christopher Ng @Aurecon  
**Original Interface**: Christopher Ng @Aurecon  
**Streamlit Conversion**: 2024

## License

This project maintains the original licensing and credits of the AGS Processor.

## Support

For issues, questions, or contributions, please refer to the repository's issue tracker.

## Version History

### v2.0 (Streamlit Version)
- Complete rewrite in Streamlit
- All original functionalities maintained
- New rockhead calculation feature
- New Q-value calculation feature
- Modern web-based interface
- Improved user experience

### v1.0 (PySimpleGUI Version)
- Original desktop application
- Basic AGS processing capabilities
