"""
Streamlit UI for AGS Processor

A web-based interface for processing AGS3 and AGS4 geotechnical data files.
"""

import streamlit as st
import pandas as pd
import io
import tempfile
import os
from pathlib import Path

from ags_processor import AGSProcessor, AGSValidator, AGSExporter, GeotechnicalCalculations


# Page configuration
st.set_page_config(
    page_title="AGS Processor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    .info-box {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'processor' not in st.session_state:
        st.session_state.processor = AGSProcessor()
    if 'validator' not in st.session_state:
        st.session_state.validator = AGSValidator()
    if 'exporter' not in st.session_state:
        st.session_state.exporter = AGSExporter()
    if 'calculations' not in st.session_state:
        st.session_state.calculations = GeotechnicalCalculations()
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []
    if 'tables' not in st.session_state:
        st.session_state.tables = {}


def display_header():
    """Display the application header."""
    st.markdown('<p class="main-header">🔍 AGS Processor</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Process AGS3 and AGS4 geotechnical data files with data quality validation</p>',
        unsafe_allow_html=True
    )
    st.markdown("---")


def sidebar_info():
    """Display information in the sidebar."""
    st.sidebar.header("About")
    st.sidebar.info(
        """
        **AGS Processor** is a comprehensive tool for processing 
        AGS3 and AGS4 geotechnical data files.
        
        **Features:**
        - Multi-file processing
        - Data validation
        - Quality checks
        - Excel/CSV export
        - Data consolidation
        """
    )
    
    st.sidebar.header("Supported Formats")
    st.sidebar.markdown("""
    - **AGS3**: Legacy format
    - **AGS4**: Current standard (4.0, 4.1, 4.2)
    """)
    
    st.sidebar.header("Quick Guide")
    st.sidebar.markdown("""
    1. Upload AGS file(s)
    2. Review validation results
    3. Explore data tables
    4. Export to Excel/CSV
    """)


def process_uploaded_files(uploaded_files):
    """Process uploaded AGS files."""
    if not uploaded_files:
        return
    
    st.session_state.processor.clear()
    st.session_state.processed_files = []
    
    with st.spinner("Processing files..."):
        # Create temporary directory for uploaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            file_paths = []
            
            # Save uploaded files to temp directory
            for uploaded_file in uploaded_files:
                temp_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(temp_path)
            
            # Process files
            file_data = st.session_state.processor.read_multiple_files(
                file_paths, 
                skip_invalid=True
            )
            
            st.session_state.processed_files = list(file_data.keys())
            st.session_state.tables = st.session_state.processor.get_all_tables()


def display_file_summary():
    """Display summary of processed files."""
    if not st.session_state.processed_files:
        return
    
    summary = st.session_state.processor.get_file_summary()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Files", summary['total_files'])
    
    with col2:
        st.metric("Total Tables", summary['total_tables'])
    
    with col3:
        total_errors = summary['total_errors']
        st.metric("Errors", total_errors, delta_color="inverse")
    
    # Display version breakdown
    if summary['files_by_version']:
        st.subheader("Files by Version")
        version_df = pd.DataFrame([
            {'Version': version, 'Count': count}
            for version, count in summary['files_by_version'].items()
        ])
        st.dataframe(version_df, use_container_width=True, hide_index=True)


def display_validation_results(uploaded_files):
    """Display validation results for uploaded files."""
    if not uploaded_files:
        return
    
    st.subheader("📋 Validation Results")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        for uploaded_file in uploaded_files:
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            with st.expander(f"📄 {uploaded_file.name}", expanded=False):
                result = st.session_state.validator.validate_file(temp_path)
                
                if result['valid']:
                    st.success(f"✅ File is valid")
                else:
                    st.error(f"❌ File has errors")
                
                # Display errors
                if result['errors']:
                    st.markdown("**Errors:**")
                    for error in result['errors']:
                        st.error(f"[{error['type']}] {error['message']}")
                
                # Display warnings
                if result['warnings']:
                    st.markdown("**Warnings:**")
                    with st.expander(f"Show {len(result['warnings'])} warning(s)", expanded=False):
                        for warning in result['warnings']:
                            st.warning(f"[{warning['type']}] {warning['message']}")


def display_tables():
    """Display data tables."""
    if not st.session_state.tables:
        st.info("No data to display. Please upload and process AGS files first.")
        return
    
    st.subheader("📊 Data Tables")
    
    # Table selector
    table_names = list(st.session_state.tables.keys())
    selected_table = st.selectbox("Select Table", table_names)
    
    if selected_table:
        df = st.session_state.tables[selected_table]
        
        # Display table info
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rows", len(df))
        with col2:
            st.metric("Columns", len(df.columns))
        
        # Display dataframe
        st.dataframe(df, use_container_width=True, height=400)
        
        # Data quality checks
        with st.expander("🔍 Data Quality Checks", expanded=False):
            # Check for null values
            null_counts = df.isnull().sum()
            if null_counts.any():
                st.markdown("**Null Values:**")
                null_df = pd.DataFrame({
                    'Column': null_counts[null_counts > 0].index,
                    'Null Count': null_counts[null_counts > 0].values
                })
                st.dataframe(null_df, use_container_width=True, hide_index=True)
            else:
                st.success("No null values found")
            
            # Check for duplicates
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                st.warning(f"⚠️ {duplicates} duplicate row(s) found")
            else:
                st.success("No duplicate rows found")


def export_data():
    """Handle data export."""
    if not st.session_state.tables:
        st.info("No data to export. Please upload and process AGS files first.")
        return
    
    st.subheader("📥 Export Data")
    
    export_format = st.radio(
        "Export Format",
        ["Excel (XLSX)", "CSV (Multiple Files)"],
        horizontal=True
    )
    
    include_summary = st.checkbox("Include summary sheet (Excel only)", value=True)
    
    if st.button("Generate Export File", type="primary"):
        with st.spinner("Generating export file..."):
            try:
                if export_format == "Excel (XLSX)":
                    # Export to Excel
                    output = io.BytesIO()
                    
                    # Create a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                        tmp_path = tmp_file.name
                    
                    success = st.session_state.exporter.export_to_excel(
                        st.session_state.tables,
                        tmp_path,
                        include_summary=include_summary
                    )
                    
                    if success:
                        with open(tmp_path, 'rb') as f:
                            output = f.read()
                        
                        st.download_button(
                            label="📥 Download Excel File",
                            data=output,
                            file_name="ags_export.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        st.success("✅ Export file generated successfully!")
                    else:
                        st.error("❌ Export failed")
                        for error in st.session_state.exporter.get_errors():
                            st.error(error)
                    
                    # Clean up
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass
                
                else:  # CSV
                    # Create ZIP file with all CSV files
                    import zipfile
                    
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Export to CSV
                        success = st.session_state.exporter.export_to_csv(
                            st.session_state.tables,
                            temp_dir
                        )
                        
                        if success:
                            # Create ZIP file
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                for csv_file in Path(temp_dir).glob('*.csv'):
                                    zip_file.write(csv_file, csv_file.name)
                            
                            st.download_button(
                                label="📥 Download CSV Files (ZIP)",
                                data=zip_buffer.getvalue(),
                                file_name="ags_export.zip",
                                mime="application/zip"
                            )
                            st.success("✅ Export files generated successfully!")
                        else:
                            st.error("❌ Export failed")
                            for error in st.session_state.exporter.get_errors():
                                st.error(error)
            
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")


def display_geotechnical_calculations():
    """Display geotechnical calculation tools."""
    if not st.session_state.tables:
        st.info("No data loaded. Please upload and process AGS files first.")
        return
    
    st.markdown("""
    Perform geotechnical calculations on your AGS data including:
    - **Rockhead Detection**: Identify soil-rock interface
    - **Corestone Identification**: Detect less-weathered rock blocks
    - **Q-Value Calculation**: NGI rock mass classification
    """)
    
    calc_type = st.selectbox(
        "Select Calculation Type",
        ["Rockhead Detection", "Corestone Identification", "Q-Value Calculator", "Q-Value Bulk Calculation"]
    )
    
    if calc_type == "Rockhead Detection":
        st.subheader("🪨 Rockhead Detection")
        st.markdown("Detect the interface between soil/weathered material and hard rock.")
        
        if 'GEOL' in st.session_state.tables:
            geol_df = st.session_state.tables['GEOL']
            
            if st.button("Detect Rockhead", type="primary"):
                with st.spinner("Detecting rockhead..."):
                    rockhead_depths = st.session_state.calculations.detect_rockhead(geol_df)
                    
                    if rockhead_depths:
                        result_df = pd.DataFrame([
                            {'Location': loc, 'Rockhead Depth (m)': depth}
                            for loc, depth in rockhead_depths.items()
                        ])
                        
                        st.success(f"✅ Rockhead detected at {len(rockhead_depths)} location(s)")
                        st.dataframe(result_df, use_container_width=True, hide_index=True)
                        
                        # Download option
                        csv = result_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Rockhead Data (CSV)",
                            data=csv,
                            file_name="rockhead_depths.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("⚠️ No rockhead detected. Check if GEOL data contains rock descriptions.")
        else:
            st.warning("⚠️ GEOL table not found. Please ensure your AGS files contain geological data.")
    
    elif calc_type == "Corestone Identification":
        st.subheader("💎 Corestone Identification")
        st.markdown("Identify less-weathered rock blocks within weathered profiles.")
        
        if 'GEOL' in st.session_state.tables:
            geol_df = st.session_state.tables['GEOL']
            
            min_thickness = st.number_input(
                "Minimum Thickness (m)",
                min_value=0.1,
                max_value=10.0,
                value=0.5,
                step=0.1,
                help="Minimum thickness to classify as corestone"
            )
            
            if st.button("Identify Corestones", type="primary"):
                with st.spinner("Identifying corestones..."):
                    corestones_df = st.session_state.calculations.detect_corestones(
                        geol_df,
                        min_thickness=min_thickness
                    )
                    
                    if not corestones_df.empty:
                        st.success(f"✅ Found {len(corestones_df)} corestone(s)")
                        st.dataframe(corestones_df, use_container_width=True, hide_index=True)
                        
                        # Statistics
                        st.markdown("**Statistics:**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Corestones", len(corestones_df))
                        with col2:
                            st.metric("Avg Thickness (m)", f"{corestones_df['THICKNESS'].mean():.2f}")
                        with col3:
                            st.metric("Max Thickness (m)", f"{corestones_df['THICKNESS'].max():.2f}")
                        
                        # Download option
                        csv = corestones_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Corestone Data (CSV)",
                            data=csv,
                            file_name="corestones.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("⚠️ No corestones identified with current criteria.")
        else:
            st.warning("⚠️ GEOL table not found.")
    
    elif calc_type == "Q-Value Calculator":
        st.subheader("📐 Q-Value Calculator (NGI Rock Mass Classification)")
        st.markdown("Calculate Q-value: **Q = (RQD/Jn) × (Jr/Ja) × (Jw/SRF)**")
        
        # Display parameter guide
        with st.expander("📖 Parameter Selection Guide", expanded=False):
            guide = st.session_state.calculations.get_q_parameters_guide()
            for param, info in guide.items():
                st.markdown(f"**{param}**: {info['description']}")
                if isinstance(info.get('guidelines'), dict):
                    for key, value in info['guidelines'].items():
                        st.markdown(f"  - {key}: {value}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            rqd = st.number_input("RQD (%)", min_value=0.0, max_value=100.0, value=75.0, step=1.0)
            jn = st.number_input("Jn (Joint set number)", min_value=0.5, max_value=20.0, value=4.0, step=0.5)
            jr = st.number_input("Jr (Joint roughness)", min_value=0.5, max_value=4.0, value=2.0, step=0.5)
        
        with col2:
            ja = st.number_input("Ja (Joint alteration)", min_value=0.75, max_value=20.0, value=2.0, step=0.25)
            jw = st.number_input("Jw (Water reduction)", min_value=0.05, max_value=1.0, value=1.0, step=0.05)
            srf = st.number_input("SRF (Stress reduction)", min_value=0.5, max_value=20.0, value=1.0, step=0.5)
        
        if st.button("Calculate Q-Value", type="primary"):
            try:
                q_value = st.session_state.calculations.calculate_q_value(rqd, jn, jr, ja, jw, srf)
                interpretation = st.session_state.calculations.interpret_q_value(q_value)
                
                st.success(f"✅ Q-Value calculated successfully!")
                
                # Display result prominently
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Q-Value", f"{q_value:.3f}")
                with col2:
                    st.metric("Rock Mass Quality", interpretation)
                
                # Display calculation breakdown
                with st.expander("📊 Calculation Breakdown", expanded=True):
                    st.latex(f"Q = \\frac{{{rqd}}}{{{jn}}} \\times \\frac{{{jr}}}{{{ja}}} \\times \\frac{{{jw}}}{{{srf}}}")
                    st.latex(f"Q = {rqd/jn:.2f} \\times {jr/ja:.2f} \\times {jw/srf:.2f} = {q_value:.3f}")
                
            except Exception as e:
                st.error(f"❌ Calculation failed: {str(e)}")
    
    elif calc_type == "Q-Value Bulk Calculation":
        st.subheader("📊 Q-Value Bulk Calculation")
        st.markdown("Calculate Q-values for multiple rows from a data table.")
        
        # Check for suitable tables
        suitable_tables = [name for name in st.session_state.tables.keys()]
        
        if suitable_tables:
            selected_table = st.selectbox("Select Table", suitable_tables)
            df = st.session_state.tables[selected_table]
            
            st.markdown("**Column Mapping:**")
            st.info("Map the columns in your table to Q-system parameters")
            
            col1, col2 = st.columns(2)
            
            with col1:
                rqd_col = st.selectbox("RQD Column", df.columns, index=0 if 'RQD' in df.columns else 0)
                jn_col = st.selectbox("Jn Column", df.columns, index=0 if 'Jn' in df.columns else 0)
                jr_col = st.selectbox("Jr Column", df.columns, index=0 if 'Jr' in df.columns else 0)
            
            with col2:
                ja_col = st.selectbox("Ja Column", df.columns, index=0 if 'Ja' in df.columns else 0)
                jw_col = st.selectbox("Jw Column", df.columns, index=0 if 'Jw' in df.columns else 0)
                srf_col = st.selectbox("SRF Column", df.columns, index=0 if 'SRF' in df.columns else 0)
            
            if st.button("Calculate Q-Values", type="primary"):
                try:
                    with st.spinner("Calculating Q-values..."):
                        result_df = st.session_state.calculations.calculate_q_values_bulk(
                            df,
                            rqd_col=rqd_col,
                            jn_col=jn_col,
                            jr_col=jr_col,
                            ja_col=ja_col,
                            jw_col=jw_col,
                            srf_col=srf_col
                        )
                        
                        st.success("✅ Q-values calculated successfully!")
                        st.dataframe(result_df, use_container_width=True, height=400)
                        
                        # Statistics
                        valid_q = result_df['Q_VALUE'].dropna()
                        if len(valid_q) > 0:
                            st.markdown("**Q-Value Statistics:**")
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Count", len(valid_q))
                            with col2:
                                st.metric("Mean", f"{valid_q.mean():.2f}")
                            with col3:
                                st.metric("Min", f"{valid_q.min():.2f}")
                            with col4:
                                st.metric("Max", f"{valid_q.max():.2f}")
                        
                        # Download option
                        csv = result_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results (CSV)",
                            data=csv,
                            file_name="q_values_calculated.csv",
                            mime="text/csv"
                        )
                
                except Exception as e:
                    st.error(f"❌ Calculation failed: {str(e)}")
        else:
            st.warning("⚠️ No data tables available for bulk calculation.")


def main():
    """Main application."""
    initialize_session_state()
    display_header()
    sidebar_info()
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📤 Upload & Process", 
        "✅ Validation", 
        "📊 Data Tables",
        "🧮 Geotechnical Calculations",
        "📥 Export"
    ])
    
    with tab1:
        st.header("Upload AGS Files")
        
        uploaded_files = st.file_uploader(
            "Choose AGS file(s)",
            type=['ags'],
            accept_multiple_files=True,
            help="Upload one or more AGS files (AGS3 or AGS4 format)"
        )
        
        if uploaded_files:
            st.info(f"📁 {len(uploaded_files)} file(s) uploaded")
            
            if st.button("🔄 Process Files", type="primary"):
                process_uploaded_files(uploaded_files)
                st.success("✅ Files processed successfully!")
                st.rerun()
        
        # Display summary if files are processed
        if st.session_state.processed_files:
            st.markdown("---")
            st.header("📈 File Summary")
            display_file_summary()
            
            # Display errors if any
            errors = st.session_state.processor.get_errors()
            if errors:
                with st.expander("⚠️ Processing Warnings/Errors", expanded=False):
                    for source, error_list in errors.items():
                        st.markdown(f"**{source}:**")
                        for error in error_list:
                            st.warning(error)
    
    with tab2:
        st.header("Validation Results")
        if uploaded_files:
            display_validation_results(uploaded_files)
        else:
            st.info("Please upload AGS files in the 'Upload & Process' tab first.")
    
    with tab3:
        st.header("Data Tables")
        display_tables()
    
    with tab4:
        st.header("Geotechnical Calculations")
        display_geotechnical_calculations()
    
    with tab5:
        st.header("Export Data")
        export_data()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        AGS Processor v0.1.0 | Built with Streamlit | 
        Supports AGS3 and AGS4 formats
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
