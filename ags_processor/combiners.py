"""
AGS File Combination Functions

Functions for combining and concatenating multiple AGS files.
Includes concat_ags_files and combine_ags_data from AGS-Processor.
"""

import pandas as pd
import numpy as np
from typing import List


def concat_ags_files(uploaded_files, giu_number):
    """
    Concatenate multiple AGS files into Excel-friendly DataFrames.

    Ensures each file gets a unique GIU_NO (giu_number suffixed by file index),
    and that GIU_NO is only applied to rows coming from that file. If a group
    has HOLE_ID, a GIU_HOLE_ID column is added by concatenating the per-file
    GIU_NO with that row's HOLE_ID.

    Parameters
    ----------
    uploaded_files : list
        List of uploaded AGS file objects
    giu_number : str
        Base GIU reference string

    Returns
    -------
    dict
        Dictionary of dataframes, one per group, merged across files.
    """
    from .processor import AGS4_to_dataframe
    
    combined = {}

    for idx, file in enumerate(uploaded_files):
        per_file_giu = f"{giu_number}_{idx+1}"
        df_dict, headings = AGS4_to_dataframe(file)

        for group_name, df in df_dict.items():
            if df is None or df.empty:
                continue
            temp = df.copy()
            temp["GIU_NO"] = per_file_giu
            temp["AGS_FILE"] = getattr(file, "name", "")
            if "HOLE_ID" in temp.columns:
                temp["GIU_HOLE_ID"] = temp["GIU_NO"].astype(str) + "_" + temp["HOLE_ID"].astype(str)
            combined.setdefault(group_name, []).append(temp)

    return {g: pd.concat(dfs, ignore_index=True) for g, dfs in combined.items()}


def combine_ags_data(uploaded_excel_files, selected_groups=None):
    """
    Combine data from multiple Excel files into a single dataframe.
    
    Parameters
    ----------
    uploaded_excel_files : list
        List of uploaded Excel file objects
    selected_groups : list, optional
        List of groups to combine. If None, combines all groups.
    
    Returns
    -------
    pd.DataFrame
        Combined dataframe
    """
    if selected_groups is None or len(selected_groups) == 0:
        group_list = ['HOLE', 'CORE', 'DETL', 'WETH', 'FRAC', 'GEOL']
    else:
        group_list = ['HOLE'] + selected_groups
    
    # Initialize master dataframe
    df = pd.DataFrame(columns=[
        'GIU_HOLE_ID', 'GIU_NO', 'HOLE_ID', 'DEPTH_FROM', 'DEPTH_TO', 
        'GEOL', 'GEOL_DESC', 'THICKNESS_M', 'TCR', 'RQD', 
        'WETH_GRAD', 'WETH', 'FI', 'Details'
    ])
    
    row_index = 0
    
    for file in uploaded_excel_files:
        # Read separate sheets for each file
        group_dict = {}
        for g in group_list:
            try:
                group_dict[g] = pd.read_excel(file, sheet_name=g)
            except:
                group_dict[g] = pd.DataFrame()
        
        if 'HOLE' not in group_dict or group_dict['HOLE'].empty:
            continue
        
        GIU_HOLE_ID_list = group_dict['HOLE']['GIU_NO'].astype(str) + "_" + group_dict['HOLE']['HOLE_ID']
        
        # Process each borehole
        for bh in range(len(GIU_HOLE_ID_list)):
            GIU_NO_bh = group_dict['HOLE'].loc[bh, 'GIU_NO']
            HOLE_ID_bh = group_dict['HOLE'].loc[bh, 'HOLE_ID']
            
            # Get combined depths from all selected groups
            all_depths = []
            
            if 'CORE' in group_list and 'CORE' in group_dict:
                core_data = group_dict['CORE'][(group_dict['CORE']['HOLE_ID'] == HOLE_ID_bh) & 
                                                (group_dict['CORE']['GIU_NO'] == GIU_NO_bh)]
                if not core_data.empty and 'CORE_TOP' in core_data.columns and 'CORE_BOT' in core_data.columns:
                    all_depths.extend(list(core_data['CORE_TOP'].values))
                    all_depths.extend(list(core_data['CORE_BOT'].values))
            
            if 'DETL' in group_list and 'DETL' in group_dict:
                detl_data = group_dict['DETL'][(group_dict['DETL']['HOLE_ID'] == HOLE_ID_bh) & 
                                                (group_dict['DETL']['GIU_NO'] == GIU_NO_bh)]
                if not detl_data.empty and 'DETL_TOP' in detl_data.columns and 'DETL_BASE' in detl_data.columns:
                    all_depths.extend(list(detl_data['DETL_TOP'].values))
                    all_depths.extend(list(detl_data['DETL_BASE'].values))
            
            if 'FRAC' in group_list and 'FRAC' in group_dict:
                frac_data = group_dict['FRAC'][(group_dict['FRAC']['HOLE_ID'] == HOLE_ID_bh) & 
                                                (group_dict['FRAC']['GIU_NO'] == GIU_NO_bh)]
                if not frac_data.empty and 'FRAC_TOP' in frac_data.columns and 'FRAC_BASE' in frac_data.columns:
                    all_depths.extend(list(frac_data['FRAC_TOP'].values))
                    all_depths.extend(list(frac_data['FRAC_BASE'].values))
            
            if 'GEOL' in group_list and 'GEOL' in group_dict:
                geol_data = group_dict['GEOL'][(group_dict['GEOL']['HOLE_ID'] == HOLE_ID_bh) & 
                                                (group_dict['GEOL']['GIU_NO'] == GIU_NO_bh)]
                if not geol_data.empty and 'GEOL_TOP' in geol_data.columns and 'GEOL_BASE' in geol_data.columns:
                    all_depths.extend(list(geol_data['GEOL_TOP'].values))
                    all_depths.extend(list(geol_data['GEOL_BASE'].values))
            
            if 'WETH' in group_list and 'WETH' in group_dict:
                weth_data = group_dict['WETH'][(group_dict['WETH']['HOLE_ID'] == HOLE_ID_bh) & 
                                                (group_dict['WETH']['GIU_NO'] == GIU_NO_bh)]
                if not weth_data.empty and 'WETH_TOP' in weth_data.columns and 'WETH_BASE' in weth_data.columns:
                    all_depths.extend(list(weth_data['WETH_TOP'].values))
                    all_depths.extend(list(weth_data['WETH_BASE'].values))
            
            # Create unique sorted depths
            depths = list(set(all_depths))
            depths.sort()
            depth = [x for x in depths if str(x) != 'nan']
            depth.sort()
            
            if len(depth) < 2:
                continue
            
            depth_from = depth[0:-1]
            depth_to = depth[1:]
            
            # Fill in the dataframe
            for d in range(len(depth_to)):
                df.loc[row_index, 'GIU_HOLE_ID'] = GIU_HOLE_ID_list[bh]
                df.loc[row_index, 'GIU_NO'] = GIU_NO_bh
                df.loc[row_index, 'HOLE_ID'] = HOLE_ID_bh
                df.loc[row_index, 'DEPTH_FROM'] = depth_from[d]
                df.loc[row_index, 'DEPTH_TO'] = depth_to[d]
                df.loc[row_index, 'THICKNESS_M'] = depth_to[d] - depth_from[d]
                row_index += 1
            
            # Fill from CORE sheet
            if 'CORE' in group_list and 'CORE' in group_dict:
                core = group_dict['CORE'][(group_dict['CORE']['HOLE_ID'] == HOLE_ID_bh) & 
                                          (group_dict['CORE']['GIU_NO'] == GIU_NO_bh)]
                for c in range(len(core)):
                    if 'CORE_TOP' in core.columns and 'CORE_BOT' in core.columns:
                        mask = (df.HOLE_ID == HOLE_ID_bh) & (df.GIU_NO == GIU_NO_bh) & \
                               (df.DEPTH_FROM.between(core.iloc[c]['CORE_TOP'], 
                                                     core.iloc[c]['CORE_BOT'], inclusive='left'))
                        if 'CORE_RQD' in core.columns:
                            df.loc[mask, 'RQD'] = core.iloc[c]['CORE_RQD']
                        if 'CORE_PREC' in core.columns:
                            df.loc[mask, 'TCR'] = core.iloc[c]['CORE_PREC']
            
            # Fill from DETL sheet
            if 'DETL' in group_list and 'DETL' in group_dict:
                detl = group_dict['DETL'][(group_dict['DETL']['HOLE_ID'] == HOLE_ID_bh) & 
                                          (group_dict['DETL']['GIU_NO'] == GIU_NO_bh)]
                for d in range(len(detl)):
                    if 'DETL_TOP' in detl.columns and 'DETL_BASE' in detl.columns and 'DETL_DESC' in detl.columns:
                        mask = (df.HOLE_ID == HOLE_ID_bh) & (df.GIU_NO == GIU_NO_bh) & \
                               (df.DEPTH_FROM.between(detl.iloc[d]['DETL_TOP'], 
                                                     detl.iloc[d]['DETL_BASE'], inclusive='left'))
                        df.loc[mask, 'Details'] = detl.iloc[d]['DETL_DESC']
            
            # Fill from FRAC sheet
            if 'FRAC' in group_list and 'FRAC' in group_dict:
                frac = group_dict['FRAC'][(group_dict['FRAC']['HOLE_ID'] == HOLE_ID_bh) & 
                                          (group_dict['FRAC']['GIU_NO'] == GIU_NO_bh)]
                for fr in range(len(frac)):
                    if 'FRAC_TOP' in frac.columns and 'FRAC_BASE' in frac.columns and 'FRAC_FI' in frac.columns:
                        mask = (df.HOLE_ID == HOLE_ID_bh) & (df.GIU_NO == GIU_NO_bh) & \
                               (df.DEPTH_FROM.between(frac.iloc[fr]['FRAC_TOP'], 
                                                     frac.iloc[fr]['FRAC_BASE'], inclusive='left'))
                        df.loc[mask, 'FI'] = frac.iloc[fr]['FRAC_FI']
            
            # Fill from GEOL sheet
            if 'GEOL' in group_list and 'GEOL' in group_dict:
                geol = group_dict['GEOL'][(group_dict['GEOL']['HOLE_ID'] == HOLE_ID_bh) & 
                                          (group_dict['GEOL']['GIU_NO'] == GIU_NO_bh)]
                for g in range(len(geol)):
                    if 'GEOL_TOP' in geol.columns and 'GEOL_BASE' in geol.columns:
                        mask = (df.HOLE_ID == HOLE_ID_bh) & (df.GIU_NO == GIU_NO_bh) & \
                               (df.DEPTH_FROM.between(geol.iloc[g]['GEOL_TOP'], 
                                                     geol.iloc[g]['GEOL_BASE'], inclusive='left'))
                        if 'GEOL_LEG' in geol.columns:
                            df.loc[mask, 'GEOL'] = geol.iloc[g]['GEOL_LEG']
                        if 'GEOL_DESC' in geol.columns:
                            df.loc[mask, 'GEOL_DESC'] = geol.iloc[g]['GEOL_DESC']
            
            # Fill from WETH sheet
            if 'WETH' in group_list and 'WETH' in group_dict:
                weth = group_dict['WETH'][(group_dict['WETH']['HOLE_ID'] == HOLE_ID_bh) & 
                                          (group_dict['WETH']['GIU_NO'] == GIU_NO_bh)]
                for w in range(len(weth)):
                    if 'WETH_TOP' in weth.columns and 'WETH_BASE' in weth.columns and 'WETH_GRAD' in weth.columns:
                        mask = (df.HOLE_ID == HOLE_ID_bh) & (df.GIU_NO == GIU_NO_bh) & \
                               (df.DEPTH_FROM.between(weth.iloc[w]['WETH_TOP'], 
                                                     weth.iloc[w]['WETH_BASE'], inclusive='left'))
                        df.loc[mask, 'WETH_GRAD'] = weth.iloc[w]['WETH_GRAD']
                
                # Simplify weathering grades
                df['WETH'] = df['WETH_GRAD']
                df.loc[(df.WETH_GRAD == 'I/II') | (df.WETH_GRAD == 'II/I'), 'WETH'] = 'II'
                df.loc[(df.WETH_GRAD == 'II/III') | (df.WETH_GRAD == 'III/II'), 'WETH'] = 'III'
                df.loc[(df.WETH_GRAD == 'III/IV') | (df.WETH_GRAD == 'IV/III') | 
                       (df.WETH_GRAD.str.contains('III', na=False) & df.WETH_GRAD.str.contains('IV', na=False)), 'WETH'] = 'IV'
                df.loc[(df.WETH_GRAD == 'IV/V') | (df.WETH_GRAD == 'V/IV'), 'WETH'] = 'V'
                df.loc[(df.WETH_GRAD == 'V/VI') | (df.WETH_GRAD == 'VI/V'), 'WETH'] = 'VI'
    
    return df


def weth_grade_to_numeric(df):
    """
    Convert weathering grade to numeric values.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with WETH_GRAD column
    
    Returns
    -------
    pd.DataFrame
        Dataframe with additional WETH_GRAD_NUM column
    """
    df = df.copy()
    
    if 'WETH_GRAD' not in df.columns:
        raise ValueError("Dataframe must contain 'WETH_GRAD' column")
    
    # Initialize numeric column
    df['WETH_GRAD_NUM'] = np.nan
    
    # Map weathering grades to numeric values
    grade_map = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6,
        'I/II': 1.5, 'II/I': 1.5,
        'II/III': 2.5, 'III/II': 2.5,
        'III/IV': 3.5, 'IV/III': 3.5,
        'IV/V': 4.5, 'V/IV': 4.5,
        'V/VI': 5.5, 'VI/V': 5.5
    }
    
    for grade, num in grade_map.items():
        df.loc[df['WETH_GRAD'] == grade, 'WETH_GRAD_NUM'] = num
    
    return df


def rock_material_criteria(df, include_weak_zones=False):
    """
    Determine if material in logged interval meets rock material criteria.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with geological data
    include_weak_zones : bool
        If True, includes moderately weak and weak zones
    
    Returns
    -------
    pd.DataFrame
        Dataframe with additional 'rock_mat' boolean column
    """
    sub_df = df.copy()
    
    # Initialize indicator columns if they don't exist
    if 'Mod_Weak' not in sub_df.columns:
        sub_df['Mod_Weak'] = False
    if 'Weak' not in sub_df.columns:
        sub_df['Weak'] = False
    if 'NR' not in sub_df.columns:
        sub_df['NR'] = False
    
    # Convert to boolean
    sub_df['Mod_Weak'] = sub_df['Mod_Weak'] == 1
    sub_df['Weak'] = sub_df['Weak'] == 1
    sub_df['NR'] = sub_df['NR'] == 1
    
    # Check for no recovery indicators
    if 'FI' in sub_df.columns:
        sub_df['NR'] = sub_df['NR'] | sub_df['FI'].str.contains('NR', na=False) | sub_df['FI'].str.contains('N.R.', na=False)
    
    # Determine rock material
    if include_weak_zones:
        sub_df['rock_mat'] = (
            (sub_df['WETH_GRAD_NUM'] <= 3) & 
            (sub_df['WETH_GRAD'] != 'NI') &
            (~sub_df['NR'])
        )
    else:
        sub_df['rock_mat'] = (
            (sub_df['WETH_GRAD_NUM'] <= 3) & 
            (sub_df['WETH_GRAD'] != 'NI') &
            (~sub_df['Mod_Weak']) & 
            (~sub_df['Weak']) &
            (~sub_df['NR'])
        )
    
    return sub_df


def calculate_rockhead(df, core_run=1.0, tcr_threshold=85, continuous_length=5, include_weak=False):
    """
    Calculate rockhead depth based on weathering grade and TCR criteria.
    
    Parameters
    ----------
    df : pd.DataFrame
        Combined geological data with HOLE_ID, DEPTH_FROM, DEPTH_TO, WETH_GRAD, TCR
    core_run : float
        Core run length in meters (default: 1.0)
    tcr_threshold : float
        TCR threshold percentage (default: 85)
    continuous_length : float
        Required continuous length of rock material in meters (default: 5)
    include_weak : bool
        Include weak zones in rock material (default: False)
    
    Returns
    -------
    dict
        Dictionary with 'summary' DataFrame and 'rockhead_depths' dict by HOLE_ID
    """
    df = df.copy()
    
    # Convert weathering grades to numeric
    df = weth_grade_to_numeric(df)
    
    # Apply rock material criteria
    df = rock_material_criteria(df, include_weak_zones=include_weak)
    
    # Calculate rock_TCR (rock material AND TCR >= threshold)
    if 'TCR' in df.columns:
        df['rock_TCR'] = df['rock_mat'] & (pd.to_numeric(df['TCR'], errors='coerce') >= tcr_threshold)
    else:
        df['rock_TCR'] = df['rock_mat']
    
    # Find rockhead for each borehole
    rockhead_depths = {}
    
    if 'HOLE_ID' in df.columns:
        hole_ids = df['HOLE_ID'].unique()
    elif 'GIU_HOLE_ID' in df.columns:
        hole_ids = df['GIU_HOLE_ID'].unique()
    else:
        raise ValueError("DataFrame must contain 'HOLE_ID' or 'GIU_HOLE_ID' column")
    
    for hole_id in hole_ids:
        hole_data = df[df['HOLE_ID'] == hole_id] if 'HOLE_ID' in df.columns else df[df['GIU_HOLE_ID'] == hole_id]
        hole_data = hole_data.sort_values('DEPTH_FROM')
        
        # Find first occurrence of continuous rock material
        rockhead_depth = None
        current_run_start = None
        current_run_length = 0
        
        for idx, row in hole_data.iterrows():
            if row['rock_TCR']:
                if current_run_start is None:
                    current_run_start = row['DEPTH_FROM']
                    current_run_length = row['DEPTH_TO'] - row['DEPTH_FROM']
                else:
                    current_run_length += row['DEPTH_TO'] - row['DEPTH_FROM']
                
                # Check if we've met the continuous length criteria
                if current_run_length >= continuous_length:
                    rockhead_depth = current_run_start
                    break
            else:
                # Reset if rock material is interrupted
                current_run_start = None
                current_run_length = 0
        
        rockhead_depths[hole_id] = rockhead_depth if rockhead_depth is not None else 'Not Found'
    
    # Create summary dataframe
    summary_df = pd.DataFrame([
        {'HOLE_ID': hole_id, 'Rockhead_Depth': depth}
        for hole_id, depth in rockhead_depths.items()
    ])
    
    return {
        'summary': summary_df,
        'rockhead_depths': rockhead_depths,
        'detailed_data': df
    }


def calculate_q_value(df, rqd_col='RQD', jn=9, jr=1, ja=1, jw=1, srf=1):
    """
    Calculate Q-value for rock mass classification.
    
    Q = (RQD/Jn) × (Jr/Ja) × (Jw/SRF)
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with RQD data
    rqd_col : str
        Name of RQD column (default: 'RQD')
    jn : float
        Joint set number (default: 9)
    jr : float
        Joint roughness number (default: 1)
    ja : float
        Joint alteration number (default: 1)
    jw : float
        Joint water reduction factor (default: 1)
    srf : float
        Stress reduction factor (default: 1)
    
    Returns
    -------
    pd.DataFrame
        Dataframe with additional Q_value column
    """
    df = df.copy()
    
    if rqd_col not in df.columns:
        raise ValueError(f"DataFrame must contain '{rqd_col}' column")
    
    # Convert RQD to numeric
    df['RQD_numeric'] = pd.to_numeric(df[rqd_col], errors='coerce')
    
    # Calculate Q-value
    df['Q_value'] = (df['RQD_numeric'] / jn) * (jr / ja) * (jw / srf)
    
    # Classify rock mass quality based on Q-value
    df['Rock_Quality'] = 'Unknown'
    df.loc[df['Q_value'] < 0.01, 'Rock_Quality'] = 'Exceptionally Poor'
    df.loc[(df['Q_value'] >= 0.01) & (df['Q_value'] < 0.1), 'Rock_Quality'] = 'Extremely Poor'
    df.loc[(df['Q_value'] >= 0.1) & (df['Q_value'] < 1), 'Rock_Quality'] = 'Very Poor'
    df.loc[(df['Q_value'] >= 1) & (df['Q_value'] < 4), 'Rock_Quality'] = 'Poor'
    df.loc[(df['Q_value'] >= 4) & (df['Q_value'] < 10), 'Rock_Quality'] = 'Fair'
    df.loc[(df['Q_value'] >= 10) & (df['Q_value'] < 40), 'Rock_Quality'] = 'Good'
    df.loc[(df['Q_value'] >= 40) & (df['Q_value'] < 100), 'Rock_Quality'] = 'Very Good'
    df.loc[(df['Q_value'] >= 100) & (df['Q_value'] < 400), 'Rock_Quality'] = 'Extremely Good'
    df.loc[df['Q_value'] >= 400, 'Rock_Quality'] = 'Exceptionally Good'
    
    return df
