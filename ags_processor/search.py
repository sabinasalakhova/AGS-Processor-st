"""
Search and Query Functions

Search functions from AGS-Processor for keyword, soil type, and depth queries.
"""

import pandas as pd
import numpy as np


def search_keyword(df_in, keyword_list):
    """
    Search for keywords in GEOL_DESC and Details columns.
    
    Parameters
    ----------
    df_in : pd.DataFrame
        Input dataframe with geological data
    keyword_list : list
        List of keywords to search for
    
    Returns
    -------
    pd.DataFrame
        Dataframe with additional boolean columns for each keyword
    """
    df = df_in.copy()
    
    # Check required columns
    if 'GEOL_DESC' not in df.columns or 'Details' not in df.columns:
        raise ValueError("Input file must contain 'GEOL_DESC' and 'Details' columns")
    
    NR_text = 'no recovery'
    
    for kw in keyword_list:
        if kw.casefold() == NR_text.casefold():
            # Special handling for "no recovery"
            if 'FI' in df.columns:
                df['No Recovery'] = (
                    df['GEOL_DESC'].str.contains(kw, case=False, na=False) | 
                    df['Details'].str.contains(kw, case=False, na=False) | 
                    (df['FI'].str.contains('N', na=False) & df['FI'].str.contains('R', na=False))
                )
            else:
                df['No Recovery'] = (
                    df['GEOL_DESC'].str.contains(kw, case=False, na=False) | 
                    df['Details'].str.contains(kw, case=False, na=False)
                )
        else:
            df[str(kw)] = (
                df['GEOL_DESC'].str.contains(kw, case=False, na=False) | 
                df['Details'].str.contains(kw, case=False, na=False)
            )
    
    return df


def match_soil_types(df_in, soil_type_list, grain_size_list):
    """
    Match soil types and grain sizes from geological descriptions.
    
    Parameters
    ----------
    df_in : pd.DataFrame
        Input dataframe with geological data
    soil_type_list : list
        List of soil types to match
    grain_size_list : list
        List of grain sizes to match
    
    Returns
    -------
    pd.DataFrame
        Dataframe with additional columns for soil type and grain size matching
    """
    df = df_in.copy()
    
    # Check required columns
    required_cols = ['GEOL_DESC', 'GEOL', 'Details', 'WETH']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Input file must contain columns: {', '.join(missing_cols)}")
    
    df['Soil Type/Grain Size'] = np.nan
    df['Grain Size'] = np.nan
    df['Soil Type'] = np.nan
    
    # Match soil types
    for st in soil_type_list:
        if st == 'IV' or st == 'V':
            df.loc[df['WETH'].str.contains(str(st), case=True, na=False), 'Soil Type'] = str(st)
        elif st == 'VI (RESIDUAL SOIL)':
            df.loc[
                (df['WETH'].str.contains('VI', case=True, na=False) | 
                 df['GEOL_DESC'].str.contains('RESIDUAL SOIL', case=True, na=False)), 
                'Soil Type'
            ] = 'VI'
        elif st == 'TOPSOIL':
            df.loc[
                (df['GEOL_DESC'].str.contains('TOPSOIL', case=True, na=False) | 
                 df['GEOL'].str.contains('TOPSOIL', case=True, na=False) | 
                 df['GEOL_DESC'].str.contains('TOP SOIL', case=True, na=False) | 
                 df['GEOL'].str.contains('TOP SOIL', case=True, na=False)), 
                'Soil Type'
            ] = 'TS'
        elif st == 'MARINE DEPOSIT':
            df.loc[
                (df['GEOL_DESC'].str.contains('MARINE DEPOSIT', case=True, na=False) | 
                 df['GEOL'].str.contains('MARINE', case=True, na=False)), 
                'Soil Type'
            ] = 'MD'
        elif st == 'ALLUVIUM':
            df.loc[
                (df['GEOL_DESC'].str.contains('ALLUVIUM', case=True, na=False) | 
                 df['GEOL'].str.contains('ALL', case=True, na=False)), 
                'Soil Type'
            ] = 'ALL'
        elif st == 'COLLUVIUM':
            df.loc[
                (df['GEOL_DESC'].str.contains('COLLUVIUM', case=True, na=False) | 
                 df['GEOL'].str.contains('COLL', case=True, na=False)), 
                'Soil Type'
            ] = 'COLL'
        elif st == 'ESTUARINE DEPOSIT':
            df.loc[
                (df['GEOL_DESC'].str.contains('ESTUARINE DEPOSIT', case=True, na=False) | 
                 df['GEOL'].str.contains('EST', case=True, na=False)), 
                'Soil Type'
            ] = 'ED'
        elif st == 'FILL':
            df.loc[
                (df['GEOL_DESC'].str.contains('FILL', case=True, na=False) | 
                 df['GEOL'].str.contains('FILL', case=True, na=False)), 
                'Soil Type'
            ] = 'FILL'
        else:
            df.loc[
                (df['GEOL_DESC'].str.contains(str(st), case=True, na=False) | 
                 df['GEOL'].str.contains(str(st), case=True, na=False)), 
                'Soil Type'
            ] = str(st)
    
    # Match grain sizes - create individual columns first
    grain_cols = []
    for gs in grain_size_list:
        if gs == 'CLAY':
            col_name = 'Clay'
            df.loc[
                ((df['GEOL_DESC'].str.contains('CLAY', case=True, na=False) | 
                  df['GEOL'].str.contains('CLAY', case=True, na=False) | 
                  df['Details'].str.contains('CLAY', case=True, na=False)) & 
                 df['Grain Size'].isna()), 
                col_name
            ] = 'c'
            grain_cols.append(col_name)
        elif gs == 'FINE':
            col_name = 'Fine'
            df.loc[
                ((df['GEOL_DESC'].str.contains('SILT/CLAY', case=True, na=False) | 
                  df['GEOL'].str.contains('FINE', case=True, na=False) | 
                  df['Details'].str.contains('FINE', case=True, na=False)) & 
                 df['Grain Size'].isna()), 
                col_name
            ] = 'c/z'
            grain_cols.append(col_name)
        elif gs == 'SILT':
            col_name = 'Silt'
            df.loc[
                ((df['GEOL_DESC'].str.contains('SILT', case=True, na=False) | 
                  df['GEOL'].str.contains('SILT', case=True, na=False) | 
                  df['Details'].str.contains('SILT', case=True, na=False)) & 
                 df['Grain Size'].isna()), 
                col_name
            ] = 'z'
            grain_cols.append(col_name)
        elif gs == 'SAND':
            col_name = 'Sand'
            df.loc[
                ((df['GEOL_DESC'].str.contains('SAND', case=True, na=False) | 
                  df['GEOL'].str.contains('SAND', case=True, na=False) | 
                  df['Details'].str.contains('SAND', case=True, na=False)) & 
                 df['Grain Size'].isna()), 
                col_name
            ] = 's'
            grain_cols.append(col_name)
        elif gs == 'GRAVEL':
            col_name = 'Gravel'
            df.loc[
                ((df['GEOL_DESC'].str.contains('GRAV', case=True, na=False) | 
                  df['GEOL'].str.contains('GRAV', case=True, na=False) | 
                  df['Details'].str.contains('GRAV', case=True, na=False)) & 
                 df['Grain Size'].isna()), 
                col_name
            ] = 'g'
            grain_cols.append(col_name)
        elif gs == 'COBBLE':
            col_name = 'Cobble'
            df.loc[
                ((df['GEOL_DESC'].str.contains('COBBLE', case=True, na=False) | 
                  df['GEOL'].str.contains('CBBL', case=True, na=False) | 
                  df['Details'].str.contains('COBBLE', case=True, na=False)) & 
                 df['Grain Size'].isna()), 
                col_name
            ] = 'cb'
            grain_cols.append(col_name)
        elif gs == 'BOULDER':
            col_name = 'Boulder'
            df.loc[
                ((df['GEOL_DESC'].str.contains('BOULDER', case=True, na=False) | 
                  df['GEOL'].str.contains('BLDR', case=True, na=False) | 
                  df['Details'].str.contains('BOULDER', case=True, na=False)) & 
                 df['Grain Size'].isna()), 
                col_name
            ] = 'bd'
            grain_cols.append(col_name)
        else:
            col_name = str(gs)
            df.loc[
                ((df['GEOL_DESC'].str.contains(str(gs), case=True, na=False) | 
                  df['GEOL'].str.contains(str(gs), case=True, na=False) | 
                  df['Details'].str.contains(str(gs), case=True, na=False)) & 
                 df['Grain Size'].isna()), 
                col_name
            ] = str(gs)
            grain_cols.append(col_name)
    
    # Combine grain size columns
    if grain_cols:
        # Only use columns that exist
        existing_grain_cols = [col for col in grain_cols if col in df.columns]
        if existing_grain_cols:
            df_gs = df[existing_grain_cols]
            df['Grain Size'] = df_gs.stack().groupby(level=0).apply(lambda x: ','.join(x))
    
    # Create final combined column
    df['Soil Type/Grain Size'] = df['Soil Type'].astype(str) + '-' + df['Grain Size'].astype(str)
    
    # Clean up
    if 'Unnamed: 0' in df.columns:
        df = df.drop('Unnamed: 0', axis=1)
    df = df.drop('Soil Type', axis=1)
    df = df.drop('Grain Size', axis=1)
    
    return df


def search_depth(df_data, df_depth, is_single_depth=True):
    """
    Extract data at specific depths or depth ranges.
    
    Parameters
    ----------
    df_data : pd.DataFrame
        Combined AGS data
    df_depth : pd.DataFrame
        Depth query data with GIU_HOLE_ID and DEPTH or DEPTH_FROM/DEPTH_TO
    is_single_depth : bool
        True for single depth points, False for depth ranges
    
    Returns
    -------
    pd.DataFrame
        Extracted data at specified depths
    """
    # Check required columns in data
    required_data_cols = ['GIU_HOLE_ID', 'DEPTH_FROM', 'DEPTH_TO']
    for col in required_data_cols:
        if col not in df_data.columns:
            raise ValueError(f"Combined data must contain '{col}' column")
    
    # Check required columns in depth query
    if is_single_depth:
        if 'GIU_HOLE_ID' not in df_depth.columns or 'DEPTH' not in df_depth.columns:
            raise ValueError("Depth query must contain 'GIU_HOLE_ID' and 'DEPTH' columns")
    else:
        required_depth_cols = ['GIU_HOLE_ID', 'DEPTH_FROM', 'DEPTH_TO']
        for col in required_depth_cols:
            if col not in df_depth.columns:
                raise ValueError(f"Depth query must contain '{col}' column")
    
    # Prepare result dataframe
    result_rows = []
    
    for idx, row in df_depth.iterrows():
        hole_id = row['GIU_HOLE_ID']
        
        # Filter data for this borehole
        hole_data = df_data[df_data['GIU_HOLE_ID'] == hole_id]
        
        if is_single_depth:
            depth = row['DEPTH']
            # Find intervals containing this depth
            matching = hole_data[
                (hole_data['DEPTH_FROM'] <= depth) & 
                (hole_data['DEPTH_TO'] > depth)
            ]
        else:
            depth_from = row['DEPTH_FROM']
            depth_to = row['DEPTH_TO']
            # Find intervals overlapping with this range
            matching = hole_data[
                ~((hole_data['DEPTH_TO'] <= depth_from) | 
                  (hole_data['DEPTH_FROM'] >= depth_to))
            ]
        
        # Add query information to results
        for _, match_row in matching.iterrows():
            result_row = row.to_dict()
            result_row.update(match_row.to_dict())
            result_rows.append(result_row)
    
    result_df = pd.DataFrame(result_rows)
    return result_df
