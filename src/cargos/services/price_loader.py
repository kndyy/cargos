"""
Price Loader Service - loads prices from precios.xlsx and caches them.

This service reads the Precios sheet from the Excel file and builds a price cache
that maps (occupation, prenda_type, size, location_group) to prices.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

import pandas as pd


# Material name to prenda_type mapping
MATERIAL_TO_PRENDA: Dict[str, str] = {
    # Polo variants
    'POLO PIQUÉ': 'POLO',
    'POLO 30/1': 'POLO',
    'POLO 31/1': 'POLO',
    # Camisa variants
    'CAMISA BLANCA': 'CAMISA',
    'CAMISA OXFORD': 'CAMISA',
    'CAMISA NEGRA': 'CAMISA',
    'CAMISA CHARCOL': 'CAMISA',
    'CAMISA COLOR': 'CAMISA',
    # Blusa variants
    'BLUSA BLANCA': 'BLUSA',
    'BLUSA COLOR': 'BLUSA',
    'BLUSA A RALLAS': 'BLUSA',
    'BLUSA OXFORD': 'BLUSA',
    # Other prendas
    'CASACA': 'CASACA',
    'CHAQUETA': 'CHAQUETA',
    'PANTALÓN': 'PANTALON',
    'PANTALON': 'PANTALON',
    'GORRO': 'GORRO',
    'GORRA': 'GORRA',
    'SACO': 'SACO',
    'MANDILON': 'MANDILON',
    'MANDILÓN': 'MANDILON',
    'ANDARIN': 'ANDARIN',
    'ANDARÍN': 'ANDARIN',
    'PECHERA': 'PECHERA',
    'GARIBALDI': 'GARIBALDI',
    'CHALECO': 'CHALECO',
    'CORBATA': 'CORBATA',
}

# Location group normalization
LOCATION_GROUP_MAP: Dict[str, str] = {
    'LIMA E ICA PROVINCIA': 'lima_ica',
    'LIMA E ICA': 'lima_ica',
    'TARAPOTO': 'tarapoto',
    'PATIO DE COMIDA': 'patios_comida',
    'PATIOS DE COMIDA': 'patios_comida',
    'VILLA STEAKHOUSE': 'villa_steakhouse',
    'SAN ISIDRO': 'villa_steakhouse',
}

# Size normalization
SIZE_MAP: Dict[str, str] = {
    'S': 'sml',
    'M': 'sml',
    'L': 'sml',
    'SML': 'sml',
    'XL': 'xl',
    'XXL': 'xxl',
    '2XL': 'xxl',
    '3XL': 'xxl',
}


class PriceLoader:
    """Service for loading and caching prices from Excel."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.prices: Dict[str, float] = {}
        self.last_updated: Optional[str] = None
        self.source_file: Optional[str] = None
        
    def _normalize_prenda_type(self, material: str) -> str:
        """Extract prenda type from material name."""
        material_upper = material.upper().strip()
        
        # Check prefixes in order of specificity
        for prefix, prenda_type in sorted(MATERIAL_TO_PRENDA.items(), key=lambda x: -len(x[0])):
            if material_upper.startswith(prefix):
                return prenda_type
        
        # Fallback: check if any keyword is contained
        for keyword, prenda_type in MATERIAL_TO_PRENDA.items():
            if keyword in material_upper:
                return prenda_type
        
        # If no match, use first word
        return material_upper.split()[0] if material_upper else 'UNKNOWN'
    
    def _detect_gender_from_material(self, material: str) -> Optional[str]:
        """Detect gender from material name."""
        material_upper = material.upper()
        if 'HOMBRE' in material_upper:
            return 'HOMBRE'
        elif 'MUJER' in material_upper:
            return 'MUJER'
        # Blusa is typically female, Camisa is typically male
        elif 'BLUSA' in material_upper:
            return 'MUJER'
        elif 'CAMISA' in material_upper:
            return 'HOMBRE'
        return None
    
    def _normalize_location(self, grupo: str) -> str:
        """Normalize location group name."""
        grupo_upper = grupo.upper().strip()
        return LOCATION_GROUP_MAP.get(grupo_upper, 'other')
    
    def _normalize_occupation(self, cargo: str) -> str:
        """Normalize occupation name."""
        return cargo.upper().strip()
    
    def _make_price_key(self, occupation: str, prenda_type: str, size: str, location: str) -> str:
        """Create a unique key for the price cache."""
        return f"{occupation}|{prenda_type}|{size}|{location}"
    
    def load_from_excel(self, excel_path: str) -> bool:
        """Load prices from Excel Precios sheet."""
        try:
            path = Path(excel_path)
            if not path.exists():
                self.logger.error(f"Excel file not found: {excel_path}")
                return False
            
            self.logger.info(f"Loading prices from: {excel_path}")
            
            # Read Precios sheet
            df = pd.read_excel(excel_path, sheet_name='Precios', header=0)
            
            # Expected columns from precios.xlsx Precios sheet
            # Actual headers: GRUPO, CARGO ESTANDAR, MATERIAL, PRECIO (S,M,L), PRECIO (XL), PRECIO (XXL), CLAVE
            col_mapping = {
                'GRUPO': 'GRUPO',
                'CARGO ESTANDAR': 'CARGO ESTANDAR',
                'MATERIAL': 'MATERIAL',
                'SML': 'PRECIO (S,M,L)',
                'XL': 'PRECIO (XL)',
                'XXL': 'PRECIO (XXL)',
            }
            
            for required, actual in [('GRUPO', 'GRUPO'), ('CARGO ESTANDAR', 'CARGO ESTANDAR'), ('MATERIAL', 'MATERIAL')]:
                if actual not in df.columns:
                    self.logger.error(f"Missing required column: {actual}")
                    return False
            
            self.prices = {}
            loaded_count = 0
            
            for _, row in df.iterrows():
                grupo = str(row['GRUPO']).strip()
                cargo = str(row['CARGO ESTANDAR']).strip()
                material = str(row['MATERIAL']).strip()
                
                if not grupo or not cargo or not material:
                    continue
                
                location = self._normalize_location(grupo)
                occupation = self._normalize_occupation(cargo)
                prenda_type = self._normalize_prenda_type(material)
                gender = self._detect_gender_from_material(material)
                
                # Add gender suffix to occupation if detected
                if gender:
                    occupation_with_gender = f"{occupation} ({gender})"
                    # Store both with and without gender
                    occupations_to_store = [occupation, occupation_with_gender]
                else:
                    occupations_to_store = [occupation]
                
                # Store prices for each size
                for size_col, size_key in [('PRECIO (S,M,L)', 'sml'), ('PRECIO (XL)', 'xl'), ('PRECIO (XXL)', 'xxl')]:
                    if size_col not in df.columns:
                        continue
                    price = row[size_col]
                    if pd.notna(price) and float(price) > 0:
                        for occ in occupations_to_store:
                            key = self._make_price_key(occ, prenda_type, size_key, location)
                            self.prices[key] = float(price)
                            loaded_count += 1
            
            self.source_file = str(path.absolute())
            self.last_updated = datetime.now().isoformat()
            
            self.logger.info(f"Loaded {loaded_count} price entries from Excel")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load prices from Excel: {e}")
            return False
    
    def save_cache(self, cache_path: str) -> bool:
        """Save prices to JSON cache file."""
        try:
            cache_data = {
                'last_updated': self.last_updated,
                'source_file': self.source_file,
                'prices': self.prices,
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(self.prices)} prices to cache: {cache_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save cache: {e}")
            return False
    
    def load_cache(self, cache_path: str) -> bool:
        """Load prices from JSON cache file."""
        try:
            path = Path(cache_path)
            if not path.exists():
                self.logger.info(f"No cache file found: {cache_path}")
                return False
            
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            self.prices = cache_data.get('prices', {})
            self.last_updated = cache_data.get('last_updated')
            self.source_file = cache_data.get('source_file')
            
            self.logger.info(f"Loaded {len(self.prices)} prices from cache")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load cache: {e}")
            return False
    
    def get_price(self, occupation: str, prenda_type: str, size: str, location: str) -> float:
        """Get price for a specific combination."""
        # Normalize inputs
        occ = occupation.upper().strip()
        prenda = prenda_type.upper().strip()
        size_key = SIZE_MAP.get(size.upper().strip(), 'sml')
        loc = self._normalize_location(location) if location else 'lima_ica'
        
        # Try exact match first
        key = self._make_price_key(occ, prenda, size_key, loc)
        if key in self.prices:
            return self.prices[key]
        
        # Try without gender suffix
        occ_base = occ.replace(' (HOMBRE)', '').replace(' (MUJER)', '').strip()
        key_base = self._make_price_key(occ_base, prenda, size_key, loc)
        if key_base in self.prices:
            return self.prices[key_base]
        
        # Try fallback locations
        fallback_locs = ['lima_ica', 'other']
        for fallback_loc in fallback_locs:
            if fallback_loc != loc:
                key = self._make_price_key(occ, prenda, size_key, fallback_loc)
                if key in self.prices:
                    return self.prices[key]
                key_base = self._make_price_key(occ_base, prenda, size_key, fallback_loc)
                if key_base in self.prices:
                    return self.prices[key_base]
        
        # No price found
        self.logger.warning(f"No price found for: {occ}/{prenda}/{size_key}/{loc}")
        return 0.0
    
    def get_price_summary(self) -> Dict[str, Any]:
        """Get summary of loaded prices."""
        occupations = set()
        prendas = set()
        locations = set()
        
        for key in self.prices:
            parts = key.split('|')
            if len(parts) == 4:
                occupations.add(parts[0])
                prendas.add(parts[1])
                locations.add(parts[3])
        
        return {
            'total_entries': len(self.prices),
            'occupations': sorted(occupations),
            'prendas': sorted(prendas),
            'locations': sorted(locations),
            'last_updated': self.last_updated,
            'source_file': self.source_file,
        }
    
    def get_gendered_prices(self, occupation_base: str, location: str) -> Dict[str, Dict[str, float]]:
        """Get sample prices for both male and female variants of an occupation.
        
        Args:
            occupation_base: Base occupation name (e.g., "STAFF ADMINISTRATIVO")
            location: Location group string
        
        Returns:
            {
                'HOMBRE': {'CAMISA': 18.0, 'SACO': 35.0, ...},
                'MUJER': {'BLUSA': 18.0, 'SACO': 35.0, ...}
            }
        """
        loc = self._normalize_location(location) if location else 'lima_ica'
        occ_base = occupation_base.upper().strip()
        
        result = {'HOMBRE': {}, 'MUJER': {}}
        
        # Look for prices with gender suffix
        for key, price in self.prices.items():
            parts = key.split('|')
            if len(parts) != 4:
                continue
            
            occ, prenda, size, key_loc = parts
            
            # Only get SML prices for sample
            if size != 'sml':
                continue
            
            # Check if location matches
            if key_loc != loc:
                continue
            
            # Check occupation
            if occ == f"{occ_base} (HOMBRE)":
                result['HOMBRE'][prenda] = price
            elif occ == f"{occ_base} (MUJER)":
                result['MUJER'][prenda] = price
            elif occ == occ_base:
                # Base occupation without gender - check prenda type
                if prenda in ['CAMISA']:
                    result['HOMBRE'][prenda] = price
                elif prenda in ['BLUSA']:
                    result['MUJER'][prenda] = price
                else:
                    # Same for both
                    result['HOMBRE'][prenda] = price
                    result['MUJER'][prenda] = price
        
        return result
    
    def is_gendered_occupation(self, occupation: str) -> bool:
        """Check if an occupation has both male and female price variants."""
        occ_base = occupation.upper().strip().replace(' (HOMBRE)', '').replace(' (MUJER)', '')
        
        has_male = False
        has_female = False
        
        for key in self.prices:
            if f"{occ_base} (HOMBRE)|" in key:
                has_male = True
            if f"{occ_base} (MUJER)|" in key:
                has_female = True
            if has_male and has_female:
                return True
        
        return False


# Test when run directly
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    loader = PriceLoader()
    
    if loader.load_from_excel('sources/precios.xlsx'):
        loader.save_cache('prices_cache.json')
        
        summary = loader.get_price_summary()
        print(f"\nPrice Summary:")
        print(f"  Total entries: {summary['total_entries']}")
        print(f"  Occupations: {len(summary['occupations'])}")
        print(f"  Prendas: {len(summary['prendas'])}")
        print(f"  Locations: {summary['locations']}")
        
        # Test some lookups
        print(f"\nTest lookups:")
        print(f"  MOZO/CAMISA/SML/lima_ica: S/{loader.get_price('MOZO', 'CAMISA', 'SML', 'LIMA E ICA'):.2f}")
        print(f"  AZAFATA/BLUSA/XL/lima_ica: S/{loader.get_price('AZAFATA', 'BLUSA', 'XL', 'LIMA E ICA'):.2f}")
        print(f"  PRODUCCIÓN / COCINA/CHAQUETA/XXL/tarapoto: S/{loader.get_price('PRODUCCIÓN / COCINA', 'CHAQUETA', 'XXL', 'TARAPOTO'):.2f}")
