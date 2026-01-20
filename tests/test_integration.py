"""Integration tests for AGS Processor."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from ags_processor import AGSProcessor, AGSValidator, AGSExporter
from tests.sample_data import create_sample_ags4_file


class TestIntegration(unittest.TestCase):
    """Integration tests for the full workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.sample_file = os.path.join(self.test_dir, 'sample.ags')
        create_sample_ags4_file(self.sample_file)
        
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_full_workflow(self):
        """Test complete workflow: read, validate, export."""
        # Initialize components
        processor = AGSProcessor()
        validator = AGSValidator()
        exporter = AGSExporter()
        
        # Validate file
        validation_result = validator.validate_file(self.sample_file)
        self.assertTrue(validation_result['valid'])
        
        # Read file
        file_data = processor.read_file(self.sample_file)
        self.assertIsNotNone(file_data)
        self.assertEqual(file_data['version'], 'AGS4')
        
        # Get tables
        tables = processor.get_all_tables()
        self.assertGreater(len(tables), 0)
        
        # Verify expected tables
        expected_tables = ['PROJ', 'TRAN', 'LOCA', 'GEOL', 'SAMP']
        for table_name in expected_tables:
            self.assertIn(table_name, tables)
            
        # Export to Excel
        output_file = os.path.join(self.test_dir, 'output.xlsx')
        success = exporter.export_to_excel(tables, output_file)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_file))
        
        # Verify file is not empty
        self.assertGreater(os.path.getsize(output_file), 0)
        
    def test_multiple_files_workflow(self):
        """Test workflow with multiple files."""
        # Create multiple sample files
        file1 = os.path.join(self.test_dir, 'file1.ags')
        file2 = os.path.join(self.test_dir, 'file2.ags')
        create_sample_ags4_file(file1)
        create_sample_ags4_file(file2)
        
        # Process multiple files
        processor = AGSProcessor()
        file_data = processor.read_multiple_files([file1, file2])
        
        self.assertEqual(len(file_data), 2)
        
        # Get summary
        summary = processor.get_file_summary()
        self.assertEqual(summary['total_files'], 2)
        self.assertEqual(summary['files_by_version']['AGS4'], 2)
        
        # Get consolidated tables
        tables = processor.get_all_tables()
        
        # Export consolidated data
        exporter = AGSExporter()
        output_file = os.path.join(self.test_dir, 'consolidated.xlsx')
        success = exporter.export_to_excel(tables, output_file)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_file))
        
    def test_csv_export(self):
        """Test CSV export functionality."""
        processor = AGSProcessor()
        processor.read_file(self.sample_file)
        
        tables = processor.get_all_tables()
        
        # Export to CSV
        exporter = AGSExporter()
        csv_dir = os.path.join(self.test_dir, 'csv_output')
        success = exporter.export_to_csv(tables, csv_dir)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(csv_dir))
        
        # Check that CSV files were created
        csv_files = list(Path(csv_dir).glob('*.csv'))
        self.assertGreater(len(csv_files), 0)


if __name__ == '__main__':
    unittest.main()
