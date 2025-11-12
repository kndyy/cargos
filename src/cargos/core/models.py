"""
Data models and configuration classes for the File Generator application.
"""
from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING, List
from cargos.core.constants import DEFAULT_OUTPUT_DIR, DEFAULT_LOG_FILE, DEFAULT_PREVIEW_ROWS

if TYPE_CHECKING:
    import pandas as pd


@dataclass
class AppConfig:
    """Application configuration settings."""
    destination_path: str = f"{DEFAULT_OUTPUT_DIR}/"
    excel_file_path: str = ""
    cargo_template_path: str = "templates/CARGO UNIFORMES.docx"
    autorizacion_template_path: str = "templates/50% - AUTORIZACIÓN DESCUENTO DE UNIFORMES (02).docx"
    log_file: str = DEFAULT_LOG_FILE
    preview_rows_limit: int = DEFAULT_PREVIEW_ROWS


@dataclass
class WorksheetMetadata:
    """Metadata extracted from a worksheet."""
    sheet_name: str
    fecha_solicitud: str = ""
    tienda: str = ""
    administrador: str = ""
    
    @property
    def identifier(self) -> str:
        """Get worksheet identifier."""
        return self.sheet_name


@dataclass
class WorksheetParsingResult:
    """Result of parsing a single worksheet."""
    metadata: WorksheetMetadata
    data: Optional['pd.DataFrame'] = None  # Main data (columns B through I)
    uniform_data: Optional['pd.DataFrame'] = None  # Uniform data (columns J through R)
    total_lines: int = 0
    people_parsed: int = 0
    errors: list = None
    warnings: list = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        # total_lines and people_parsed are set directly in services.py after processing


@dataclass
class ExcelData:
    """Container for Excel file data and metadata."""
    file_path: str = ""
    worksheets: list = None  # List[WorksheetParsingResult]
    total_worksheets: int = 0
    successful_worksheets: int = 0
    
    def __post_init__(self):
        if self.worksheets is None:
            self.worksheets = []
        self.total_worksheets = len(self.worksheets)
        self.successful_worksheets = len([w for w in self.worksheets if w.data is not None])
    
    @property
    def is_loaded(self) -> bool:
        """Check if data is loaded."""
        return len(self.worksheets) > 0 and self.successful_worksheets > 0
    
    @property
    def total_people_parsed(self) -> int:
        """Get total number of people parsed across all worksheets."""
        return sum(w.people_parsed for w in self.worksheets)
    
    @property
    def total_errors(self) -> int:
        """Get total number of errors across all worksheets."""
        return sum(len(w.errors) for w in self.worksheets)
    
    def get_worksheet_by_name(self, sheet_name: str) -> Optional['WorksheetParsingResult']:
        """Get worksheet by name."""
        for worksheet in self.worksheets:
            if worksheet.metadata.sheet_name == sheet_name:
                return worksheet
        return None


@dataclass
class ExcelValidationResult:
    """Result of Excel file validation."""
    is_valid: bool
    errors: list = None
    warnings: list = None
    message: str = ""
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class GenerationResult:
    """Result of file generation process."""
    success: bool
    files_generated: int = 0
    errors: list = None
    message: str = ""
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


@dataclass
class Prenda:
    """Represents a garment item with its description and quantity."""
    string: str  # Formatted string like "CAMISA TALLA M"
    qty: int     # Quantity of this garment


@dataclass
class GenerationOptions:
    """Options for controlling generation behavior and scope."""
    selected_locales: List[str]
    combine_per_local: bool = False  # False: per person only; True: also generate combined DOCX per local
    cargo_enabled: bool = True  # Generate CARGO documents
    autorizacion_enabled: bool = True  # Generate AUTORIZACION documents


@dataclass
class OccupationPrenda:
    """Represents a prenda that can be assigned to a specific occupation with pricing."""
    prenda_type: str  # e.g., "CAMISA", "BLUSA", "MANDILON"
    display_name: str = ""  # Display name for the prenda
    has_sizes: bool = True  # Whether this prenda has different sizes
    garment_type: str = "UPPER"  # "UPPER" for upper body (uses talla superior), "LOWER" for lower body (uses talla inferior)
    is_required: bool = False  # Whether this prenda is required for the occupation
    default_quantity: int = 0  # Default quantity if not specified
    is_primary: bool = False  # Whether this prenda is the primary one for juegos calculation
    # Pricing for different size groups and local groups
    price_sml_other: float = 0.0  # Price for S/M/L sizes in OTHER local
    price_xl_other: float = 0.0   # Price for XL size in OTHER local
    price_xxl_other: float = 0.0  # Price for XXL size in OTHER local
    price_sml_tarapoto: float = 0.0  # Price for S/M/L sizes in TARAPOTO local
    price_xl_tarapoto: float = 0.0   # Price for XL size in TARAPOTO local
    price_xxl_tarapoto: float = 0.0  # Price for XXL size in TARAPOTO local
    price_sml_san_isidro: float = 0.0  # Price for S/M/L sizes in SAN_ISIDRO local
    price_xl_san_isidro: float = 0.0   # Price for XL size in SAN_ISIDRO local
    price_xxl_san_isidro: float = 0.0  # Price for XXL size in SAN_ISIDRO local


@dataclass
class Occupation:
    """Represents an occupation with its associated prendas and configuration."""
    name: str  # e.g., "MOZO", "AZAFATA", "PACKER"
    display_name: str  # e.g., "Mozo", "Azafata", "Packer"
    synonyms: List[str]  # Alternative names for this occupation
    prendas: List[OccupationPrenda]  # Prendas that can be assigned to this occupation
    is_active: bool = True  # Whether this occupation is currently active
    description: str = ""  # Optional description of the occupation


@dataclass
class UnifiedConfig:
    """Unified configuration combining occupations and their pricing."""
    occupations: List[Occupation]
    default_occupation: str = "MOZO"
    default_local_group: str = "OTHER"
    
    def _determine_local_group(self, local: str) -> str:
        """Determine local group with sanitization for TARAPOTO and SAN ISIDRO."""
        local_upper = local.upper().strip()
        
        # Check for TARAPOTO (exact match or contains "TARAPOTO")
        if local_upper == "TARAPOTO" or "TARAPOTO" in local_upper:
            return "tarapoto"
        
        # Check for SAN ISIDRO (exact match or contains "SAN ISIDRO" or "SAN_ISIDRO")
        if (local_upper in ["SAN ISIDRO", "SAN_ISIDRO"] or 
            "SAN ISIDRO" in local_upper or "SAN_ISIDRO" in local_upper):
            return "san_isidro"
        
        # Default to other
        return "other"
    
    def get_occupation(self, name: str) -> Optional[Occupation]:
        """Get occupation by name (case-insensitive)."""
        name_upper = name.upper().strip()
        for occupation in self.occupations:
            if (occupation.name.upper() == name_upper or 
                name_upper in [syn.upper() for syn in occupation.synonyms]):
                return occupation
        return None
    
    def get_active_occupations(self) -> List[Occupation]:
        """Get all active occupations."""
        return [occ for occ in self.occupations if occ.is_active]
    
    def get_occupation_prendas(self, occupation_name: str) -> List[OccupationPrenda]:
        """Get prendas for a specific occupation."""
        occupation = self.get_occupation(occupation_name)
        return occupation.prendas if occupation else []
    
    def is_valid_occupation(self, name: str) -> bool:
        """Check if an occupation name is valid."""
        return self.get_occupation(name) is not None
    
    def get_occupation_synonyms(self, occupation_name: str) -> List[str]:
        """Get synonyms for an occupation."""
        occupation = self.get_occupation(occupation_name)
        return occupation.synonyms if occupation else [occupation_name]
    
    def get_price(self, prenda_type: str, size: str, cargo: str, local: str) -> float:
        """Get price for a specific combination using unified config."""
        # Normalize inputs
        prenda_type = prenda_type.upper().strip()
        size = size.upper().strip()
        cargo = cargo.upper().strip()
        local = local.upper().strip()
        
        # Find occupation
        occupation = self.get_occupation(cargo)
        if not occupation:
            return 0.0
        
        # Find prenda in occupation
        for prenda in occupation.prendas:
            if prenda.prenda_type.upper() == prenda_type:
                # Determine size group
                if size in ["S", "M", "L", "SML"]:
                    size_group = "sml"
                elif size == "XL":
                    size_group = "xl"
                elif size == "XXL":
                    size_group = "xxl"
                else:
                    size_group = "sml"  # Default fallback
                
                # Determine local group with sanitization
                local_group = self._determine_local_group(local)
                
                # Get price based on size and local group
                price_attr = f"price_{size_group}_{local_group}"
                return getattr(prenda, price_attr, 0.0)
        
        return 0.0  # No price found
