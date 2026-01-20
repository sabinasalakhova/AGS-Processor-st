# Tests

This directory contains tests for the AGS Processor.

## Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_processor

# Run with verbose output
python -m unittest discover tests -v
```

## Test Structure

- `test_processor.py` - Tests for core processor, validator, and exporter functionality
- `sample_data.py` - Sample AGS4 data for testing
