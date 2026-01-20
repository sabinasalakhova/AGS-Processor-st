"""AGS Processor - A tool for processing AGS3 and AGS4 geotechnical data files."""

__version__ = "0.1.0"

# Import legacy modules
from .validator import AGSValidator
from .exporter import AGSExporter
from .calculations import GeotechnicalCalculations

# Import new comprehensive modules
from . import processor
from . import triaxial
from . import cleaners
from . import search
from . import combiners

__all__ = [
    "AGSValidator", 
    "AGSExporter", 
    "GeotechnicalCalculations",
    "processor",
    "triaxial",
    "cleaners",
    "search",
    "combiners"
]
