# Cargos - Uniform Management Application

A professional GUI application for generating uniform documents from Excel data using Word templates.

## Project Structure

```
cargos/
├── src/
│   └── cargos/              # Main application package
│       ├── core/            # Core business logic and models
│       │   ├── models.py    # Data models and dataclasses
│       │   ├── constants.py # Application constants
│       │   └── validators.py # Validation logic
│       ├── services/        # Business services
│       │   ├── excel_service.py        # Excel parsing and file generation
│       │   ├── config_manager.py       # Configuration persistence
│       │   └── unified_config_service.py # Unified config management
│       ├── ui/              # User interface components
│       │   └── ui_components.py # Tkinter UI components
│       └── main.py          # Main application class
├── templates/               # Word document templates
├── config.json             # Application configuration (single source of truth)
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Features

- ✅ **Excel Data Processing**: Automatically parse uniform requirements from Excel files
- ✅ **Document Generation**: Generate Word documents (CARGO and AUTORIZACION) using templates
- ✅ **Flexible Occupations**: Support for multiple occupations with customizable prendas and pricing
- ✅ **Garment Type Classification**: Automatic handling of upper/lower body garments with appropriate sizing
- ✅ **Multi-Location Pricing**: Different pricing for OTHER, TARAPOTO, and SAN ISIDRO locations
- ✅ **Synonym Matching**: Robust occupation name matching with comprehensive synonyms
- ✅ **Configuration UI**: Easy-to-use interface for managing occupations, prendas, and pricing
- ✅ **Data Preview**: View and validate Excel data before generation
- ✅ **Modular Architecture**: Clean, maintainable code structure

## Installation

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

### Setup

1. **Clone or download the repository**

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

```bash
python run.py
```

Or with virtual environment:
```bash
source .venv/bin/activate
python run.py
```

### Basic Workflow

1. **Load Excel File**:
   - Click "Browse" next to "Formato Uniforme"
   - Select your Excel file with uniform requirements
   - Click "Load"

2. **Review Data**:
   - Check the "Summary" tab for overview
   - View "Details" tab for specific data
   - Check "Uniforms" tab to see parsed uniform data

3. **Configure (Optional)**:
   - Go to "Configuration" tab
   - Add/edit occupations, prendas, and pricing
   - Save configuration

4. **Generate Documents**:
   - Select destination folder
   - Choose templates (CARGO and/or AUTORIZACION)
   - Click "Generate Files"

## Excel Format

The application expects Excel files with the following structure:

### Metadata (Rows 1-6)
- **C3**: Fecha de Solicitud
- **C4**: Tienda (Store name)
- **C5**: Administrador

### Main Data (Starting Row 7)
- **Columns B-I**: Employee information (DNI, Name, Cargo, etc.)
- **Columns J-AF**: Uniform quantities by prenda type

### Uniform Columns (J-AF)
The system uses **fixed position mapping** for uniform columns:
- J-M: SALÓN (Camisa, Blusa, Mandilón, Andarín)
- N-P: DELIVERY (Polo, Casaca, Gorra)
- Q-R: PACKER (Polo, Gorra)
- S-U: BAR (Camisa, Blusa, Polo)
- V: PECHERA BAR
- W-Y: ANFITRIÓN (Camisa, Blusa, Saco)
- Z-AA: SEGURIDAD (Camisa, Casaca)
- AB-AF: PRODUCCIÓN (Chaqueta, Polo, Pantalón, Pechera, Garibaldi)

## Configuration

All configuration is stored in `config.json` as the **single source of truth**.

### Structure

```json
{
  "app_settings": {
    "destination_path": "output/",
    "cargo_template_path": "templates/CARGO UNIFORMES.docx",
    "autorizacion_template_path": "templates/50% - AUTORIZACIÓN DESCUENTO DE UNIFORMES (02).docx",
    "preview_rows_limit": 100
  },
  "occupations": [
    {
      "name": "MOZO",
      "display_name": "Mozo",
      "synonyms": ["MOZO", "MOZA", "MOZO(A)", "MESERO", ...],
      "prendas": [
        {
          "prenda_type": "CAMISA",
          "display_name": "Camisa",
          "has_sizes": true,
          "garment_type": "UPPER",
          "price_sml_other": 36.0,
          ...
        }
      ],
      "is_active": true
    }
  ],
  "default_occupation": "MOZO",
  "default_local_group": "OTHER"
}
```

### Garment Types

- **UPPER**: Upper body garments (shirts, jackets, aprons)
  - Uses "Talla Prenda Superior" from Excel
- **LOWER**: Lower body garments (pants, trousers)
  - Uses "Talla Prenda Inferior" from Excel
  - Falls back to "Talla Prenda Superior" if not available

## Development

### Project Architecture

The application follows a **modular architecture**:

- **`core/`**: Domain models, constants, and validation logic
- **`services/`**: Business logic for Excel processing, file generation, and configuration
- **`ui/`**: User interface components using Tkinter
- **`main.py`**: Application orchestration and initialization

### Key Design Principles

1. **Single Source of Truth**: All configuration in `config.json`
2. **Separation of Concerns**: Clear boundaries between layers
3. **Dependency Injection**: Services injected into UI components
4. **Type Safety**: Extensive use of dataclasses and type hints
5. **Error Handling**: Comprehensive error handling and logging

### Adding New Occupations

See `OCCUPATION_MANAGEMENT.md` for detailed instructions on:
- Adding occupations via UI or config.json
- Managing prendas and pricing
- Configuring synonyms
- Programmatic API usage

## Troubleshooting

### Application won't start
- Ensure virtual environment is activated
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.8+)

### Excel file not loading
- Verify Excel file format matches expected structure
- Check that metadata cells (C3, C4, C5) contain data
- Ensure uniform data starts at row 8 (0-indexed row 7)

### Occupations not recognized
- Check synonyms in `config.json` match Excel cargo values exactly
- Add missing synonyms via Configuration tab
- Ensure case-insensitive matching (all synonyms stored as UPPERCASE)

### Pricing incorrect
- Verify prenda types in config match Excel column names
- Check that all 9 price fields are set (3 sizes × 3 locations)
- Review garment_type setting (UPPER vs LOWER)

### Check logs
- Application logs are written to `app.log`
- Review for detailed error messages and stack traces

## License

Proprietary - All rights reserved

## Support

For issues or questions, refer to:
1. `OCCUPATION_MANAGEMENT.md` - Detailed occupation management guide
2. `app.log` - Application logs
3. Configuration tab - Built-in validation and error messages

## Version History

### v1.0.0 (Current)
- ✅ Modular architecture with clean separation of concerns
- ✅ Fixed column mapping for uniform data
- ✅ Garment type classification (UPPER/LOWER)
- ✅ Comprehensive synonym matching
- ✅ Multi-location pricing support
- ✅ Configuration UI with validation
- ✅ Single source of truth in config.json
