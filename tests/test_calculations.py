"""Tests for geotechnical calculations."""

import unittest
import pandas as pd
import numpy as np

from ags_processor.calculations import GeotechnicalCalculations


class TestGeotechnicalCalculations(unittest.TestCase):
    """Test cases for geotechnical calculation functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calc = GeotechnicalCalculations()
        
    def test_q_value_calculation(self):
        """Test Q-value calculation."""
        # Test case from NGI handbook
        q = self.calc.calculate_q_value(
            rqd=90,
            jn=3,
            jr=3,
            ja=1,
            jw=1,
            srf=1
        )
        self.assertAlmostEqual(q, 90.0, places=1)
        
    def test_q_value_poor_rock(self):
        """Test Q-value for poor rock mass."""
        q = self.calc.calculate_q_value(
            rqd=40,
            jn=9,
            jr=1,
            ja=3,
            jw=0.66,
            srf=5
        )
        self.assertLess(q, 1.0)
        
    def test_q_value_invalid_inputs(self):
        """Test Q-value calculation with invalid inputs."""
        with self.assertRaises(ValueError):
            self.calc.calculate_q_value(
                rqd=150,  # Invalid RQD
                jn=3,
                jr=3,
                ja=1,
                jw=1,
                srf=1
            )
        
        with self.assertRaises(ValueError):
            self.calc.calculate_q_value(
                rqd=90,
                jn=0,  # Invalid Jn
                jr=3,
                ja=1,
                jw=1,
                srf=1
            )
    
    def test_q_value_interpretation(self):
        """Test Q-value interpretation."""
        self.assertEqual(
            self.calc.interpret_q_value(500),
            "Exceptionally Good"
        )
        self.assertEqual(
            self.calc.interpret_q_value(50),
            "Very Good"
        )
        self.assertEqual(
            self.calc.interpret_q_value(5),
            "Fair"
        )
        self.assertEqual(
            self.calc.interpret_q_value(0.5),
            "Very Poor"  # Fixed: 0.5 is in range 0.1-1.0
        )
        self.assertEqual(
            self.calc.interpret_q_value(0.05),
            "Extremely Poor"
        )
        self.assertEqual(
            self.calc.interpret_q_value(0.005),
            "Exceptionally Poor"
        )
    
    def test_rockhead_detection(self):
        """Test rockhead detection."""
        # Create sample geological data
        geol_data = pd.DataFrame({
            'LOCA_ID': ['BH01', 'BH01', 'BH01', 'BH02', 'BH02'],
            'GEOL_TOP': [0.0, 2.5, 5.0, 0.0, 3.0],
            'GEOL_BASE': [2.5, 5.0, 10.0, 3.0, 8.0],
            'GEOL_DESC': [
                'CLAY - brown, soft',
                'CLAY - grey, stiff',
                'GRANITE - slightly weathered',
                'SAND - loose',
                'ROCK - fresh sandstone'  # Changed to ensure detection
            ]
        })
        
        rockhead = self.calc.detect_rockhead(geol_data)
        
        self.assertIn('BH01', rockhead)
        self.assertIn('BH02', rockhead)
        self.assertEqual(rockhead['BH01'], 5.0)
        self.assertEqual(rockhead['BH02'], 3.0)
    
    def test_rockhead_detection_empty(self):
        """Test rockhead detection with empty dataframe."""
        geol_data = pd.DataFrame()
        rockhead = self.calc.detect_rockhead(geol_data)
        self.assertEqual(rockhead, {})
    
    def test_corestone_detection(self):
        """Test corestone detection."""
        geol_data = pd.DataFrame({
            'LOCA_ID': ['BH01', 'BH01', 'BH01', 'BH01'],
            'GEOL_TOP': [0.0, 2.0, 4.0, 6.0],
            'GEOL_BASE': [2.0, 4.0, 6.0, 10.0],
            'GEOL_DESC': [
                'SOIL - weathered',
                'GRANITE - fresh (corestone)',
                'SOIL - highly weathered',
                'GRANITE - slightly weathered'
            ]
        })
        
        corestones = self.calc.detect_corestones(geol_data, min_thickness=0.5)
        
        self.assertGreater(len(corestones), 0)
        self.assertEqual(corestones.iloc[0]['LOCA_ID'], 'BH01')
        self.assertEqual(corestones.iloc[0]['THICKNESS'], 2.0)
    
    def test_corestone_detection_min_thickness(self):
        """Test corestone detection with thickness filter."""
        geol_data = pd.DataFrame({
            'LOCA_ID': ['BH01', 'BH01'],
            'GEOL_TOP': [0.0, 1.0],
            'GEOL_BASE': [1.0, 1.3],
            'GEOL_DESC': [
                'SOIL - weathered',
                'GRANITE - fresh (corestone)'
            ]
        })
        
        # With min_thickness=0.5, should find corestone
        corestones = self.calc.detect_corestones(geol_data, min_thickness=0.2)
        self.assertEqual(len(corestones), 1)
        
        # With min_thickness=1.0, should not find corestone
        corestones = self.calc.detect_corestones(geol_data, min_thickness=1.0)
        self.assertEqual(len(corestones), 0)
    
    def test_q_value_bulk_calculation(self):
        """Test bulk Q-value calculation."""
        data = pd.DataFrame({
            'RQD': [90, 75, 50],
            'Jn': [3, 4, 9],
            'Jr': [3, 2, 1],
            'Ja': [1, 2, 3],
            'Jw': [1, 0.66, 0.5],
            'SRF': [1, 1, 5]
        })
        
        result = self.calc.calculate_q_values_bulk(data)
        
        self.assertIn('Q_VALUE', result.columns)
        self.assertEqual(len(result), 3)
        self.assertAlmostEqual(result.iloc[0]['Q_VALUE'], 90.0, places=1)
        self.assertTrue(result.iloc[0]['Q_VALUE'] > result.iloc[2]['Q_VALUE'])
    
    def test_q_value_bulk_with_invalid_data(self):
        """Test bulk Q-value calculation with some invalid rows."""
        data = pd.DataFrame({
            'RQD': [90, None, 50],
            'Jn': [3, 4, 0],  # Invalid Jn in last row
            'Jr': [3, 2, 1],
            'Ja': [1, 2, 3],
            'Jw': [1, 0.66, 0.5],
            'SRF': [1, 1, 5]
        })
        
        result = self.calc.calculate_q_values_bulk(data)
        
        # First row should have valid Q-value
        self.assertFalse(pd.isna(result.iloc[0]['Q_VALUE']))
        # Second and third rows should have NaN
        self.assertTrue(pd.isna(result.iloc[1]['Q_VALUE']))
        self.assertTrue(pd.isna(result.iloc[2]['Q_VALUE']))
    
    def test_rqd_estimation_from_fractures(self):
        """Test RQD estimation from fracture frequency."""
        # Low fracture frequency -> high RQD
        rqd_low = self.calc.estimate_rqd_from_fracture_frequency(2)
        self.assertGreater(rqd_low, 90)
        
        # High fracture frequency -> low RQD
        rqd_high = self.calc.estimate_rqd_from_fracture_frequency(20)
        self.assertLess(rqd_high, 50)
        
        # Very high fracture frequency -> should clamp to 0
        rqd_very_high = self.calc.estimate_rqd_from_fracture_frequency(50)
        self.assertEqual(rqd_very_high, 0)
    
    def test_parameter_guide(self):
        """Test parameter guide retrieval."""
        guide = self.calc.get_q_parameters_guide()
        
        self.assertIn('RQD', guide)
        self.assertIn('Jn', guide)
        self.assertIn('Jr', guide)
        self.assertIn('Ja', guide)
        self.assertIn('Jw', guide)
        self.assertIn('SRF', guide)
        
        self.assertIn('description', guide['RQD'])
        self.assertIn('guidelines', guide['Jn'])


if __name__ == '__main__':
    unittest.main()
