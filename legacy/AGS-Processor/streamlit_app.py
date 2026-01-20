"""
AGS Processor - Streamlit Version

This is a comprehensive Streamlit application that recreates all functionalities 
of the AGS Processor originally built with PySimpleGUI.

Credits:
Original Ideas: Philip Wu @Aurecon
AGS_Concat: Regine Tsui @Aurecon
AGS_Combine: Christopher Ng @Aurecon
UglyInterface Design: Christopher Ng @Aurecon
Streamlit Conversion: 2024
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
from io import BytesIO
import base64

# Import core processing modules
from ags_core import (
    AGS4_to_dataframe,
    concat_ags_files,
    combine_ags_data,
    search_keyword,
    match_soil_types,
    search_depth,
    calculate_rockhead,
    calculate_q_value
)

# Page configuration
st.set_page_config(
    page_title="AGS Processor",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #2E7D32;
        color: white;
        border-radius: 5px;
        padding: 10px 24px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #1B5E20;
    }
    h1, h2, h3 {
        color: #1B5E20;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'selected_files' not in st.session_state:
    st.session_state.selected_files = []
if 'keyword_list' not in st.session_state:
    st.session_state.keyword_list = []
if 'soil_type_list' not in st.session_state:
    st.session_state.soil_type_list = ['IV', 'V', 'VI (RESIDUAL SOIL)', 'TOPSOIL', 'MARINE DEPOSIT', 'ALLUVIUM', 'COLLUVIUM', 'FILL', 'ESTUARINE DEPOSIT']
if 'grain_size_list' not in st.session_state:
    st.session_state.grain_size_list = ['CLAY', 'FINE', 'SILT', 'SAND', 'GRAVEL', 'COBBLE', 'BOULDER']

# Sidebar navigation
st.sidebar.title("AGS Processor v2.0")
st.sidebar.markdown("---")

# Navigation menu
menu_options = {
    "🏠 Home": "Home",
    "📊 AGS to Excel": "AGS to Excel",
    "🔄 Combine Data": "Combine Data",
    "🔍 Information Extraction": "Information Extraction",
    "🪨 Calculate Rockhead": "Calculate Rockhead",
    "📈 Corestone Percentage": "Corestone Percentage",
    "⚠️ Define Weak Seam": "Define Weak Seam",
    "📐 Calculate Q-value": "Calculate Q-value"
}

selected_menu = st.sidebar.radio("Navigation", list(menu_options.keys()))
st.session_state.page = menu_options[selected_menu]

st.sidebar.markdown("---")
st.sidebar.info("""
**AGS Processor** helps you process and analyze AGS (Association of Geotechnical and Geoenvironmental Specialists) data files.
""")

# Utility function to create download link
def create_download_link(df, filename):
    """Create a download link for a pandas DataFrame as Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">Download {filename}</a>'

# ============================================================================
# HOME PAGE
# ============================================================================
if st.session_state.page == 'Home':
    st.title("🗂️ AGS Processor")
    st.markdown("### Welcome to the AGS Processor Application")
    
    st.markdown("""
    This application provides comprehensive tools for processing AGS (Association of Geotechnical 
    and Geoenvironmental Specialists) data files.
    
    #### Available Functions:
    
    1. **AGS to Excel** - Convert and concatenate AGS files to Excel format
        - Supports multiple AGS files
        - Preserves all data groups
        - Handles exceptions (<UNITS>, <CONT> rows)
    
    2. **Combine Data** - Combine data from different groups into a single Excel file
        - Merge multiple Excel files
        - Select specific groups to combine
        - Generate comprehensive combined dataset
    
    3. **Information Extraction** - Extract specific information from combined data
        - **Search Keyword**: Find keywords in geological descriptions
        - **Match Soil**: Match soil types with grain sizes
        - **Search Depth**: Query data at specific depths or ranges
    
    4. **Advanced Functions** (Coming Soon)
        - Calculate Rockhead
        - Corestone Percentage
        - Define Weak Seam
        - Calculate Q-value
    
    #### Getting Started:
    Use the sidebar to navigate to the function you need. Each function includes detailed 
    instructions and input validation to ensure accurate processing.
    """)
    
    st.info("💡 **Tip**: Start with 'AGS to Excel' to convert your AGS files, then use 'Combine Data' to merge them before extraction.")

# ============================================================================
# AGS TO EXCEL PAGE
# ============================================================================
elif st.session_state.page == 'AGS to Excel':
    st.title("📊 AGS to Excel")
    st.markdown("Convert and concatenate AGS files to Excel format")
    
    st.markdown("""
    **Instructions:**
    1. Upload one or more AGS files
    2. Optionally view individual AGS files before processing
    3. Click 'Concatenate' to convert to Excel format
    4. Download the resulting Excel file
    """)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload AGS Files",
        type=['ags', 'AGS'],
        accept_multiple_files=True,
        key='ags_files'
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) selected")
        
        # Display selected files
        st.markdown("**Selected Files:**")
        for i, file in enumerate(uploaded_files):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.text(f"{i+1}. {file.name}")
            with col2:
                if st.button(f"View", key=f"view_{i}"):
                    st.session_state.view_file_index = i
        
        # View single AGS file
        if hasattr(st.session_state, 'view_file_index'):
            idx = st.session_state.view_file_index
            st.markdown(f"### Viewing: {uploaded_files[idx].name}")
            
            try:
                # Parse AGS file
                df_dict, headings = AGS4_to_dataframe(uploaded_files[idx])
                
                # Create tabs for different groups
                available_groups = list(df_dict.keys())
                if available_groups:
                    tabs = st.tabs(available_groups[:10])  # Limit to first 10 groups for display
                    
                    for i, group in enumerate(available_groups[:10]):
                        with tabs[i]:
                            st.dataframe(df_dict[group], use_container_width=True)
                else:
                    st.warning("No data groups found in the AGS file")
                    
            except Exception as e:
                st.error(f"Error parsing AGS file: {str(e)}")
        
        st.markdown("---")
        
        # GIU Number input
        st.markdown("**Processing Options:**")
        giu_number = st.text_input(
            "GIU Number (for reference)",
            placeholder="Enter a unique identifier",
            help="Assign a unique number for ease of reference"
        )
        
        # Concatenate button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("🔄 Concatenate Files", type="primary"):
                if not giu_number:
                    st.warning("Please enter a GIU number")
                else:
                    with st.spinner("Processing AGS files..."):
                        try:
                            # Process files
                            result_df = concat_ags_files(uploaded_files, giu_number)
                            
                            # Store in session state
                            st.session_state.processed_data = result_df
                            st.success("✅ Files concatenated successfully!")
                            
                        except Exception as e:
                            st.error(f"Error processing files: {str(e)}")
        
        # Download button
        if hasattr(st.session_state, 'processed_data'):
            with col2:
                # Create Excel file in memory
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for sheet_name, df in st.session_state.processed_data.items():
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name="concatenated_ags.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# ============================================================================
# COMBINE DATA PAGE
# ============================================================================
elif st.session_state.page == 'Combine Data':
    st.title("🔄 Combine Data")
    st.markdown("Combine data from different groups in Excel files into a single-tabbed file")
    
    st.markdown("""
    **Instructions:**
    1. Upload Excel files from the 'AGS to Excel' function
    2. Select which groups to combine (or leave empty for all groups)
    3. Click 'Combine' to merge the data
    4. Download the combined Excel file
    """)
    
    st.info("📝 **Note**: Only files from the AGS to Excel function should be used here.")
    
    # File uploader
    uploaded_excel_files = st.file_uploader(
        "Upload Excel Files",
        type=['xlsx', 'XLSX'],
        accept_multiple_files=True,
        key='excel_files'
    )
    
    if uploaded_excel_files:
        st.success(f"✅ {len(uploaded_excel_files)} file(s) selected")
        
        # Display selected files
        st.markdown("**Selected Files:**")
        for i, file in enumerate(uploaded_excel_files):
            st.text(f"{i+1}. {file.name}")
        
        # Group selection
        st.markdown("**Select Groups to Combine:**")
        st.markdown("(Leave empty to combine all groups)")
        
        group_options = ['CORE', 'DETL', 'WETH', 'FRAC', 'GEOL']
        selected_groups = st.multiselect(
            "Groups",
            options=group_options,
            help="Select specific groups or leave empty for all"
        )
        
        # Combine button
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔄 Combine Data", type="primary"):
                with st.spinner("Combining data..."):
                    try:
                        # Combine data
                        combined_df = combine_ags_data(
                            uploaded_excel_files, 
                            selected_groups if selected_groups else None
                        )
                        
                        # Store in session state
                        st.session_state.combined_data = combined_df
                        st.success("✅ Data combined successfully!")
                        
                        # Show preview
                        st.markdown("**Preview of Combined Data:**")
                        st.dataframe(combined_df.head(20), use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Error combining data: {str(e)}")
        
        # Download button
        if hasattr(st.session_state, 'combined_data'):
            with col2:
                output = BytesIO()
                st.session_state.combined_data.to_excel(output, index=False, engine='openpyxl')
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📥 Download Combined Data",
                    data=excel_data,
                    file_name="combined_ags.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# ============================================================================
# INFORMATION EXTRACTION PAGE
# ============================================================================
elif st.session_state.page == 'Information Extraction':
    st.title("🔍 Information Extraction")
    st.markdown("Extract specific information from combined AGS data")
    
    # Sub-menu for extraction type
    extraction_type = st.radio(
        "Select Extraction Type:",
        ["Search Keyword", "Match Soil Type & Grain Size", "Query Data at Specific Depths"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # ========================================================================
    # SEARCH KEYWORD
    # ========================================================================
    if extraction_type == "Search Keyword":
        st.markdown("### 🔎 Search Keyword")
        st.markdown("Search for keywords in GEOL_DESC and Details columns")
        
        # Upload combined file
        input_file = st.file_uploader(
            "Upload Combined AGS Excel File",
            type=['xlsx'],
            key='keyword_input'
        )
        
        # Keyword management
        st.markdown("**Manage Keywords:**")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            new_keyword = st.text_input("Add keyword:", key='new_keyword')
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Add"):
                if new_keyword and new_keyword not in st.session_state.keyword_list:
                    st.session_state.keyword_list.append(new_keyword)
                    st.rerun()
        
        # Display current keywords
        if st.session_state.keyword_list:
            st.markdown("**Current Keywords:**")
            for i, kw in enumerate(st.session_state.keyword_list):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"• {kw}")
                with col2:
                    if st.button("🗑️", key=f"del_kw_{i}"):
                        st.session_state.keyword_list.pop(i)
                        st.rerun()
            
            if st.button("Clear All Keywords"):
                st.session_state.keyword_list = []
                st.rerun()
        
        # Search button
        if input_file and st.session_state.keyword_list:
            if st.button("🔍 Search", type="primary"):
                with st.spinner("Searching..."):
                    try:
                        df_in = pd.read_excel(input_file)
                        result_df = search_keyword(df_in, st.session_state.keyword_list)
                        
                        st.session_state.keyword_result = result_df
                        st.success("✅ Search completed!")
                        
                        # Preview
                        st.markdown("**Preview of Results:**")
                        st.dataframe(result_df.head(20), use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Error during search: {str(e)}")
            
            # Download
            if hasattr(st.session_state, 'keyword_result'):
                output = BytesIO()
                st.session_state.keyword_result.to_excel(output, index=False, engine='openpyxl')
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📥 Download Results",
                    data=excel_data,
                    file_name="keyword_search_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        elif input_file:
            st.warning("Please add at least one keyword to search")
        else:
            st.info("Upload a file and add keywords to begin searching")
    
    # ========================================================================
    # MATCH SOIL TYPE & GRAIN SIZE
    # ========================================================================
    elif extraction_type == "Match Soil Type & Grain Size":
        st.markdown("### 🌍 Match Soil Type & Grain Size")
        st.markdown("Match soil types with grain sizes from geological descriptions")
        
        # Upload combined file
        input_file = st.file_uploader(
            "Upload Combined AGS Excel File",
            type=['xlsx'],
            key='soil_input'
        )
        
        # Two columns for soil types and grain sizes
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Soil Types:**")
            # Add new soil type
            new_soil = st.text_input("Add soil type:", key='new_soil')
            if st.button("➕ Add Soil Type"):
                if new_soil and new_soil not in st.session_state.soil_type_list:
                    st.session_state.soil_type_list.append(new_soil)
                    st.rerun()
            
            # Display soil types
            if st.session_state.soil_type_list:
                for i, soil in enumerate(st.session_state.soil_type_list):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.text(f"• {soil}")
                    with c2:
                        if st.button("🗑️", key=f"del_soil_{i}"):
                            st.session_state.soil_type_list.pop(i)
                            st.rerun()
                
                if st.button("Clear All Soil Types"):
                    st.session_state.soil_type_list = []
                    st.rerun()
        
        with col2:
            st.markdown("**Grain Sizes:**")
            # Add new grain size
            new_grain = st.text_input("Add grain size:", key='new_grain')
            if st.button("➕ Add Grain Size"):
                if new_grain and new_grain not in st.session_state.grain_size_list:
                    st.session_state.grain_size_list.append(new_grain)
                    st.rerun()
            
            # Display grain sizes
            if st.session_state.grain_size_list:
                for i, grain in enumerate(st.session_state.grain_size_list):
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.text(f"• {grain}")
                    with c2:
                        if st.button("🗑️", key=f"del_grain_{i}"):
                            st.session_state.grain_size_list.pop(i)
                            st.rerun()
                
                if st.button("Clear All Grain Sizes"):
                    st.session_state.grain_size_list = []
                    st.rerun()
        
        # Match button
        if input_file:
            if st.button("🔄 Match", type="primary"):
                with st.spinner("Matching..."):
                    try:
                        df_in = pd.read_excel(input_file)
                        result_df = match_soil_types(
                            df_in, 
                            st.session_state.soil_type_list,
                            st.session_state.grain_size_list
                        )
                        
                        st.session_state.soil_match_result = result_df
                        st.success("✅ Matching completed!")
                        
                        # Preview
                        st.markdown("**Preview of Results:**")
                        st.dataframe(result_df.head(20), use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Error during matching: {str(e)}")
            
            # Download
            if hasattr(st.session_state, 'soil_match_result'):
                output = BytesIO()
                st.session_state.soil_match_result.to_excel(output, index=False, engine='openpyxl')
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📥 Download Results",
                    data=excel_data,
                    file_name="soil_match_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("Upload a file to begin matching")
    
    # ========================================================================
    # QUERY DATA AT SPECIFIC DEPTHS
    # ========================================================================
    elif extraction_type == "Query Data at Specific Depths":
        st.markdown("### 📏 Query Data at Specific Depths")
        st.markdown("Extract data at specific depths or depth ranges")
        
        # Upload files
        col1, col2 = st.columns(2)
        
        with col1:
            combined_data_file = st.file_uploader(
                "Upload Combined AGS Data Excel",
                type=['xlsx'],
                key='depth_data'
            )
        
        with col2:
            depth_file = st.file_uploader(
                "Upload Depth Query Excel",
                type=['xlsx'],
                key='depth_query',
                help="Excel with GIU_HOLE_ID and DEPTH or DEPTH_FROM/DEPTH_TO columns"
            )
        
        # Query type
        query_type = st.radio(
            "Depth Data Format:",
            ["Single Depth Points", "From & To Depth Ranges"],
            horizontal=True
        )
        
        # Process button
        if combined_data_file and depth_file:
            if st.button("🔍 Search Depths", type="primary"):
                with st.spinner("Processing..."):
                    try:
                        df_data = pd.read_excel(combined_data_file)
                        df_depth = pd.read_excel(depth_file)
                        
                        result_df = search_depth(
                            df_data,
                            df_depth,
                            query_type == "Single Depth Points"
                        )
                        
                        st.session_state.depth_result = result_df
                        st.success("✅ Depth query completed!")
                        
                        # Preview
                        st.markdown("**Preview of Results:**")
                        st.dataframe(result_df.head(20), use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Error during depth query: {str(e)}")
            
            # Download
            if hasattr(st.session_state, 'depth_result'):
                output = BytesIO()
                st.session_state.depth_result.to_excel(output, index=False, engine='openpyxl')
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📥 Download Results",
                    data=excel_data,
                    file_name="depth_query_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.info("Upload both files to begin depth query")

# ============================================================================
# CALCULATE ROCKHEAD PAGE
# ============================================================================
elif st.session_state.page == 'Calculate Rockhead':
    st.title("🪨 Calculate Rockhead")
    st.markdown("Calculate rockhead depth based on weathering grade and TCR criteria")
    
    st.markdown("""
    **Instructions:**
    1. Upload Combined AGS data Excel file
    2. Configure calculation parameters
    3. View and download rockhead calculation results
    
    **Criteria:**
    - Weathering grade I-III (Fresh to Moderately Weathered)
    - TCR (Total Core Recovery) above threshold
    - Continuous rock material over specified length
    """)
    
    # File upload
    input_file = st.file_uploader(
        "Upload Combined AGS Excel File",
        type=['xlsx'],
        key='rockhead_input',
        help="Upload the combined data file from the Combine Data function"
    )
    
    if input_file:
        st.success("✅ File uploaded successfully")
        
        # Configuration parameters
        st.markdown("### Calculation Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            core_run = st.number_input(
                "Core Run Length (m)",
                min_value=0.5,
                max_value=10.0,
                value=1.0,
                step=0.5,
                help="Length of core run in meters"
            )
            
            tcr_threshold = st.number_input(
                "TCR Threshold (%)",
                min_value=0,
                max_value=100,
                value=85,
                step=5,
                help="Minimum Total Core Recovery percentage"
            )
        
        with col2:
            continuous_length = st.number_input(
                "Continuous Length (m)",
                min_value=1.0,
                max_value=20.0,
                value=5.0,
                step=1.0,
                help="Required continuous length of rock material"
            )
            
            include_weak = st.checkbox(
                "Include Weak Zones",
                value=False,
                help="Include moderately weak and weak zones in rock material"
            )
        
        # Calculate button
        if st.button("🧮 Calculate Rockhead", type="primary"):
            with st.spinner("Calculating rockhead..."):
                try:
                    df_in = pd.read_excel(input_file)
                    
                    # Calculate rockhead
                    result = calculate_rockhead(
                        df_in,
                        core_run=core_run,
                        tcr_threshold=tcr_threshold,
                        continuous_length=continuous_length,
                        include_weak=include_weak
                    )
                    
                    st.session_state.rockhead_result = result
                    st.success("✅ Rockhead calculation completed!")
                    
                    # Display summary
                    st.markdown("### Rockhead Summary")
                    st.dataframe(result['summary'], use_container_width=True)
                    
                    # Statistics
                    st.markdown("### Statistics")
                    col1, col2, col3 = st.columns(3)
                    
                    total_holes = len(result['rockhead_depths'])
                    found = sum(1 for v in result['rockhead_depths'].values() if v != 'Not Found')
                    not_found = total_holes - found
                    
                    with col1:
                        st.metric("Total Boreholes", total_holes)
                    with col2:
                        st.metric("Rockhead Found", found)
                    with col3:
                        st.metric("Rockhead Not Found", not_found)
                    
                    # Detailed data preview
                    st.markdown("### Detailed Data Preview")
                    st.dataframe(result['detailed_data'].head(50), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error calculating rockhead: {str(e)}")
        
        # Download buttons
        if hasattr(st.session_state, 'rockhead_result'):
            st.markdown("---")
            st.markdown("### Download Results")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Download summary
                output_summary = BytesIO()
                st.session_state.rockhead_result['summary'].to_excel(
                    output_summary, index=False, engine='openpyxl'
                )
                excel_data = output_summary.getvalue()
                
                st.download_button(
                    label="📥 Download Summary",
                    data=excel_data,
                    file_name="rockhead_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col2:
                # Download detailed data
                output_detailed = BytesIO()
                st.session_state.rockhead_result['detailed_data'].to_excel(
                    output_detailed, index=False, engine='openpyxl'
                )
                excel_data = output_detailed.getvalue()
                
                st.download_button(
                    label="📥 Download Detailed Data",
                    data=excel_data,
                    file_name="rockhead_detailed.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# ============================================================================
# CALCULATE Q-VALUE PAGE
# ============================================================================
elif st.session_state.page == 'Calculate Q-value':
    st.title("📐 Calculate Q-value")
    st.markdown("Calculate Q-value for rock mass classification")
    
    st.markdown("""
    **Instructions:**
    1. Upload Combined AGS data Excel file with RQD data
    2. Configure Q-value parameters (Jn, Jr, Ja, Jw, SRF)
    3. View and download Q-value calculation results
    
    **Formula:**
    Q = (RQD/Jn) × (Jr/Ja) × (Jw/SRF)
    
    **Parameters:**
    - **RQD**: Rock Quality Designation (from data)
    - **Jn**: Joint set number
    - **Jr**: Joint roughness number
    - **Ja**: Joint alteration number
    - **Jw**: Joint water reduction factor
    - **SRF**: Stress reduction factor
    """)
    
    # File upload
    input_file = st.file_uploader(
        "Upload Combined AGS Excel File",
        type=['xlsx'],
        key='qvalue_input',
        help="Upload file with RQD data"
    )
    
    if input_file:
        st.success("✅ File uploaded successfully")
        
        # Show available columns
        try:
            df_preview = pd.read_excel(input_file, nrows=5)
            st.markdown("**Available Columns:**")
            st.write(", ".join(df_preview.columns.tolist()))
        except:
            pass
        
        # Configuration parameters
        st.markdown("### Q-value Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            rqd_column = st.text_input(
                "RQD Column Name",
                value="RQD",
                help="Name of the column containing RQD values"
            )
            
            jn = st.number_input(
                "Jn (Joint Set Number)",
                min_value=0.5,
                max_value=20.0,
                value=9.0,
                step=0.5,
                help="Number of joint sets: 0.5-20"
            )
            
            jr = st.number_input(
                "Jr (Joint Roughness Number)",
                min_value=0.5,
                max_value=4.0,
                value=1.0,
                step=0.5,
                help="Joint roughness: 0.5-4"
            )
        
        with col2:
            ja = st.number_input(
                "Ja (Joint Alteration Number)",
                min_value=0.75,
                max_value=20.0,
                value=1.0,
                step=0.25,
                help="Joint alteration: 0.75-20"
            )
            
            jw = st.number_input(
                "Jw (Joint Water Reduction Factor)",
                min_value=0.05,
                max_value=1.0,
                value=1.0,
                step=0.05,
                help="Water reduction: 0.05-1.0"
            )
            
            srf = st.number_input(
                "SRF (Stress Reduction Factor)",
                min_value=0.5,
                max_value=20.0,
                value=1.0,
                step=0.5,
                help="Stress reduction: 0.5-20"
            )
        
        # Calculate button
        if st.button("🧮 Calculate Q-value", type="primary"):
            with st.spinner("Calculating Q-values..."):
                try:
                    df_in = pd.read_excel(input_file)
                    
                    # Calculate Q-value
                    result_df = calculate_q_value(
                        df_in,
                        rqd_col=rqd_column,
                        jn=jn,
                        jr=jr,
                        ja=ja,
                        jw=jw,
                        srf=srf
                    )
                    
                    st.session_state.qvalue_result = result_df
                    st.success("✅ Q-value calculation completed!")
                    
                    # Statistics
                    st.markdown("### Statistics")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    valid_q = result_df['Q_value'].notna().sum()
                    mean_q = result_df['Q_value'].mean()
                    min_q = result_df['Q_value'].min()
                    max_q = result_df['Q_value'].max()
                    
                    with col1:
                        st.metric("Valid Q-values", valid_q)
                    with col2:
                        st.metric("Mean Q-value", f"{mean_q:.2f}" if not pd.isna(mean_q) else "N/A")
                    with col3:
                        st.metric("Min Q-value", f"{min_q:.2f}" if not pd.isna(min_q) else "N/A")
                    with col4:
                        st.metric("Max Q-value", f"{max_q:.2f}" if not pd.isna(max_q) else "N/A")
                    
                    # Rock quality distribution
                    if 'Rock_Quality' in result_df.columns:
                        st.markdown("### Rock Quality Distribution")
                        quality_counts = result_df['Rock_Quality'].value_counts()
                        st.bar_chart(quality_counts)
                    
                    # Preview results
                    st.markdown("### Results Preview")
                    display_cols = ['HOLE_ID', 'DEPTH_FROM', 'DEPTH_TO', 'RQD_numeric', 'Q_value', 'Rock_Quality']
                    available_cols = [col for col in display_cols if col in result_df.columns]
                    st.dataframe(result_df[available_cols].head(50), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error calculating Q-value: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
        
        # Download button
        if hasattr(st.session_state, 'qvalue_result'):
            st.markdown("---")
            output = BytesIO()
            st.session_state.qvalue_result.to_excel(output, index=False, engine='openpyxl')
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 Download Q-value Results",
                data=excel_data,
                file_name="qvalue_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ============================================================================
# PLACEHOLDER PAGES FOR REMAINING FEATURES
# ============================================================================
elif st.session_state.page in ['Corestone Percentage', 'Define Weak Seam']:
    st.title(f"⚙️ {st.session_state.page}")
    st.info(f"""
    This function is currently under development.
    
    The **{st.session_state.page}** feature will be available in a future update.
    
    Please check back later or contact the development team for more information.
    """)
    
    st.markdown("---")
    st.markdown("### Coming Soon")
    st.markdown("""
    We are working on implementing this feature with the following capabilities:
    - Advanced geological analysis
    - Automated calculations
    - Interactive visualizations
    - Export functionality
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
<small>
**AGS Processor v2.0**<br>
Streamlit Implementation<br>
© 2024
</small>
""", unsafe_allow_html=True)
