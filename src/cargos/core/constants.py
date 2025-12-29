"""
Application constants and configuration values.
"""

# Excel parsing constants - Metadata rows
METADATA_ROW_FECHA_SOLICITUD = 2  # C3 (0-indexed: row 2, col 2)
METADATA_COL_FECHA_SOLICITUD = 2
METADATA_ROW_TIENDA = 3  # C4
METADATA_COL_TIENDA = 2
METADATA_ROW_ADMINISTRADOR = 4  # C5
METADATA_COL_ADMINISTRADOR = 2

# New Excel format row indices (0-indexed)
LOCATION_ROW = 5           # Row 6 in Excel - Location group headers
OCCUPATION_ROW = 6         # Row 7 in Excel - Occupation headers
HEADER_ROW = 7             # Row 8 in Excel - Column headers (DNI, CARGO, prendas, etc.)
DATA_START_ROW = 8         # Row 9 in Excel - First data row

# Data extraction constants
IGNORE_COLUMN_INDEX = 0    # Column A (row numbers)
MAIN_DATA_END_COLUMN = 8   # Column I (0-indexed, inclusive)

# Main data columns (columns B-I, indices 1-8)
MAIN_DATA_COLUMNS = {
    1: "DNI",
    2: "APELLIDOS_Y_NOMBRES",
    3: "CARGO",
    4: "FECHA_DE_INGRESO",
    5: "TRABAJADOR",
    6: "MODALIDAD",
    7: "TALLA_PRENDA_SUPERIOR",
    8: "TALLA_PRENDA_INFERIOR",
}

# Uniform data constants
UNIFORM_DATA_START_ROW = DATA_START_ROW  # Row 9 in Excel (0-indexed = 8)
UNIFORM_DATA_START_COLUMN = 9   # Column J (0-indexed)
UNIFORM_DATA_END_COLUMN = 71    # Column BT (0-indexed) - 72 total columns

# Location-based column groups for uniforms
# Each group has different pricing
LOCATION_GROUPS = {
    "LIMA_ICA": {
        "display_name": "LIMA E ICA PROVINCIA",
        "start_col": 9,
        "end_col": 49,
    },
    "PATIOS_COMIDA": {
        "display_name": "PATIOS DE COMIDA (LARCOMAR, PURUCHUCO, IQUITOS)",
        "start_col": 50,
        "end_col": 63,
    },
    "VILLA_STEAKHOUSE": {
        "display_name": "VILLA STEAKHOUSE (SAN ISIDRO)",
        "start_col": 64,
        "end_col": 71,
    },
}

# Mapping from old location groups to new ones (for backward compatibility in pricing)
OLD_TO_NEW_LOCATION_MAPPING = {
    "OTHER": "LIMA_ICA",
    "TARAPOTO": "LIMA_ICA",  # Tarapoto uses Lima pricing
    "SAN_ISIDRO": "VILLA_STEAKHOUSE",
}

# Detailed column mapping for LIMA E ICA PROVINCIA (columns J-AX, indices 9-49)
LIMA_ICA_COLUMN_MAPPING = {
    # SALÓN (9-12)
    9: ("SALON", "CAMISA"),
    10: ("SALON", "BLUSA"),
    11: ("SALON", "MANDILON"),
    12: ("SALON", "ANDARIN"),
    # DELIVERY (13-15)
    13: ("DELIVERY", "POLO"),
    14: ("DELIVERY", "CASACA"),
    15: ("DELIVERY", "GORRA"),
    # PACKER (16-17)
    16: ("PACKER", "POLO"),
    17: ("PACKER", "GORRA"),
    # BAR (18-21)
    18: ("BAR", "CAMISA"),
    19: ("BAR", "BLUSA"),
    20: ("BAR", "POLO"),
    21: ("BAR", "PECHERA"),
    # ANFITRIONAJE (22-25)
    22: ("ANFITRIONAJE", "CAMISA"),
    23: ("ANFITRIONAJE", "SACO_H"),
    24: ("ANFITRIONAJE", "BLUSA"),
    25: ("ANFITRIONAJE", "SACO_M"),
    # SEGURIDAD (26-27)
    26: ("SEGURIDAD", "CAMISA"),
    27: ("SEGURIDAD", "CASACA"),
    # PRODUCCIÓN (28-32)
    28: ("PRODUCCION", "CHAQUETA"),
    29: ("PRODUCCION", "POLO"),
    30: ("PRODUCCION", "PANTALON"),
    31: ("PRODUCCION", "PECHERA"),
    32: ("PRODUCCION", "GARIBALDI"),
    # CAJA (33-36)
    33: ("CAJA", "CAMISA"),
    34: ("CAJA", "SACO_H"),
    35: ("CAJA", "BLUSA"),
    36: ("CAJA", "SACO_M"),
    # Additional columns (37-38) - unclear from headers, might be CAJA continued
    37: ("CAJA", "CHALECO"),
    38: ("CAJA", "PANTALON"),
    # MANTENIMIENTO (39-41)
    39: ("MANTENIMIENTO", "CHAQUETA"),
    40: ("MANTENIMIENTO", "POLO"),
    41: ("MANTENIMIENTO", "PANTALON"),
    # ADMINISTRACIÓN (42-47)
    42: ("ADMINISTRACION", "CAMISA"),
    43: ("ADMINISTRACION", "SACO_H"),
    44: ("ADMINISTRACION", "POLO"),
    45: ("ADMINISTRACION", "GORRA"),
    46: ("ADMINISTRACION", "BLUSA"),
    47: ("ADMINISTRACION", "SACO_M"),
    # AUDITORÍA (48-49)
    48: ("AUDITORIA", "POLO"),
    49: ("AUDITORIA", "CASACA"),
}

# Detailed column mapping for PATIOS DE COMIDA (columns AY-BL, indices 50-63)
PATIOS_COMIDA_COLUMN_MAPPING = {
    # COUNTER (50-51)
    50: ("COUNTER", "POLO_MANGA_CORTA"),
    51: ("COUNTER", "CASACA"),
    # ADMINISTRACIÓN (52-54)
    52: ("ADMINISTRACION", "CAMISA"),
    53: ("ADMINISTRACION", "BLUSA"),
    54: ("ADMINISTRACION", "GORRO"),
    # PRODUCCIÓN (55-60)
    55: ("PRODUCCION", "POLO_MANGA_CORTA"),
    56: ("PRODUCCION", "CHAQUETA"),
    57: ("PRODUCCION", "POLO"),
    58: ("PRODUCCION", "PANTALON"),
    59: ("PRODUCCION", "PECHERA"),
    60: ("PRODUCCION", "GARIBALDI"),
    # DELIVERY (61-63)
    61: ("DELIVERY", "POLO_MANGA_CORTA"),
    62: ("DELIVERY", "CASACA"),
    63: ("DELIVERY", "GORRA"),
}

# Detailed column mapping for VILLA STEAKHOUSE (columns BM-BT, indices 64-71)
VILLA_STEAKHOUSE_COLUMN_MAPPING = {
    # SALÓN (64-67)
    64: ("SALON", "CAMISA"),
    65: ("SALON", "BLUSA"),
    66: ("SALON", "PECHERA"),
    67: ("SALON", "ANDARIN"),
    # CORREDOR (68-71)
    68: ("CORREDOR", "CAMISA"),
    69: ("CORREDOR", "BLUSA"),
    70: ("CORREDOR", "PECHERA"),
    71: ("CORREDOR", "ANDARIN"),
}

# Combined mapping by location group
LOCATION_COLUMN_MAPPINGS = {
    "LIMA_ICA": LIMA_ICA_COLUMN_MAPPING,
    "PATIOS_COMIDA": PATIOS_COMIDA_COLUMN_MAPPING,
    "VILLA_STEAKHOUSE": VILLA_STEAKHOUSE_COLUMN_MAPPING,
}

# Legacy mapping for backward compatibility (kept for reference)
# This was the old UNIFORM_COLUMN_MAPPING before the format change
LEGACY_UNIFORM_COLUMN_MAPPING = {
    9: "SALON_CAMISA",
    10: "SALON_BLUSA",
    11: "SALON_MANDILON",
    12: "SALON_ANDARIN",
    13: "DELIVERY_POLO",
    14: "DELIVERY_CASACA",
    15: "DELIVERY_GORRA",
    16: "PACKER_POLO",
    17: "PACKER_GORRA",
    18: "BAR_CAMISA",
    19: "BAR_BLUSA",
    20: "BAR_POLO",
    21: "BAR_PECHERA",
    24: "ANFITRION_CAMISA",
    25: "ANFITRION_BLUSA",
    26: "ANFITRION_SACO",
    27: "SEGURIDAD_CAMISA",
    28: "SEGURIDAD_CASACA",
    29: "PRODUCCION_CHAQUETA",
    30: "PRODUCCION_POLO",
    31: "PRODUCCION_PANTALON",
    32: "PRODUCCION_PECHERA",
    33: "PRODUCCION_GARIBALDI",
}

# Build unified column name mapping (LOCATION_OCCUPATION_PRENDA format)
def _build_uniform_column_mapping():
    """Build a flat mapping of column index to unified column name."""
    mapping = {}
    for location, col_map in LOCATION_COLUMN_MAPPINGS.items():
        for col_idx, (occupation, prenda) in col_map.items():
            # Format: LOCATION_OCCUPATION_PRENDA
            mapping[col_idx] = f"{location}_{occupation}_{prenda}"
    return mapping

UNIFORM_COLUMN_MAPPING = _build_uniform_column_mapping()

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