"""
Price Service - Loads and manages pricing data from Excel source files.
"""
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, Optional, Any


class PriceService:
    """Service for loading and managing pricing data from Excel source files."""
    
    DEFAULT_PRICE_FILE = "sources/precios.xlsm"
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self._price_cache: Dict[str, Dict[str, Dict[str, float]]] = {}
        self._last_loaded_file: Optional[str] = None
    
    def load_prices_from_excel(self, file_path: Optional[str] = None) -> bool:
        """
        Load prices from an Excel file.
        
        Args:
            file_path: Path to the Excel file. Uses DEFAULT_PRICE_FILE if not provided.
            
        Returns:
            True if prices were loaded successfully, False otherwise.
        """
        if file_path is None:
            file_path = self.DEFAULT_PRICE_FILE
        
        try:
            if not Path(file_path).exists():
                self.logger.warning(f"Price file not found: {file_path}")
                return False
            
            self.logger.info(f"Loading prices from: {file_path}")
            
            # Read the Movimientos sheet
            df = pd.read_excel(file_path, sheet_name='Movimientos', engine='openpyxl')
            
            # Get unique prices
            prices = df[['GRUPO', 'CARGO ESTANDAR', 'MATERIAL', 'TALLA', 'Precio Unit']].drop_duplicates()
            
            # Build price cache: location_group -> occupation -> prenda_type -> size -> price
            self._price_cache = {}
            
            for _, row in prices.iterrows():
                grupo = self._normalize_location_group(row['GRUPO'])
                cargo = self._normalize_occupation(row['CARGO ESTANDAR'])
                prenda_type = self._normalize_prenda_type(row['MATERIAL'])
                talla = self._normalize_talla(row['TALLA'])
                price = float(row['Precio Unit'])
                
                if grupo not in self._price_cache:
                    self._price_cache[grupo] = {}
                if cargo not in self._price_cache[grupo]:
                    self._price_cache[grupo][cargo] = {}
                if prenda_type not in self._price_cache[grupo][cargo]:
                    self._price_cache[grupo][cargo][prenda_type] = {}
                
                self._price_cache[grupo][cargo][prenda_type][talla] = price
            
            self._last_loaded_file = file_path
            self.logger.info(f"Loaded {len(prices)} price entries from {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load prices from {file_path}: {e}")
            return False
    
    def get_price(self, location_group: str, occupation: str, prenda_type: str, size: str) -> Optional[float]:
        """
        Get price for a specific combination.
        
        Args:
            location_group: Location group (e.g., "lima_ica", "patios_comida")
            occupation: Occupation name (e.g., "MOZO", "PRODUCCION")
            prenda_type: Prenda type (e.g., "POLO", "CAMISA")
            size: Size (e.g., "sml", "xl", "xxl")
            
        Returns:
            Price if found, None otherwise.
        """
        location_group = location_group.lower()
        occupation = self._normalize_occupation(occupation)
        prenda_type = prenda_type.upper()
        size = size.lower()
        
        try:
            return self._price_cache.get(location_group, {}).get(occupation, {}).get(prenda_type, {}).get(size)
        except Exception:
            return None
    
    def get_all_prices(self) -> Dict[str, Any]:
        """Get all cached prices."""
        return self._price_cache
    
    def get_price_summary(self) -> Dict[str, int]:
        """Get summary of loaded prices."""
        summary = {
            "total_entries": 0,
            "location_groups": len(self._price_cache),
            "occupations": 0,
            "prenda_types": 0,
        }
        
        occupations = set()
        prenda_types = set()
        
        for grupo, cargos in self._price_cache.items():
            for cargo, prendas in cargos.items():
                occupations.add(cargo)
                for prenda, sizes in prendas.items():
                    prenda_types.add(prenda)
                    summary["total_entries"] += len(sizes)
        
        summary["occupations"] = len(occupations)
        summary["prenda_types"] = len(prenda_types)
        
        return summary
    
    def generate_config_updates(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Generate config.json-compatible price updates.
        
        Returns:
            Dict with structure: occupation -> prenda_type -> price_field -> price
            e.g., {"MOZO": {"CAMISA": {"price_sml_lima_ica": 18.5}}}
        """
        updates = {}
        
        for location_group, cargos in self._price_cache.items():
            for cargo, prendas in cargos.items():
                if cargo not in updates:
                    updates[cargo] = {}
                
                for prenda_type, sizes in prendas.items():
                    if prenda_type not in updates[cargo]:
                        updates[cargo][prenda_type] = {}
                    
                    for size, price in sizes.items():
                        price_key = f"price_{size}_{location_group}"
                        updates[cargo][prenda_type][price_key] = price
        
        return updates
    
    def _normalize_location_group(self, grupo: str) -> str:
        """Normalize location group name."""
        grupo_upper = str(grupo).upper()
        
        if 'LIMA' in grupo_upper or 'ICA' in grupo_upper:
            return 'lima_ica'
        elif 'PATIO' in grupo_upper:
            return 'patios_comida'
        elif 'VILLA' in grupo_upper or 'SAN ISIDRO' in grupo_upper:
            return 'villa_steakhouse'
        else:
            return 'other'
    
    def _normalize_occupation(self, cargo: str) -> str:
        """Normalize occupation name."""
        cargo_upper = str(cargo).upper().strip()
        
        # Map common variations
        occupation_map = {
            'PRODUCCIÓN / COCINA': 'PRODUCCION',
            'PRODUCCION / COCINA': 'PRODUCCION',
            'STAFF ADMINISTRATIVO': 'ADMINISTRACION',
        }
        
        return occupation_map.get(cargo_upper, cargo_upper.replace(' / ', '_').replace(' ', '_'))
    
    def _normalize_prenda_type(self, material: str) -> str:
        """Normalize material name to prenda type."""
        material_upper = str(material).upper()
        
        known_prendas = {
            'POLO': ['POLO'],
            'CAMISA': ['CAMISA'],
            'BLUSA': ['BLUSA'],
            'CHAQUETA': ['CHAQUETA'],
            'PANTALON': ['PANTALON', 'PANTALÓN'],
            'PECHERA': ['PECHERA'],
            'GARIBALDI': ['GARIBALDI'],
            'MANDILON': ['MANDILON', 'MANDILÓN'],
            'ANDARIN': ['ANDARIN'],
            'SACO': ['SACO'],
            'GORRA': ['GORRA', 'GORRO'],
            'CASACA': ['CASACA'],
        }
        
        for prenda_type, keywords in known_prendas.items():
            for keyword in keywords:
                if keyword in material_upper:
                    return prenda_type
        
        return 'OTHER'
    
    def _normalize_talla(self, talla: str) -> str:
        """Normalize size value."""
        talla_upper = str(talla).upper().strip()
        
        if talla_upper in ['S', 'M', 'L', 'SML']:
            return 'sml'
        elif talla_upper == 'XL':
            return 'xl'
        elif talla_upper in ['XXL', '2XL']:
            return 'xxl'
        else:
            return 'sml'  # Default to SML
