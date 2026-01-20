"""
Geotechnical calculation functions for AGS data.

Integrates legacy functions from AGS-Processor repository as primary implementation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


class GeotechnicalCalculations:
    """Geotechnical calculations from AGS-Processor repository."""
    
    def __init__(self):
        pass
    
    def weth_grade_to_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convert weathering grade to numeric (from AGS-Processor)."""
        df = df.copy()
        if 'WETH_GRAD' not in df.columns:
            raise ValueError("Dataframe must contain 'WETH_GRAD' column")
        
        df['WETH_GRAD_NUM'] = np.nan
        grade_map = {
            'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6,
            'I/II': 1.5, 'II/I': 1.5, 'II/III': 2.5, 'III/II': 2.5,
            'III/IV': 3.5, 'IV/III': 3.5, 'IV/V': 4.5, 'V/IV': 4.5,
            'V/VI': 5.5, 'VI/V': 5.5
        }
        for grade, num in grade_map.items():
            df.loc[df['WETH_GRAD'] == grade, 'WETH_GRAD_NUM'] = num
        return df
    
    def rock_material_criteria(self, df: pd.DataFrame, include_weak_zones: bool = False) -> pd.DataFrame:
        """Rock material criteria (from AGS-Processor)."""
        sub_df = df.copy()
        if 'Mod_Weak' not in sub_df.columns:
            sub_df['Mod_Weak'] = False
        if 'Weak' not in sub_df.columns:
            sub_df['Weak'] = False
        if 'NR' not in sub_df.columns:
            sub_df['NR'] = False
        
        sub_df['Mod_Weak'] = sub_df['Mod_Weak'] == 1
        sub_df['Weak'] = sub_df['Weak'] == 1
        sub_df['NR'] = sub_df['NR'] == 1
        
        if 'FI' in sub_df.columns:
            sub_df['NR'] = sub_df['NR'] | sub_df['FI'].str.contains('NR', na=False) | sub_df['FI'].str.contains('N.R.', na=False)
        
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
                (~sub_df['Mod_Weak']) & (~sub_df['Weak']) & (~sub_df['NR'])
            )
        return sub_df
    
    def calculate_rockhead(self, df: pd.DataFrame, core_run: float = 1.0, 
                          tcr_threshold: float = 85, continuous_length: float = 5, 
                          include_weak: bool = False) -> Dict:
        """Calculate rockhead (from AGS-Processor)."""
        df = df.copy()
        df = self.weth_grade_to_numeric(df)
        df = self.rock_material_criteria(df, include_weak_zones=include_weak)
        
        if 'TCR' in df.columns:
            df['rock_TCR'] = df['rock_mat'] & (pd.to_numeric(df['TCR'], errors='coerce') >= tcr_threshold)
        else:
            df['rock_TCR'] = df['rock_mat']
        
        rockhead_depths = {}
        
        if 'HOLE_ID' in df.columns:
            hole_id_col = 'HOLE_ID'
        elif 'GIU_HOLE_ID' in df.columns:
            hole_id_col = 'GIU_HOLE_ID'
        elif 'LOCA_ID' in df.columns:
            hole_id_col = 'LOCA_ID'
        else:
            raise ValueError("DataFrame must contain 'HOLE_ID', 'GIU_HOLE_ID', or 'LOCA_ID' column")
        
        for hole_id in df[hole_id_col].unique():
            hole_data = df[df[hole_id_col] == hole_id].sort_values('DEPTH_FROM')
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
                    
                    if current_run_length >= continuous_length:
                        rockhead_depth = current_run_start
                        break
                else:
                    current_run_start = None
                    current_run_length = 0
            
            rockhead_depths[hole_id] = rockhead_depth if rockhead_depth is not None else 'Not Found'
        
        summary_df = pd.DataFrame([
            {hole_id_col: hole_id, 'Rockhead_Depth': depth}
            for hole_id, depth in rockhead_depths.items()
        ])
        
        return {'summary': summary_df, 'rockhead_depths': rockhead_depths, 'detailed_data': df}
    
    def detect_rockhead(self, geology_df: pd.DataFrame, weathering_threshold: str = 'MODERATELY WEATHERED') -> Dict[str, float]:
        """Simple wrapper for backward compatibility."""
        if 'WETH_GRAD' in geology_df.columns and 'DEPTH_FROM' in geology_df.columns:
            result = self.calculate_rockhead(geology_df, continuous_length=1.0)
            return result['rockhead_depths']
        
        rockhead_depths = {}
        if geology_df.empty:
            return rockhead_depths
        
        required_cols = ['LOCA_ID', 'GEOL_TOP', 'GEOL_DESC']
        if not all(col in geology_df.columns for col in required_cols):
            return rockhead_depths
        
        rock_keywords = ['ROCK', 'GRANITE', 'BASALT', 'LIMESTONE', 'SANDSTONE', 'MUDSTONE',
                        'SLIGHTLY WEATHERED', 'FRESH', 'UNWEATHERED', 'MODERATELY WEATHERED']
        soil_keywords = [' SOIL', 'CLAY', 'SILT', ' SAND ', 'GRAVEL',
                        'COMPLETELY WEATHERED', 'HIGHLY WEATHERED', 'MADE GROUND', 'FILL']
        
        for loca_id, group in geology_df.groupby('LOCA_ID'):
            group = group.sort_values('GEOL_TOP')
            for idx, row in group.iterrows():
                desc = str(row.get('GEOL_DESC', '')).upper()
                is_rock = any(keyword in desc for keyword in rock_keywords)
                is_not_highly_weathered = not any(keyword in desc for keyword in soil_keywords)
                if is_rock and is_not_highly_weathered:
                    rockhead_depths[loca_id] = float(row['GEOL_TOP'])
                    break
        return rockhead_depths
    
    def calculate_q_value_bulk(self, df: pd.DataFrame, rqd_col: str = 'RQD', 
                              jn: float = 9, jr: float = 1, ja: float = 1, 
                              jw: float = 1, srf: float = 1) -> pd.DataFrame:
        """Calculate Q-value bulk (from AGS-Processor)."""
        df = df.copy()
        if rqd_col not in df.columns:
            raise ValueError(f"DataFrame must contain '{rqd_col}' column")
        
        df['RQD_numeric'] = pd.to_numeric(df[rqd_col], errors='coerce')
        df['Q_value'] = (df['RQD_numeric'] / jn) * (jr / ja) * (jw / srf)
        
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
    
    def calculate_q_values_bulk(self, data_df: pd.DataFrame, rqd_col: str = 'RQD',
                               jn_col: str = 'Jn', jr_col: str = 'Jr', ja_col: str = 'Ja',
                               jw_col: str = 'Jw', srf_col: str = 'SRF') -> pd.DataFrame:
        """Wrapper with column mapping."""
        result_df = data_df.copy()
        required_cols = [rqd_col, jn_col, jr_col, ja_col, jw_col, srf_col]
        if not all(col in data_df.columns for col in required_cols):
            raise ValueError(f"Missing required columns. Need: {required_cols}")
        
        q_values = []
        for idx, row in data_df.iterrows():
            try:
                q = self.calculate_q_value(
                    rqd=float(row[rqd_col]), jn=float(row[jn_col]), jr=float(row[jr_col]),
                    ja=float(row[ja_col]), jw=float(row[jw_col]), srf=float(row[srf_col])
                )
                q_values.append(q)
            except (ValueError, TypeError, ZeroDivisionError):
                q_values.append(np.nan)
        result_df['Q_VALUE'] = q_values
        return result_df
    
    def calculate_q_value(self, rqd: float, jn: float, jr: float, ja: float, jw: float, srf: float) -> float:
        """Calculate single Q-value."""
        if any(val <= 0 for val in [jn, ja, srf]):
            raise ValueError("Jn, Ja, and SRF must be greater than 0")
        if not (0 <= rqd <= 100):
            raise ValueError("RQD must be between 0 and 100")
        return (rqd / jn) * (jr / ja) * (jw / srf)
    
    def interpret_q_value(self, q_value: float) -> str:
        """Interpret Q-value."""
        if q_value >= 400:
            return "Exceptionally Good"
        elif q_value >= 100:
            return "Extremely Good"
        elif q_value >= 40:
            return "Very Good"
        elif q_value >= 10:
            return "Good"
        elif q_value >= 4:
            return "Fair"
        elif q_value >= 1:
            return "Poor"
        elif q_value >= 0.1:
            return "Very Poor"
        elif q_value >= 0.01:
            return "Extremely Poor"
        else:
            return "Exceptionally Poor"
    
    def detect_corestones(self, geology_df: pd.DataFrame, min_thickness: float = 0.5) -> pd.DataFrame:
        """Detect corestones."""
        corestones = []
        if geology_df.empty:
            return pd.DataFrame(corestones)
        
        if not all(col in geology_df.columns for col in ['LOCA_ID', 'GEOL_TOP', 'GEOL_BASE', 'GEOL_DESC']):
            return pd.DataFrame(corestones)
        
        corestone_keywords = ['SLIGHTLY WEATHERED', 'FRESH', 'CORESTONE', 'MODERATELY WEATHERED', 'UNWEATHERED']
        
        for loca_id, group in geology_df.groupby('LOCA_ID'):
            group = group.sort_values('GEOL_TOP')
            for idx, row in group.iterrows():
                desc = str(row.get('GEOL_DESC', '')).upper()
                if any(keyword in desc for keyword in corestone_keywords):
                    top = float(row.get('GEOL_TOP', 0))
                    base = float(row.get('GEOL_BASE', top))
                    thickness = base - top
                    if thickness >= min_thickness:
                        corestones.append({
                            'LOCA_ID': loca_id, 'CORESTONE_TOP': top,
                            'CORESTONE_BASE': base, 'THICKNESS': thickness,
                            'DESCRIPTION': row.get('GEOL_DESC', '')
                        })
        return pd.DataFrame(corestones)
    
    def estimate_rqd_from_fracture_frequency(self, fractures_per_meter: float) -> float:
        """Estimate RQD from fracture frequency."""
        jv = fractures_per_meter * 3
        rqd = 115 - 3.3 * jv
        return max(0, min(100, rqd))
    
    def get_q_parameters_guide(self) -> Dict[str, Dict]:
        """Get Q-system parameter guidelines."""
        return {
            'RQD': {'description': 'Rock Quality Designation (%)', 'range': '0-100',
                   'guidelines': {'Very Poor': '0-25', 'Poor': '25-50', 'Fair': '50-75',
                                'Good': '75-90', 'Excellent': '90-100'}},
            'Jn': {'description': 'Joint set number',
                  'guidelines': {'Massive, no joints': 0.5-1.0, 'One joint set': 2,
                               'One joint set plus random': 3, 'Two joint sets': 4,
                               'Two joint sets plus random': 6, 'Three joint sets': 9,
                               'Three joint sets plus random': 12, 'Four or more joint sets': 15,
                               'Crushed rock': 20}},
            'Jr': {'description': 'Joint roughness number',
                  'guidelines': {'Discontinuous joints': 4, 'Rough/irregular, undulating': 3,
                               'Smooth, undulating': 2, 'Slickensided, undulating': 1.5,
                               'Rough/irregular, planar': 1.5, 'Smooth, planar': 1.0,
                               'Slickensided, planar': 0.5}},
            'Ja': {'description': 'Joint alteration number',
                  'guidelines': {'Tightly healed': 0.75, 'Unaltered joint walls': 1.0,
                               'Slightly altered': 2, 'Silty/sandy coating': 3,
                               'Soft clay coating': 4, 'Sandy clay/crushed rock': 6,
                               'Soft clay/low friction': 8-12}},
            'Jw': {'description': 'Joint water reduction factor',
                  'guidelines': {'Dry excavation': 1.0, 'Medium inflow': 0.66,
                               'Large inflow': 0.5, 'Severe inflow': 0.33-0.1}},
            'SRF': {'description': 'Stress reduction factor',
                   'guidelines': {'Low stress': 2.5, 'Medium stress': 1.0,
                                'High stress': 5-20, 'Squeezing rock': 5-20,
                                'Swelling rock': 5-20}}
        }
