"""
Price Loader Service - loads prices from precios.xlsx and caches them.

This service reads the Precios sheet from the Excel file and builds a price cache
that maps CLAVE (canonical key) to prices. CLAVE format: GRUPO|CARGO|MATERIAL
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Optional, Any, Tuple, List
from datetime import datetime
from difflib import SequenceMatcher

import pandas as pd


# Location group normalization
LOCATION_GROUP_MAP: Dict[str, str] = {
    "LIMA E ICA PROVINCIA": "lima_ica",
    "LIMA E ICA": "lima_ica",
    "TARAPOTO": "tarapoto",
    "PATIO DE COMIDA": "patios_comida",
    "PATIOS DE COMIDA": "patios_comida",
    "VILLA STEAKHOUSE": "villa_steakhouse",
    "SAN ISIDRO": "villa_steakhouse",
}

# Size normalization
SIZE_MAP: Dict[str, str] = {
    "S": "sml",
    "M": "sml",
    "L": "sml",
    "SML": "sml",
    "XL": "xl",
    "XXL": "xxl",
    "2XL": "xxl",
    "3XL": "xxl",
}


class PriceLoader:
    """Service for loading and caching prices from Excel using CLAVE as canonical key."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.prices: Dict[str, float] = {}  # CLAVE|size -> price
        self.clave_metadata: Dict[
            str, Dict
        ] = {}  # CLAVE -> {grupo, cargo, material, gender}
        self.last_updated: Optional[str] = None
        self.source_file: Optional[str] = None

    def _normalize_location(self, grupo: str) -> str:
        """Normalize location group name."""
        grupo_upper = grupo.upper().strip()
        return LOCATION_GROUP_MAP.get(grupo_upper, "lima_ica")

    def _extract_material_keywords(self, material: str) -> List[str]:
        """Extract searchable keywords from material description."""
        material_upper = material.upper().strip()
        # Remove common descriptors and extract core garment type
        keywords = []

        # Primary garment types (in order of priority)
        garment_types = [
            "POLO PIQUÉ",
            "POLO 30/1",
            "POLO 31/1",
            "POLO",
            "CAMISA OXFORD",
            "CAMISA BLANCA",
            "CAMISA NEGRA",
            "CAMISA CHARCOL",
            "CAMISA COLOR",
            "CAMISA",
            "BLUSA BLANCA",
            "BLUSA COLOR",
            "BLUSA A RALLAS",
            "BLUSA OXFORD",
            "BLUSA",
            "PANTALÓN",
            "PANTALON",
            "MANDILÓN",
            "MANDILON",
            "ANDARÍN",
            "ANDARIN",
            "CHAQUETA",
            "PECHERA",
            "GARIBALDI",
            "CHALECO",
            "CORBATA",
            "GORRA",
            "GORRO",
            "SACO",
            "CASACA",
        ]

        for garment in garment_types:
            if garment in material_upper:
                keywords.append(garment.replace("Ó", "O").replace("Í", "I"))
                break

        # Extract color descriptors
        colors = [
            "BLANCA",
            "NEGRA",
            "COLOR",
            "CELESTE",
            "GRIS",
            "AZUL",
            "PLOMO",
            "PIZARRA",
        ]
        for color in colors:
            if color in material_upper:
                keywords.append(color)

        # Extract gender
        if "HOMBRE" in material_upper:
            keywords.append("HOMBRE")
        elif "MUJER" in material_upper:
            keywords.append("MUJER")

        return keywords

    def _detect_gender_from_material(self, material: str) -> Optional[str]:
        """Detect gender from material name."""
        material_upper = material.upper()
        if "HOMBRE" in material_upper:
            return "HOMBRE"
        elif "MUJER" in material_upper:
            return "MUJER"
        return None

    def _make_price_key(self, clave: str, size: str) -> str:
        """Create a unique key for the price cache using CLAVE."""
        return f"{clave}|{size}"

    def load_from_excel(self, excel_path: str) -> bool:
        """Load prices from Excel Precios sheet using CLAVE as canonical key."""
        try:
            path = Path(excel_path)
            if not path.exists():
                self.logger.error(f"Excel file not found: {excel_path}")
                return False

            self.logger.info(f"Loading prices from: {excel_path}")

            # Read Precios sheet
            df = pd.read_excel(excel_path, sheet_name="Precios", header=0)

            # Expected columns: GRUPO, CARGO ESTANDAR, MATERIAL, PRECIO (S,M,L), PRECIO (XL), PRECIO (XXL), CLAVE
            required_cols = ["GRUPO", "CARGO ESTANDAR", "MATERIAL", "CLAVE"]
            for col in required_cols:
                if col not in df.columns:
                    self.logger.error(f"Missing required column: {col}")
                    return False

            self.prices = {}
            self.clave_metadata = {}
            loaded_count = 0

            for _, row in df.iterrows():

                def _scalar(val):
                    if isinstance(val, pd.Series):
                        return val.iloc[0] if len(val) > 0 else ""
                    return val

                grupo = str(_scalar(row["GRUPO"])).strip()
                cargo = str(_scalar(row["CARGO ESTANDAR"])).strip()
                material = str(_scalar(row["MATERIAL"])).strip()
                clave = str(_scalar(row["CLAVE"])).strip()

                if not grupo or not cargo or not material or not clave:
                    continue

                location = self._normalize_location(grupo)
                gender = self._detect_gender_from_material(material)
                keywords = self._extract_material_keywords(material)

                # Store metadata for this CLAVE
                self.clave_metadata[clave] = {
                    "grupo": grupo,
                    "location": location,
                    "cargo": cargo.upper(),
                    "material": material,
                    "gender": gender,
                    "keywords": keywords,
                }

                # Store prices for each size
                for size_col, size_key in [
                    ("PRECIO (S,M,L)", "sml"),
                    ("PRECIO (XL)", "xl"),
                    ("PRECIO (XXL)", "xxl"),
                ]:
                    if size_col not in df.columns:
                        continue
                    price = _scalar(row[size_col])
                    try:
                        price_float = (
                            float(price)
                            if price is not None and str(price) != "nan"
                            else 0.0
                        )
                    except (ValueError, TypeError):
                        price_float = 0.0
                    if price_float > 0:
                        key = self._make_price_key(clave, size_key)
                        self.prices[key] = price_float
                        loaded_count += 1

            self.source_file = str(path.absolute())
            self.last_updated = datetime.now().isoformat()

            self.logger.info(
                f"Loaded {loaded_count} price entries from Excel ({len(self.clave_metadata)} unique CLAVEs)"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to load prices from Excel: {e}")
            return False

    def save_cache(self, cache_path: str) -> bool:
        """Save prices to JSON cache file."""
        try:
            cache_data = {
                "last_updated": self.last_updated,
                "source_file": self.source_file,
                "prices": self.prices,
                "clave_metadata": self.clave_metadata,
            }

            with open(cache_path, "w", encoding="utf-8") as f:
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

            with open(cache_path, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            self.prices = cache_data.get("prices", {})
            self.clave_metadata = cache_data.get("clave_metadata", {})
            self.last_updated = cache_data.get("last_updated")
            self.source_file = cache_data.get("source_file")

            self.logger.info(
                f"Loaded {len(self.prices)} prices from cache ({len(self.clave_metadata)} CLAVEs)"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to load cache: {e}")
            return False

    def get_price_by_clave(self, clave: str, size: str) -> float:
        """Get price for a specific CLAVE and size."""
        size_key = SIZE_MAP.get(size.upper().strip(), "sml")
        key = self._make_price_key(clave, size_key)

        if key in self.prices:
            return self.prices[key]

        self.logger.warning(f"No price found for CLAVE: {clave} size: {size_key}")
        return 0.0

    def find_best_clave(
        self, location_group: str, cargo: str, column_name: str, talla: str = "M"
    ) -> Optional[str]:
        """
        Find the best matching CLAVE based on location, cargo, and column context.

        Args:
            location_group: Location group (e.g., "LIMA E ICA PROVINCIA", "TARAPOTO")
            cargo: Occupation/cargo (e.g., "MOZO", "STAFF ADMINISTRATIVO")
            column_name: Uniform column name (e.g., "LIMA_ICA_SALON_CAMISA")
            talla: Size for gender detection

        Returns:
            Best matching CLAVE string or None
        """
        if not self.clave_metadata:
            return None

        # Normalize inputs
        loc_norm = self._normalize_location(location_group)
        cargo_norm = cargo.upper().strip()
        col_upper = column_name.upper().strip()

        # Extract keywords from column name
        col_keywords = []

        # Extract garment type from column
        garment_patterns = [
            ("CAMISA", "CAMISA"),
            ("BLUSA", "BLUSA"),
            ("POLO", "POLO"),
            ("PANTALON", "PANTALON"),
            ("PANTALÓN", "PANTALON"),
            ("MANDILON", "MANDILON"),
            ("MANDILÓN", "MANDILON"),
            ("ANDARIN", "ANDARIN"),
            ("ANDARÍN", "ANDARIN"),
            ("CHAQUETA", "CHAQUETA"),
            ("PECHERA", "PECHERA"),
            ("GARIBALDI", "GARIBALDI"),
            ("CHALECO", "CHALECO"),
            ("CORBATA", "CORBATA"),
            ("GORRA", "GORRA"),
            ("GORRO", "GORRO"),
            ("SACO", "SACO"),
            ("CASACA", "CASACA"),
        ]

        target_garment = None
        for pattern, garment in garment_patterns:
            if pattern in col_upper:
                col_keywords.append(garment)
                target_garment = garment
                break

        # Detect gender from column name or cargo context
        gender = None
        if "HOMBRE" in col_upper or cargo_norm.endswith("(HOMBRE)"):
            gender = "HOMBRE"
        elif "MUJER" in col_upper or cargo_norm.endswith("(MUJER)"):
            gender = "MUJER"
        elif "BLUSA" in col_upper:
            gender = "MUJER"
        elif "CAMISA" in col_upper and "BLUSA" not in col_upper:
            gender = "HOMBRE"

        if gender:
            col_keywords.append(gender)

        # Score all CLAVEs and find best match
        best_clave = None
        best_score = 0.0

        for clave, metadata in self.clave_metadata.items():
            score = 0.0

            # Location match (highest priority)
            if metadata["location"] == loc_norm:
                score += 100.0

            # Cargo match
            meta_cargo = metadata["cargo"]
            if cargo_norm == meta_cargo:
                score += 50.0
            elif (
                cargo_norm.replace(" (HOMBRE)", "").replace(" (MUJER)", "").strip()
                == meta_cargo
            ):
                score += 40.0

            # Gender match
            if gender and metadata["gender"] == gender:
                score += 30.0

            # Garment type match
            if target_garment:
                meta_material = metadata["material"].upper()
                if target_garment in meta_material:
                    score += 20.0
                    # Bonus for exact match at start
                    if meta_material.startswith(target_garment):
                        score += 10.0

            # Keyword overlap
            meta_keywords = set(metadata["keywords"])
            col_keywords_set = set(col_keywords)
            if meta_keywords and col_keywords_set:
                overlap = len(meta_keywords & col_keywords_set)
                score += overlap * 5.0

            if score > best_score:
                best_score = score
                best_clave = clave

        if best_clave and best_score >= 50.0:  # Minimum threshold
            self.logger.debug(
                f"Matched column '{column_name}' to CLAVE '{best_clave}' (score: {best_score})"
            )
            return best_clave

        self.logger.warning(
            f"No good CLAVE match for {loc_norm}/{cargo_norm}/{column_name} (best score: {best_score})"
        )
        return None

    def get_price(
        self,
        occupation: str,
        prenda_type: str,
        size: str,
        location: str,
        clave: Optional[str] = None,
    ) -> float:
        """
        Get price for a specific combination.

        If clave is provided, uses direct CLAVE lookup.
        Otherwise falls back to legacy key format.
        """
        # If CLAVE provided, use direct lookup
        if clave:
            return self.get_price_by_clave(clave, size)

        # Legacy fallback (should not be used with new system)
        occ = occupation.upper().strip()
        prenda = prenda_type.upper().strip()
        size_key = SIZE_MAP.get(size.upper().strip(), "sml")
        loc = self._normalize_location(location) if location else "lima_ica"

        # Try to find matching CLAVE
        best_clave = self.find_best_clave(location, occupation, prenda, size)
        if best_clave:
            return self.get_price_by_clave(best_clave, size)

        self.logger.warning(f"No price found for: {occ}/{prenda}/{size_key}/{loc}")
        return 0.0

    def get_price_summary(self) -> Dict[str, Any]:
        """Get summary of loaded prices."""
        locations = set()
        cargos = set()
        materials = set()

        for clave, metadata in self.clave_metadata.items():
            locations.add(metadata["location"])
            cargos.add(metadata["cargo"])
            materials.add(metadata["material"])

        return {
            "total_entries": len(self.prices),
            "unique_claves": len(self.clave_metadata),
            "locations": sorted(locations),
            "cargos": sorted(cargos),
            "occupations": sorted(cargos),
            "prendas": sorted(materials),
            "materials_count": len(materials),
            "last_updated": self.last_updated,
            "source_file": self.source_file,
        }

    def get_claves_for_location_cargo(
        self, location_group: str, cargo: str
    ) -> List[Tuple[str, str, float]]:
        """
        Get all CLAVEs and their SML prices for a location/cargo combination.

        Returns:
            List of (clave, material, price) tuples
        """
        loc_norm = self._normalize_location(location_group)
        cargo_norm = cargo.upper().strip()
        results = []

        for clave, metadata in self.clave_metadata.items():
            if metadata["location"] == loc_norm and metadata["cargo"] == cargo_norm:
                price = self.get_price_by_clave(clave, "sml")
                if price > 0:
                    results.append((clave, metadata["material"], price))

        return sorted(results, key=lambda x: x[1])  # Sort by material name
