"""Tests for AGS Processor."""

import os
import tempfile
import unittest
from pathlib import Path

from ags_processor import AGSProcessor, AGSValidator, AGSExporter


class TestAGSProcessor(unittest.TestCase):
    """Test cases for AGSProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = AGSProcessor()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temp directory
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_initialization(self):
        """Test processor initialization."""
        self.assertIsNotNone(self.processor)
        self.assertEqual(len(self.processor.files_data), 0)
        self.assertEqual(len(self.processor.errors), 0)
        
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        result = self.processor.read_file('nonexistent.ags')
        self.assertIsNone(result)
        self.assertIn('nonexistent.ags', self.processor.errors)
        
    def test_get_table_list_empty(self):
        """Test getting table list with no files loaded."""
        tables = self.processor.get_table_list()
        self.assertEqual(len(tables), 0)
        
    def test_get_file_summary_empty(self):
        """Test getting summary with no files loaded."""
        summary = self.processor.get_file_summary()
        self.assertEqual(summary['total_files'], 0)
        self.assertEqual(summary['total_errors'], 0)
        self.assertEqual(summary['total_tables'], 0)
        
    def test_clear(self):
        """Test clearing processor data."""
        self.processor.errors['test'] = ['error']
        self.processor.clear()
        self.assertEqual(len(self.processor.files_data), 0)
        self.assertEqual(len(self.processor.errors), 0)


class TestAGSValidator(unittest.TestCase):
    """Test cases for AGSValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = AGSValidator()
        
    def test_initialization(self):
        """Test validator initialization."""
        self.assertIsNotNone(self.validator)
        self.assertEqual(len(self.validator.validation_errors), 0)
        self.assertEqual(len(self.validator.validation_warnings), 0)
        
    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file."""
        result = self.validator.validate_file('nonexistent.ags')
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)
        
    def test_get_summary(self):
        """Test getting validation summary."""
        summary = self.validator.get_summary()
        self.assertIn('total_errors', summary)
        self.assertIn('total_warnings', summary)


class TestAGSExporter(unittest.TestCase):
    """Test cases for AGSExporter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.exporter = AGSExporter()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_initialization(self):
        """Test exporter initialization."""
        self.assertIsNotNone(self.exporter)
        self.assertEqual(len(self.exporter.export_errors), 0)
        
    def test_export_empty_tables(self):
        """Test exporting empty tables."""
        import pandas as pd
        tables = {'TEST': pd.DataFrame()}
        output_path = os.path.join(self.test_dir, 'output.xlsx')
        
        success = self.exporter.export_to_excel(tables, output_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(output_path))
        
    def test_create_summary_sheet(self):
        """Test summary sheet creation."""
        import pandas as pd
        tables = {
            'TABLE1': pd.DataFrame({'A': [1, 2], 'B': [3, 4]}),
            'TABLE2': pd.DataFrame({'C': [5], 'D': [6]})
        }
        
        summary = self.exporter._create_summary_sheet(tables)
        self.assertEqual(len(summary), 2)
        self.assertIn('Table Name', summary.columns)
        self.assertIn('Row Count', summary.columns)
        
    def test_clear_errors(self):
        """Test clearing export errors."""
        self.exporter.export_errors.append('test error')
        self.exporter.clear_errors()
        self.assertEqual(len(self.exporter.export_errors), 0)


if __name__ == '__main__':
    unittest.main()
