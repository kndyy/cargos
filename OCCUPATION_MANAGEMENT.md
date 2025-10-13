# Occupation Management Guide

This guide explains how to add, modify, and manage occupations in the Uniformes application in a maintainable and extensible way.

## Overview

The application uses a **single source of truth** for all configuration: `config.json`. All occupation data, prendas, pricing, and synonyms are stored in this file and managed through the `UnifiedConfigService`.

## Architecture

```
config.json (Single Source of Truth)
    ↓
ConfigManager (Low-level file I/O)
    ↓
UnifiedConfigService (Business logic & API)
    ↓
UI Components & Services (Application layer)
```

## Adding a New Occupation

### Method 1: Via UI (Recommended for most users)

1. Open the application
2. Go to the **Configuration** tab
3. Click **"Add Occupation"**
4. Fill in the occupation details:
   - **Name**: Internal identifier (e.g., "CAJERO")
   - **Display Name**: User-friendly name (e.g., "Cajero")
   - **Synonyms**: All variations (e.g., "CAJERO", "CAJERA", "CAJERO(A)", "CAJERO (A)", "CASHIER")
   - **Description**: Optional description
5. Add prendas to the occupation
6. Set prices for each prenda (by size and location)
7. Click **"Save Configuration"**

### Method 2: Via config.json (For bulk changes or advanced users)

1. Open `config.json` in a text editor
2. Add a new occupation object to the `occupations` array:

```json
{
  "name": "CAJERO",
  "display_name": "Cajero",
  "synonyms": [
    "CAJERO", "CAJERA", "CAJERO(A)", "CAJERO (A)",
    "CASHIER", "CASHIER(A)", "CASHIER (A)",
    "CAJA", "CAJA(A)", "CAJA (A)"
  ],
  "prendas": [
    {
      "prenda_type": "CAMISA",
      "display_name": "Camisa Cajero",
      "has_sizes": true,
      "is_required": false,
      "default_quantity": 0,
      "price_sml_other": 36.0,
      "price_xl_other": 38.0,
      "price_xxl_other": 40.0,
      "price_sml_tarapoto": 34.0,
      "price_xl_tarapoto": 36.0,
      "price_xxl_tarapoto": 36.0,
      "price_sml_san_isidro": 43.0,
      "price_xl_san_isidro": 46.0,
      "price_xxl_san_isidro": 46.0
    }
  ],
  "is_active": true,
  "description": "Cajero/Cashier position"
}
```

3. Save the file
4. Restart the application or click **"Reload"** in the Configuration tab

## Occupation Structure

### Required Fields

- **name** (string): Internal identifier, UPPERCASE, no spaces
- **display_name** (string): Human-readable name
- **synonyms** (array of strings): All variations of the occupation name
- **prendas** (array): List of clothing items for this occupation
- **is_active** (boolean): Whether this occupation is currently in use

### Optional Fields

- **description** (string): Additional information about the occupation

## Prenda Structure

### Required Fields

- **prenda_type** (string): Internal identifier (e.g., "CAMISA", "POLO", "PANTALON")
- **display_name** (string): User-friendly name (e.g., "Camisa Bar")
- **has_sizes** (boolean): Whether this prenda has size variations
- **garment_type** (string): "UPPER" for upper body garments or "LOWER" for lower body garments
  - **UPPER**: Uses "talla prenda superior" from Excel (shirts, jackets, aprons, etc.)
  - **LOWER**: Uses "talla prenda inferior" from Excel (pants, trousers)
  - Defaults to "UPPER" if not specified
- **price_sml_other** (float): Price for S/M/L sizes in OTHER locations
- **price_xl_other** (float): Price for XL size in OTHER locations
- **price_xxl_other** (float): Price for XXL size in OTHER locations
- **price_sml_tarapoto** (float): Price for S/M/L sizes in TARAPOTO
- **price_xl_tarapoto** (float): Price for XL size in TARAPOTO
- **price_xxl_tarapoto** (float): Price for XXL size in TARAPOTO
- **price_sml_san_isidro** (float): Price for S/M/L sizes in SAN ISIDRO
- **price_xl_san_isidro** (float): Price for XL size in SAN ISIDRO
- **price_xxl_san_isidro** (float): Price for XXL size in SAN ISIDRO

### Optional Fields

- **is_required** (boolean): Whether this prenda is mandatory (default: false)
- **default_quantity** (integer): Default quantity when creating new entries (default: 0)

### Garment Type Details

The `garment_type` field determines which size column from the Excel file is used:

- **UPPER garments** (default):
  - Shirts (CAMISA, BLUSA)
  - Polos (POLO)
  - Jackets (CASACA, SACO, CHAQUETA)
  - Aprons (MANDILON, PECHERA)
  - Accessories (GORRA, ANDARIN)
  - Uses: "Talla Prenda Superior" column from Excel

- **LOWER garments**:
  - Pants (PANTALON, PANTALÓN)
  - Trousers (PANTS, TROUSERS)
  - Uses: "Talla Prenda Inferior" column from Excel
  - Falls back to "Talla Prenda Superior" if inferior not available

The system automatically detects garment type based on the prenda name, but you can override it by setting the `garment_type` field explicitly.

## Synonym Best Practices

Always include these variations for each occupation:

1. **Base name**: `MOZO`
2. **Feminine form**: `MOZA`
3. **Gender-neutral with parentheses**: `MOZO(A)` (no space)
4. **Gender-neutral with space**: `MOZO (A)` (with space)
5. **Alternative names**: `MESERO`, `MESERA`, `MESERO(A)`, `MESERO (A)`
6. **English equivalents** (if applicable): `WAITER`, `WAITRESS`, `WAITER(A)`
7. **Abbreviations**: `MOZO FT`, `MOZO F/T`, `MOZO PT`, `MOZO P/T`
8. **Full forms**: `MOZO FULL TIME`, `MOZO PART TIME`

### Example for Production/Kitchen Staff

```json
"synonyms": [
  "PRODUCCION", "PRODUCCIÓN", "PRODUCCION(A)", "PRODUCCIÓN(A)", "PRODUCCION (A)", "PRODUCCIÓN (A)",
  "COCINA", "COCINERO", "COCINERA", "COCINERO(A)", "COCINERO (A)",
  "CHEF", "CHEF(A)", "CHEF (A)", "KITCHEN",
  "AYUDANTE DE COCINA", "AYUDANTE DE COCINA (A)", "AYUDANTE(A) DE COCINA",
  "PARRILLERO", "PARRILLERA", "PARRILLERO(A)", "PARRILLERO (A)",
  "HORNERO", "HORNERA", "HORNERO(A)", "HORNERO (A)",
  "PANADERO", "PANADERA", "PANADERO(A)", "PANADERO (A)",
  "PASTELERO", "PASTELERA", "PASTELERO(A)", "PASTELERO (A)"
]
```

## Programmatic API

The `UnifiedConfigService` provides a comprehensive API for managing occupations:

### Occupation Management

```python
# Get service instance
from unified_config_service import UnifiedConfigService
import logging

service = UnifiedConfigService(logging.getLogger())

# Get all occupations
occupations = service.get_all_occupations()

# Get specific occupation (by name or synonym)
occupation = service.get_occupation("MOZO")
occupation = service.get_occupation("MESERO")  # Works with synonyms

# Normalize occupation name
normalized = service.normalize_occupation("mesero(a)")  # Returns "MOZO"

# Add new occupation
from models import Occupation, OccupationPrenda

new_occupation = Occupation(
    name="CAJERO",
    display_name="Cajero",
    synonyms=["CAJERO", "CAJERA", "CAJERO(A)"],
    prendas=[...],
    is_active=True
)
service.add_occupation(new_occupation)

# Update occupation
service.update_occupation(modified_occupation)

# Delete occupation
service.delete_occupation("CAJERO")

# Validate occupation before saving
errors = service.validate_occupation(new_occupation)
if not errors:
    service.add_occupation(new_occupation)
    service.save()
```

### Prenda Management

```python
# Add prenda to occupation
new_prenda = OccupationPrenda(
    prenda_type="CHALECO",
    display_name="Chaleco",
    has_sizes=True,
    price_sml_other=45.0,
    # ... other prices
)
service.add_prenda_to_occupation("MOZO", new_prenda)

# Update prenda
service.update_prenda_in_occupation("MOZO", modified_prenda)

# Delete prenda
service.delete_prenda_from_occupation("MOZO", "CHALECO")

# Get specific prenda
prenda = service.get_prenda_from_occupation("MOZO", "CAMISA")
```

### Synonym Management

```python
# Add synonym
service.add_synonym_to_occupation("MOZO", "WAITER")

# Remove synonym
service.remove_synonym_from_occupation("MOZO", "WAITER")
```

### Pricing

```python
# Calculate total price for a person
prendas = [
    {"prenda_type": "CAMISA", "qty": 2, "string": "CAMISA TALLA M"},
    {"prenda_type": "MANDILON", "qty": 1, "string": "MANDILON"}
]
total = service.calculate_total_price(prendas, "MOZO", "TARAPOTO")

# Get configuration matrix (for UI display)
matrix = service.get_configuration_matrix()
# Returns list of dicts with: occupation_display, prenda_type, size_group, local_group, price
```

### Persistence

```python
# Save all changes to config.json
service.save()

# Reload from config.json
service.reload()

# Export to dictionary
config_dict = service.export_to_dict()
```

## Excel Integration

The application automatically reads prenda names from the Excel file (row 6, columns J-AH). When you add a new occupation:

1. Update the Excel template to include columns for the new occupation's prendas
2. Ensure row 6 contains the prenda names (e.g., "POLO", "GORRA", "CAMISA")
3. The application will automatically detect and use these column names

## Validation

The system validates:

- Occupation names are not empty
- Display names are provided
- At least one synonym exists
- At least one prenda exists
- Prenda types are not empty
- Prices are non-negative

Use `validate_occupation()` and `validate_prenda()` before saving to catch errors early.

## Best Practices

1. **Always use UPPERCASE** for internal names and synonyms
2. **Include comprehensive synonyms** to handle all variations in Excel files
3. **Use descriptive display names** for better UI readability
4. **Set appropriate prices** for all size/location combinations
5. **Test with sample data** after adding new occupations
6. **Back up config.json** before making bulk changes
7. **Use the UI** for single changes, edit config.json for bulk updates
8. **Validate** before saving to catch errors early

## Troubleshooting

### Occupation not recognized in Excel

- Check that all synonyms are included in the occupation's synonym list
- Ensure synonyms match exactly (case-insensitive but spacing matters)
- Add the Excel cargo value as a synonym

### Prices not calculating correctly

- Verify all price fields are set (9 prices per prenda)
- Check that prenda_type matches exactly between config and Excel
- Use logging to debug: check app.log for pricing calculations

### UI not showing changes

- Click "Reload" in the Configuration tab
- Restart the application
- Check that config.json was saved correctly

## Migration Guide

If you have old configuration in code, migrate to config.json:

1. Export current configuration: `service.export_to_dict()`
2. Save to config.json
3. Remove hardcoded defaults from code
4. Test thoroughly with sample data

## Support

For issues or questions:
1. Check app.log for error messages
2. Validate your configuration using the API
3. Review this guide for best practices
4. Test with a small sample before bulk changes

