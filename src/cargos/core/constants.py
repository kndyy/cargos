"""
Application constants and configuration values.
"""

# Excel parsing constants
METADATA_ROW_FECHA_SOLICITUD = 2  # C3 (0-indexed: row 2, col 2)
METADATA_COL_FECHA_SOLICITUD = 2
METADATA_ROW_TIENDA = 3  # C4
METADATA_COL_TIENDA = 2
METADATA_ROW_ADMINISTRADOR = 4  # C5
METADATA_COL_ADMINISTRADOR = 2

# Data extraction constants
DATA_START_ROW = 6  # Row 7 in Excel (0-indexed)
IGNORE_COLUMN_INDEX = 0  # Column A
MAIN_DATA_END_COLUMN = 8  # Column I (0-indexed, inclusive)

# Uniform data constants
UNIFORM_DATA_START_ROW = 7  # Row 8 in Excel (0-indexed)
UNIFORM_DATA_START_COLUMN = 9  # Column J (0-indexed)
UNIFORM_DATA_END_COLUMN = 33  # Column AH (0-indexed) - extended for new format

# Fixed column mapping for uniform data (Columns J-AH, indices 9-33)
# Based on exact Excel header structure from image
# Format: "OCCUPATION_PRENDA" to avoid duplicates
UNIFORM_COLUMN_MAPPING = {
    # J-M (9-12): SALÓN
    9: "SALON_CAMISA",
    10: "SALON_BLUSA",
    11: "SALON_MANDILON",
    12: "SALON_ANDARIN",
    
    # N-P (13-15): DELIVERY
    13: "DELIVERY_POLO",
    14: "DELIVERY_CASACA",
    15: "DELIVERY_GORRA",
    
    # Q-R (16-17): PACKER
    16: "PACKER_POLO",
    17: "PACKER_GORRA",
    
    # S-V (18-21): BAR
    18: "BAR_CAMISA",
    19: "BAR_BLUSA",
    20: "BAR_POLO",
    21: "BAR_PECHERA",
    
    # W-X (22-23): CAJERO (included but not actively used)
    22: "CAJERO_CAMISA",
    23: "CAJERO_BLUSA",
    
    # Y-AA (24-26): SEGURIDAD
    24: "SEGURIDAD_CAMISA",
    25: "SEGURIDAD_BLUSA",
    26: "SEGURIDAD_SACO",
    
    # AB-AC (27-28): ANFITRIÓN
    27: "ANFITRION_CAMISA",
    28: "ANFITRION_CASACA",
    
    # AD-AH (29-33): PRODUCCIÓN
    29: "PRODUCCION_CHAQUETA",
    30: "PRODUCCION_POLO",
    31: "PRODUCCION_PANTALON",
    32: "PRODUCCION_PECHERA",
    33: "PRODUCCION_GARIBALDI",
}

# UI constants
DEFAULT_WINDOW_SIZE = "700x850"
DEFAULT_PREVIEW_ROWS = 100
DEFAULT_TREE_HEIGHT = 8

# Dialog constants
GENERATION_DIALOG_WIDTH = 600
GENERATION_DIALOG_HEIGHT = 600
GENERATION_DIALOG_CANVAS_HEIGHT = 400

# Tree column widths
TREE_COLUMN_WIDTH_PEOPLE = 120
TREE_COLUMN_WIDTH_STATUS = 100
TREE_COLUMN_WIDTH_UNIFORM = 100
TREE_COLUMN_WIDTH_DATA = 100

# Spanish month names for CARGO documents
SPANISH_MONTHS = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto", 
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

# File paths
DEFAULT_TEMPLATES_DIR = "templates"
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_LOG_FILE = "app.log"

IGNORE_QUANTITY_IN_PRICING = False