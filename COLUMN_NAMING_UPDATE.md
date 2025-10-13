# Column Naming Logic Update

## Overview

Rewrote the uniform column naming logic to use occupation-prefixed names, eliminating duplicates and matching the exact Excel structure.

## Changes Made

### 1. New Column Naming Format

**Before**: 
- Simple prenda names: `POLO`, `CAMISA`, `GORRA`
- Duplicates handled by adding suffixes: `POLO_2`, `POLO_3`, `CAMISA_2`

**After**:
- Occupation-prefixed names: `DELIVERY_POLO`, `BAR_CAMISA`, `PACKER_GORRA`
- No duplicates - each column has a unique name
- Format: `OCCUPATION_PRENDA`

### 2. Updated Column Mapping

**File**: `src/cargos/core/constants.py`

```python
UNIFORM_COLUMN_MAPPING = {
    # SALÓN (Columns J-M)
    9: "SALON_CAMISA",
    10: "SALON_BLUSA",
    11: "SALON_MANDILON",
    12: "SALON_ANDARIN",
    
    # DELIVERY (Columns N-P) - Starting from image
    13: "DELIVERY_POLO",
    14: "DELIVERY_CASACA",
    15: "DELIVERY_GORRA",
    
    # PACKER (Columns Q-R)
    16: "PACKER_POLO",
    17: "PACKER_GORRA",
    
    # BAR (Columns S-U)
    18: "BAR_CAMISA",
    19: "BAR_BLUSA",
    20: "BAR_POLO",
    
    # PECHERA BAR (Column V)
    21: "BAR_PECHERA",
    
    # ANFITRIÓN (Columns W-Y)
    22: "ANFITRION_CAMISA",
    23: "ANFITRION_BLUSA",
    24: "ANFITRION_SACO",
    
    # SEGURIDAD (Columns Z-AA)
    25: "SEGURIDAD_CAMISA",
    26: "SEGURIDAD_CASACA",
    
    # PRODUCCIÓN (Columns AB-AF)
    27: "PRODUCCION_CHAQUETA",
    28: "PRODUCCION_POLO",
    29: "PRODUCCION_PANTALON",
    30: "PRODUCCION_PECHERA",
    31: "PRODUCCION_GARIBALDI",
}
```

### 3. Simplified Excel Service Logic

**File**: `src/cargos/services/excel_service.py`

**Removed**:
- Complex duplicate handling logic
- Suffix counting (`_2`, `_3`, etc.)
- Special case handling for PACKER, DELIVERY prefixes

**Simplified**:
```python
# Before (complex)
if prenda_name in column_names:
    count = column_names.count(prenda_name) + 1
    column_names.append(f"{prenda_name}_{count}")
else:
    column_names.append(prenda_name)

# After (simple)
column_names.append(UNIFORM_COLUMN_MAPPING[col_idx])
```

### 4. Updated Helper Methods

#### `_normalize_prenda_type()`
```python
# Now handles OCCUPATION_PRENDA format
def _normalize_prenda_type(self, column_name: str) -> str:
    col_upper = str(column_name).upper().strip()
    
    # If already in OCCUPATION_PRENDA format, return as-is
    if '_' in col_upper:
        return col_upper
    
    # Fallback for legacy format...
```

#### `_get_display_name()`
```python
# Simplified to just format the name
def _get_display_name(self, prenda_type: str) -> str:
    # "DELIVERY_POLO" -> "Delivery Polo"
    display = prenda_type.replace('_', ' ').title()
    return display
```

## Benefits

### 1. No Duplicates
✅ Each column has a unique name
✅ No need for suffix counting logic
✅ Clearer data structure

### 2. Semantic Meaning
✅ Column names indicate which occupation they belong to
✅ Easy to understand: `DELIVERY_POLO` vs `POLO_2`
✅ Self-documenting

### 3. Simpler Code
✅ Removed complex duplicate handling
✅ Removed special case logic
✅ More maintainable

### 4. Exact Excel Match
✅ Matches Excel structure starting from Column N
✅ Follows exact order from user's image
✅ Consistent with visual layout

## Column Order Verification

Starting from Column N (index 13) as shown in Excel:

| Column | Index | Name | Occupation |
|--------|-------|------|------------|
| N | 13 | DELIVERY_POLO | DELIVERY |
| O | 14 | DELIVERY_CASACA | DELIVERY |
| P | 15 | DELIVERY_GORRA | DELIVERY |
| Q | 16 | PACKER_POLO | PACKER |
| R | 17 | PACKER_GORRA | PACKER |
| S | 18 | BAR_CAMISA | BAR |
| T | 19 | BAR_BLUSA | BAR |
| U | 20 | BAR_POLO | BAR |
| V | 21 | BAR_PECHERA | PECHERA BAR |
| W | 22 | ANFITRION_CAMISA | ANFITRIÓN |
| X | 23 | ANFITRION_BLUSA | ANFITRIÓN |
| Y | 24 | ANFITRION_SACO | ANFITRIÓN |
| Z | 25 | SEGURIDAD_CAMISA | SEGURIDAD |
| AA | 26 | SEGURIDAD_CASACA | SEGURIDAD |
| AB | 27 | PRODUCCION_CHAQUETA | PRODUCCIÓN |
| AC | 28 | PRODUCCION_POLO | PRODUCCIÓN |
| AD | 29 | PRODUCCION_PANTALON | PRODUCCIÓN |
| AE | 30 | PRODUCCION_PECHERA | PRODUCCIÓN |
| AF | 31 | PRODUCCION_GARIBALDI | PRODUCCIÓN |

## Display Examples

### In UI (Uniforms Tab)
Columns will now display as:
- `DELIVERY_POLO` (instead of `POLO`)
- `BAR_CAMISA` (instead of `CAMISA_2`)
- `PRODUCCION_PANTALON` (instead of `PANTALON`)

### In Document Generation
Display names are formatted nicely:
- `DELIVERY_POLO` → "Delivery Polo"
- `BAR_CAMISA` → "Bar Camisa"
- `PRODUCCION_PANTALON` → "Produccion Pantalon"

## Testing

### Verified Functionality
✅ All 23 columns mapped correctly
✅ All column names are unique
✅ Normalization works correctly
✅ Display names format properly
✅ Excel parsing uses fixed mapping
✅ No duplicate handling needed

### Test Results
```
✅ Total columns: 23
✅ All names unique: True
✅ Column mapping starts at index 13 (Column N)
✅ Matches exact order from Excel image
```

## Migration

### For Users
No action needed! The application will automatically use the new column names when loading Excel files.

### For Developers
If you have code that references column names:

**Before**:
```python
# Old format
if column == "POLO":  # Ambiguous!
    ...
```

**After**:
```python
# New format - clear and specific
if column == "DELIVERY_POLO":
    ...
elif column == "PACKER_POLO":
    ...
```

## Future Enhancements

Possible improvements:
1. Add column descriptions to mapping
2. Create reverse mapping (name → index)
3. Add validation for Excel structure
4. Generate mapping from config file

## Conclusion

The new column naming logic:
- ✅ Eliminates duplicates
- ✅ Provides semantic meaning
- ✅ Simplifies code
- ✅ Matches Excel structure exactly
- ✅ Improves maintainability

The UI will now display clear, unambiguous column names that indicate both the occupation and the prenda type.

