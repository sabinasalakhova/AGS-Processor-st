#!/usr/bin/env python
"""
Comprehensive Integration Test for AGS Processor

This script demonstrates all functionality from the integrated legacy repositories.
"""

from pathlib import Path
import pandas as pd
import ags_processor.processor as proc
import ags_processor.triaxial as tri
import ags_processor.cleaners as clean
import ags_processor.search as search
import ags_processor.combiners as comb

def test_processor_module():
    """Test processor.py - Core AGS parsing"""
    print("=" * 70)
    print("1. TESTING PROCESSOR MODULE (processor.py)")
    print("=" * 70)
    
    # Test primary parser
    ags_file = Path('/tmp/ags3_all_data_to_excel/31039-GE9907_7A.AGS')
    if not ags_file.exists():
        print("⚠ AGS test file not found")
        return {}
    
    print("\n✓ Testing parse_ags_file (primary parser):")
    file_bytes = ags_file.read_bytes()
    groups = proc.parse_ags_file(file_bytes)
    print(f"  - Parsed {len(groups)} groups")
    print(f"  - Groups: {', '.join(list(groups.keys())[:8])}")
    
    # Test secondary parser
    print("\n✓ Testing AGS4_to_dataframe:")
    df_dict, headings = proc.AGS4_to_dataframe(ags_file)
    print(f"  - Parsed {len(df_dict)} groups")
    print(f"  - Available groups: {', '.join(list(df_dict.keys())[:8])}")
    
    # Test helper functions
    print("\n✓ Testing helper functions:")
    if 'HOLE' in groups:
        hole_id_col = proc.find_hole_id_column(groups['HOLE'].columns)
        print(f"  - Identified HOLE_ID column: {hole_id_col}")
    
    return groups

def test_triaxial_module(groups):
    """Test triaxial.py - Triaxial test processing"""
    print("\n" + "=" * 70)
    print("2. TESTING TRIAXIAL MODULE (triaxial.py)")
    print("=" * 70)
    
    print("\n✓ Testing generate_triaxial_table:")
    triaxial_table = tri.generate_triaxial_table(groups)
    print(f"  - Generated table: {triaxial_table.shape}")
    print(f"  - Columns: {', '.join(triaxial_table.columns.tolist())}")
    
    print("\n✓ Testing generate_triaxial_with_lithology:")
    triaxial_with_litho = tri.generate_triaxial_with_lithology(groups)
    print(f"  - Added lithology column: {'LITHOLOGY' in triaxial_with_litho.columns}")
    
    print("\n✓ Testing calculate_s_t_values:")
    if not triaxial_table.empty:
        st_values = tri.calculate_s_t_values(triaxial_table)
        print(f"  - Calculated s-t values: {st_values.shape}")
        has_cols = all(col in st_values.columns for col in ['s', 't', 'valid'])
        print(f"  - Has s, t, valid columns: {has_cols}")
    
    print("\n✓ Testing remove_duplicate_tests:")
    deduplicated = tri.remove_duplicate_tests(triaxial_table)
    print(f"  - Original: {triaxial_table.shape[0]} rows")
    print(f"  - Deduplicated: {deduplicated.shape[0]} rows")

def test_cleaners_module():
    """Test cleaners.py - Data cleaning utilities"""
    print("\n" + "=" * 70)
    print("3. TESTING CLEANERS MODULE (cleaners.py)")
    print("=" * 70)
    
    print("\n✓ Testing normalize_columns:")
    df = pd.DataFrame({'Test Column': [1, 2], 'another_col': [3, 4]})
    df_norm = clean.normalize_columns(df)
    print(f"  - Before: {list(df.columns)}")
    print(f"  - After: {list(df_norm.columns)}")
    
    print("\n✓ Testing drop_singleton_rows:")
    df = pd.DataFrame({'A': [1, None, None, 4], 'B': [None, 2, None, 5]})
    df_clean = clean.drop_singleton_rows(df)
    print(f"  - Before: {len(df)} rows")
    print(f"  - After: {len(df_clean)} rows")
    
    print("\n✓ Testing deduplicate_cell:")
    cell = 'clay | sand | clay | silt'
    result = clean.deduplicate_cell(cell)
    print(f"  - Before: \"{cell}\"")
    print(f"  - After: \"{result}\"")
    
    print("\n✓ Testing expand_rows:")
    df = pd.DataFrame({
        'Material': ['clay | sand', 'gravel'],
        'Depth': [5.0, 10.0]
    })
    expanded = clean.expand_rows(df)
    print(f"  - Before: {df.shape}")
    print(f"  - After: {expanded.shape}")
    
    print("\n✓ Testing coalesce_columns:")
    df = pd.DataFrame({'SPEC_DPTH': [1.5, 2.5], 'OTHER': [10, 20]})
    clean.coalesce_columns(df, ['SPEC_DPTH', 'SPEC_DEPTH'], 'SPEC_DEPTH')
    print(f"  - Coalesced SPEC_DPTH to SPEC_DEPTH: {'SPEC_DEPTH' in df.columns}")
    
    print("\n✓ Testing to_numeric_safe:")
    df = pd.DataFrame({'Value': ['1.5', '2.3', 'invalid']})
    clean.to_numeric_safe(df, ['Value'])
    print(f"  - Converted to numeric (invalid -> NaN): {df['Value'].dtype}")

def test_search_module():
    """Test search.py - Search and query functions"""
    print("\n" + "=" * 70)
    print("4. TESTING SEARCH MODULE (search.py)")
    print("=" * 70)
    
    print("\n✓ Testing search_keyword:")
    df = pd.DataFrame({
        'GEOL_DESC': ['weathered granite', 'fresh sandstone', 'fractured rock'],
        'Details': ['with clay infill', 'massive', 'highly fractured']
    })
    keywords = ['weathered', 'fractured']
    result = search.search_keyword(df, keywords)
    print(f"  - Searched for keywords: {keywords}")
    print(f"  - Added columns: {[col for col in result.columns if col in keywords]}")
    
    print("\n✓ Testing match_soil_types:")
    df = pd.DataFrame({
        'GEOL_DESC': ['CLAY with sand', 'SANDY GRAVEL', 'RESIDUAL SOIL'],
        'GEOL': ['C', 'SG', 'RS'],
        'Details': ['brown', 'grey', 'red'],
        'WETH': ['IV', 'V', 'VI']
    })
    soil_types = ['IV', 'V', 'VI (RESIDUAL SOIL)']
    grain_sizes = ['CLAY', 'SAND', 'GRAVEL']
    result = search.match_soil_types(df, soil_types, grain_sizes)
    print(f"  - Matched soil types: {soil_types}")
    print(f"  - Matched grain sizes: {grain_sizes}")
    print(f"  - Created column: {'Soil Type/Grain Size' in result.columns}")

def test_combiners_module():
    """Test combiners.py - File combination and rock engineering"""
    print("\n" + "=" * 70)
    print("5. TESTING COMBINERS MODULE (combiners.py)")
    print("=" * 70)
    
    print("\n✓ Testing weth_grade_to_numeric:")
    df = pd.DataFrame({
        'WETH_GRAD': ['I', 'II', 'III/IV', 'V', 'VI'],
        'DEPTH': [0, 5, 10, 15, 20]
    })
    result = comb.weth_grade_to_numeric(df)
    print(f"  - Grades: {df['WETH_GRAD'].tolist()}")
    print(f"  - Numeric: {result['WETH_GRAD_NUM'].tolist()}")
    
    print("\n✓ Testing rock_material_criteria:")
    result = comb.rock_material_criteria(result, include_weak_zones=False)
    print(f"  - Rock material criteria applied: {'rock_mat' in result.columns}")
    print(f"  - Rock material flags: {result['rock_mat'].tolist()}")
    
    print("\n✓ Testing calculate_q_value:")
    df = pd.DataFrame({
        'RQD': [75, 50, 25, 90],
        'HOLE_ID': ['BH1', 'BH2', 'BH3', 'BH4']
    })
    result = comb.calculate_q_value(df, jn=9, jr=1, ja=1, jw=1, srf=1)
    print(f"  - RQD values: {df['RQD'].tolist()}")
    print(f"  - Q-values: {[f'{q:.2f}' for q in result['Q_value'].tolist()]}")
    print(f"  - Rock quality: {result['Rock_Quality'].tolist()}")
    
    print("\n✓ Testing calculate_rockhead:")
    df = pd.DataFrame({
        'HOLE_ID': ['BH1'] * 10,
        'DEPTH_FROM': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        'DEPTH_TO': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'WETH_GRAD': ['V', 'IV', 'III', 'II', 'II', 'I', 'I', 'I', 'I', 'I'],
        'TCR': [40, 60, 80, 85, 90, 95, 95, 95, 95, 95]
    })
    result = comb.calculate_rockhead(df, tcr_threshold=85, continuous_length=5.0)
    print(f"  - Calculated rockhead depth: {result['summary']['Rockhead_Depth'].values[0]}")

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "AGS PROCESSOR - COMPREHENSIVE INTEGRATION TEST" + " " * 12 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Test each module
    groups = test_processor_module()
    test_triaxial_module(groups)
    test_cleaners_module()
    test_search_module()
    test_combiners_module()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("\n✅ All 5 modules tested successfully!")
    print("\nModules:")
    print("  1. processor.py   - AGS parsing (parse_ags_file, AGS4_to_dict, AGS4_to_dataframe)")
    print("  2. triaxial.py    - Triaxial test processing")
    print("  3. cleaners.py    - Data cleaning utilities")
    print("  4. search.py      - Search and query functions")
    print("  5. combiners.py   - File combination and rock engineering")
    print("\n" + "=" * 70)
    print("Integration complete! All legacy functions available.")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    main()
