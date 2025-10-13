"""
Cargos - Uniform Management Application

A GUI application for generating uniform documents from Excel data.
"""

__version__ = "1.0.0"
__author__ = "Leonardo Candio"

from .core import *
from .services import *
from .ui import *

__all__ = [
    'ExcelService',
    'FileGenerationService',
    'ConfigManager',
    'UnifiedConfigService',
    'CargosTab',
    'ConfigurationTab',
]

