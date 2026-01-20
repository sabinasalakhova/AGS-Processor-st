"""
Geotechnical calculation functions for AGS data.

Includes:
- Rockhead detection
- Corestone identification
- Q-value (NGI rock mass classification) calculation
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


class GeotechnicalCalculations:
    """
    Geotechnical calculations for AGS data analysis.
    
    Provides functions for:
    - Rockhead depth determination
    - Corestone detection
    - Q-value calculation (NGI rock mass classification)
    """
    
    def __init__(self):
        """Initialize geotechnical calculations."""
        pass
    
    def detect_rockhead(
        self, 
        geology_df: pd.DataFrame,
        weathering_threshold: str = 'MODERATELY WEATHERED'
    ) -> Dict[str, float]:
        """
        Detect rockhead depth for each location.
        
        Rockhead is the interface between soil/weathered material and hard rock.
        
        Args:
            geology_df: DataFrame with GEOL group data (must include LOCA_ID, GEOL_TOP, GEOL_DESC)
            weathering_threshold: Weathering grade that marks rockhead transition
            
        Returns:
            Dictionary mapping LOCA_ID to rockhead depth
        """
        rockhead_depths = {}
        
        if geology_df.empty:
            return rockhead_depths
        
        # Ensure required columns exist
        required_cols = ['LOCA_ID', 'GEOL_TOP', 'GEOL_DESC']
        if not all(col in geology_df.columns for col in required_cols):
            return rockhead_depths
        
        # Keywords indicating hard rock
        rock_keywords = [
            'ROCK', 'GRANITE', 'BASALT', 'LIMESTONE', 'SANDSTONE', 'MUDSTONE',
            'SLIGHTLY WEATHERED', 'FRESH', 'UNWEATHERED', 'MODERATELY WEATHERED'
        ]
        
        # Keywords indicating soil/highly weathered material (use word boundaries)
        soil_keywords = [
            ' SOIL', 'CLAY', 'SILT', ' SAND ', 'GRAVEL',
            'COMPLETELY WEATHERED', 'HIGHLY WEATHERED', 'MADE GROUND', 'FILL'
        ]
        
        # Group by location
        for loca_id, group in geology_df.groupby('LOCA_ID'):
            # Sort by depth
            group = group.sort_values('GEOL_TOP')
            
            for idx, row in group.iterrows():
                desc = str(row.get('GEOL_DESC', '')).upper()
                
                # Check if this layer indicates rock
                is_rock = any(keyword in desc for keyword in rock_keywords)
                is_not_highly_weathered = not any(keyword in desc for keyword in soil_keywords)
                
                if is_rock and is_not_highly_weathered:
                    rockhead_depths[loca_id] = float(row['GEOL_TOP'])
                    break
        
        return rockhead_depths
    
    def detect_corestones(
        self,
        geology_df: pd.DataFrame,
        min_thickness: float = 0.5
    ) -> pd.DataFrame:
        """
        Detect corestones in geological profile.
        
        Corestones are less-weathered rock blocks within a weathered profile.
        
        Args:
            geology_df: DataFrame with GEOL group data
            min_thickness: Minimum thickness (m) to classify as corestone
            
        Returns:
            DataFrame with corestone locations and depths
        """
        corestones = []
        
        if geology_df.empty:
            return pd.DataFrame(corestones)
        
        # Ensure required columns
        if not all(col in geology_df.columns for col in ['LOCA_ID', 'GEOL_TOP', 'GEOL_BASE', 'GEOL_DESC']):
            return pd.DataFrame(corestones)
        
        # Keywords for fresh/slightly weathered rock (potential corestones)
        corestone_keywords = [
            'SLIGHTLY WEATHERED', 'FRESH', 'CORESTONE',
            'MODERATELY WEATHERED', 'UNWEATHERED'
        ]
        
        # Group by location
        for loca_id, group in geology_df.groupby('LOCA_ID'):
            group = group.sort_values('GEOL_TOP')
            
            for idx, row in group.iterrows():
                desc = str(row.get('GEOL_DESC', '')).upper()
                
                # Check if this is a corestone
                is_corestone = any(keyword in desc for keyword in corestone_keywords)
                
                if is_corestone:
                    top = float(row.get('GEOL_TOP', 0))
                    base = float(row.get('GEOL_BASE', top))
                    thickness = base - top
                    
                    if thickness >= min_thickness:
                        corestones.append({
                            'LOCA_ID': loca_id,
                            'CORESTONE_TOP': top,
                            'CORESTONE_BASE': base,
                            'THICKNESS': thickness,
                            'DESCRIPTION': row.get('GEOL_DESC', '')
                        })
        
        return pd.DataFrame(corestones)
    
    def calculate_q_value(
        self,
        rqd: float,
        jn: float,
        jr: float,
        ja: float,
        jw: float,
        srf: float
    ) -> float:
        """
        Calculate Q-value using NGI rock mass classification.
        
        Q = (RQD/Jn) × (Jr/Ja) × (Jw/SRF)
        
        Args:
            rqd: Rock Quality Designation (%)
            jn: Joint set number
            jr: Joint roughness number
            ja: Joint alteration number
            jw: Joint water reduction factor
            srf: Stress reduction factor
            
        Returns:
            Q-value (0.001 to 1000)
        """
        # Validate inputs
        if any(val <= 0 for val in [jn, ja, srf]):
            raise ValueError("Jn, Ja, and SRF must be greater than 0")
        
        if not (0 <= rqd <= 100):
            raise ValueError("RQD must be between 0 and 100")
        
        # Calculate Q-value
        q_value = (rqd / jn) * (jr / ja) * (jw / srf)
        
        return q_value
    
    def calculate_q_values_bulk(
        self,
        data_df: pd.DataFrame,
        rqd_col: str = 'RQD',
        jn_col: str = 'Jn',
        jr_col: str = 'Jr',
        ja_col: str = 'Ja',
        jw_col: str = 'Jw',
        srf_col: str = 'SRF'
    ) -> pd.DataFrame:
        """
        Calculate Q-values for multiple rows in a DataFrame.
        
        Args:
            data_df: DataFrame with rock mass parameters
            rqd_col: Column name for RQD
            jn_col: Column name for Jn
            jr_col: Column name for Jr
            ja_col: Column name for Ja
            jw_col: Column name for Jw
            srf_col: Column name for SRF
            
        Returns:
            DataFrame with added Q_VALUE column
        """
        result_df = data_df.copy()
        
        # Check if required columns exist
        required_cols = [rqd_col, jn_col, jr_col, ja_col, jw_col, srf_col]
        if not all(col in data_df.columns for col in required_cols):
            raise ValueError(f"Missing required columns. Need: {required_cols}")
        
        # Calculate Q-value for each row
        q_values = []
        for idx, row in data_df.iterrows():
            try:
                q = self.calculate_q_value(
                    rqd=float(row[rqd_col]),
                    jn=float(row[jn_col]),
                    jr=float(row[jr_col]),
                    ja=float(row[ja_col]),
                    jw=float(row[jw_col]),
                    srf=float(row[srf_col])
                )
                q_values.append(q)
            except (ValueError, TypeError, ZeroDivisionError):
                q_values.append(np.nan)
        
        result_df['Q_VALUE'] = q_values
        
        return result_df
    
    def interpret_q_value(self, q_value: float) -> str:
        """
        Interpret Q-value and return rock mass quality description.
        
        Args:
            q_value: Calculated Q-value
            
        Returns:
            Rock mass quality description
        """
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
    
    def estimate_rqd_from_fracture_frequency(self, fractures_per_meter: float) -> float:
        """
        Estimate RQD from fracture frequency.
        
        Uses Palmström's formula: RQD = 115 - 3.3 * Jv
        where Jv is the volumetric joint count (fractures/m³)
        
        Args:
            fractures_per_meter: Number of fractures per meter
            
        Returns:
            Estimated RQD (%)
        """
        # For linear fracture frequency, approximate volumetric
        jv = fractures_per_meter * 3  # Rough approximation
        
        rqd = 115 - 3.3 * jv
        
        # Clamp between 0 and 100
        return max(0, min(100, rqd))
    
    def get_q_parameters_guide(self) -> Dict[str, Dict]:
        """
        Get guidance for selecting Q-system parameters.
        
        Returns:
            Dictionary with parameter guidelines
        """
        return {
            'RQD': {
                'description': 'Rock Quality Designation (%)',
                'range': '0-100',
                'guidelines': {
                    'Very Poor': '0-25',
                    'Poor': '25-50',
                    'Fair': '50-75',
                    'Good': '75-90',
                    'Excellent': '90-100'
                }
            },
            'Jn': {
                'description': 'Joint set number',
                'guidelines': {
                    'Massive, no joints': 0.5-1.0,
                    'One joint set': 2,
                    'One joint set plus random': 3,
                    'Two joint sets': 4,
                    'Two joint sets plus random': 6,
                    'Three joint sets': 9,
                    'Three joint sets plus random': 12,
                    'Four or more joint sets': 15,
                    'Crushed rock': 20
                }
            },
            'Jr': {
                'description': 'Joint roughness number',
                'guidelines': {
                    'Discontinuous joints': 4,
                    'Rough/irregular, undulating': 3,
                    'Smooth, undulating': 2,
                    'Slickensided, undulating': 1.5,
                    'Rough/irregular, planar': 1.5,
                    'Smooth, planar': 1.0,
                    'Slickensided, planar': 0.5
                }
            },
            'Ja': {
                'description': 'Joint alteration number',
                'guidelines': {
                    'Tightly healed': 0.75,
                    'Unaltered joint walls': 1.0,
                    'Slightly altered': 2,
                    'Silty/sandy coating': 3,
                    'Soft clay coating': 4,
                    'Sandy clay/crushed rock': 6,
                    'Soft clay/low friction': 8-12
                }
            },
            'Jw': {
                'description': 'Joint water reduction factor',
                'guidelines': {
                    'Dry excavation': 1.0,
                    'Medium inflow': 0.66,
                    'Large inflow': 0.5,
                    'Severe inflow': 0.33-0.1
                }
            },
            'SRF': {
                'description': 'Stress reduction factor',
                'guidelines': {
                    'Low stress': 2.5,
                    'Medium stress': 1.0,
                    'High stress': 5-20,
                    'Squeezing rock': 5-20,
                    'Swelling rock': 5-20
                }
            }
        }
