"""
Unified configuration service for managing occupations and pricing.
"""
from __future__ import annotations

import logging
from typing import List, Optional, Dict

from cargos.core.models import UnifiedConfig, Occupation, OccupationPrenda, AppConfig
from cargos.services.config_manager import ConfigManager


class UnifiedConfigService:
    """Service for managing unified configuration (occupations and pricing)."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.config_manager = ConfigManager()
        self.unified_config = self._load_config()

    def _load_config(self) -> UnifiedConfig:
        data = self.config_manager.load_unified_config_data()
        occupations: List[Occupation] = []

        for occ_data in data.get("occupations", []):
            prendas: List[OccupationPrenda] = []
            for prenda_data in occ_data.get("prendas", []):
                try:
                    # Determine garment type if not specified
                    garment_type = prenda_data.get("garment_type", "UPPER")
                    if not garment_type:
                        # Auto-detect based on prenda type
                        prenda_type_upper = prenda_data["prenda_type"].upper()
                        if any(lower in prenda_type_upper for lower in ["PANTALON", "PANTALÓN", "PANTS"]):
                            garment_type = "LOWER"
                        else:
                            garment_type = "UPPER"
                    
                    prendas.append(
                        OccupationPrenda(
                            prenda_type=prenda_data["prenda_type"],
                            display_name=prenda_data.get("display_name", ""),
                            has_sizes=prenda_data.get("has_sizes", True),
                            garment_type=garment_type,
                            is_required=prenda_data.get("is_required", False),
                            default_quantity=prenda_data.get("default_quantity", 0),
                            is_primary=prenda_data.get("is_primary", False),
                            price_sml_other=prenda_data.get("price_sml_other", 0.0),
                            price_xl_other=prenda_data.get("price_xl_other", 0.0),
                            price_xxl_other=prenda_data.get("price_xxl_other", 0.0),
                            price_sml_tarapoto=prenda_data.get("price_sml_tarapoto", 0.0),
                            price_xl_tarapoto=prenda_data.get("price_xl_tarapoto", 0.0),
                            price_xxl_tarapoto=prenda_data.get("price_xxl_tarapoto", 0.0),
                            price_sml_san_isidro=prenda_data.get("price_sml_san_isidro", 0.0),
                            price_xl_san_isidro=prenda_data.get("price_xl_san_isidro", 0.0),
                            price_xxl_san_isidro=prenda_data.get("price_xxl_san_isidro", 0.0),
                        )
                    )
                except KeyError as error:
                    self.logger.warning(f"Skipping prenda with missing data: {error}")

            occupations.append(
                Occupation(
                    name=occ_data["name"],
                    display_name=occ_data.get("display_name", occ_data["name"]),
                    synonyms=occ_data.get("synonyms", []),
                    prendas=prendas,
                    is_active=occ_data.get("is_active", True),
                    description=occ_data.get("description", ""),
                )
            )

        return UnifiedConfig(
            occupations=occupations,
            default_occupation=data.get("default_occupation", "MOZO"),
            default_local_group=data.get("default_local_group", "OTHER"),
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self, config: Optional[AppConfig] = None, unified_config: Optional[UnifiedConfig] = None) -> bool:
        if config is None:
            config = self.config_manager.load_config()
        if unified_config is not None:
            self.unified_config = unified_config
        return self.config_manager.save_config(config, self.unified_config)

    def reload(self) -> UnifiedConfig:
        self.unified_config = self._load_config()
        return self.unified_config

    def get_app_config(self) -> AppConfig:
        return self.config_manager.load_config()

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------
    def get_occupation(self, name: str) -> Optional[Occupation]:
        name_upper = name.upper().strip()
        for occupation in self.unified_config.occupations:
            if occupation.name.upper() == name_upper:
                return occupation
            for synonym in occupation.synonyms:
                if synonym.upper() == name_upper:
                    return occupation
        return None

    def get_primary_prenda(self, occupation_name: str) -> Optional[OccupationPrenda]:
        """Get the primary prenda for an occupation (used for juegos calculation)."""
        occupation = self.get_occupation(occupation_name)
        if not occupation:
            return None
        # Find the prenda with is_primary=True
        primary_prenda = next((p for p in occupation.prendas if p.is_primary), None)
        return primary_prenda

    def get_occupation_synonyms(self, occupation_name: str) -> List[str]:
        occupation = self.get_occupation(occupation_name)
        return occupation.synonyms if occupation else [occupation_name]

    def normalize_occupation(self, cargo: str) -> str:
        occupation = self.get_occupation(cargo)
        return occupation.name if occupation else cargo.upper()

    def calculate_total_price(self, prendas: List[Dict], cargo: str, local: str, local_group: Optional[str] = None) -> float:
        """
        Calculate total price for a list of prendas.
        
        Args:
            prendas: List of dictionaries with 'prenda_type', 'qty', and 'string'
            cargo: Occupation name or synonym
            local: Specific locale/tienda string
            local_group: Optional location group string from Excel (e.g. "LIMA E ICA PROVINCIA")
        """
        total = 0.0
        occupation = self.get_occupation(cargo)
        if not occupation:
            self.logger.warning(f"No occupation found for cargo: {cargo}")
            return total

        # Determine location group - prefer explicit local_group if provided
        loc_str = local_group if local_group else local
        
        self.logger.info(f"Calculating price for {cargo} -> {occupation.name} in {loc_str}")
        
        for prenda in prendas:
            qty = prenda.get("qty", 0)
            if qty <= 0:
                continue

            prenda_type = prenda.get("prenda_type", "").upper().strip()
            size = self._extract_size(prenda.get("string", ""))
            prenda_string = prenda.get("string", "")

            # Get the price using the model's logic
            # Signature: get_price(prenda_type, size, cargo, local)
            price = self.unified_config.get_price(prenda_type, size, occupation.name, loc_str)
            
            subtotal = price * qty
            total += subtotal
            
            if price > 0:
                self.logger.info(f"  {prenda_string}: {prenda_type} TALLA {size} x{qty} = {price} x {qty} = {subtotal}")
            else:
                self.logger.warning(f"  ⚠️ NO PRICE FOUND for {prenda_type} (size {size}) in {occupation.name} at {loc_str}")
            
        self.logger.info(f"Total price for {cargo}: {total}")
        return total

    def _resolve_price(self, prenda_cfg: OccupationPrenda, size: str, local: str) -> float:
        """Deprecated: use unified_config.get_price instead."""
        return self.unified_config.get_price("", prenda_cfg.prenda_type, size, local)

    def _extract_size(self, name: str) -> str:
        name = name.upper()
        if "TALLA" in name:
            parts = name.split("TALLA")
            if len(parts) > 1:
                size = parts[1].strip().split()[0]
                if size in {"S", "M", "L", "XL", "XXL"}:
                    return size
        return "M"

    def get_configuration_matrix(self) -> List[Dict]:
        """Get a flat list of all pricing configurations for display in UI."""
        matrix = []
        
        for occupation in self.unified_config.occupations:
            for prenda in occupation.prendas:
                # Add entries for each size group and local combination
                for size_group in ["S/M/L", "XL", "XXL"]:
                    for local_group, local_name in [("other", "OTHER"), ("tarapoto", "TARAPOTO"), ("san_isidro", "SAN ISIDRO")]:
                        # Get the price for this combination
                        if size_group == "S/M/L":
                            price = getattr(prenda, f"price_sml_{local_group}", 0.0)
                        elif size_group == "XL":
                            price = getattr(prenda, f"price_xl_{local_group}", 0.0)
                        else:  # XXL
                            price = getattr(prenda, f"price_xxl_{local_group}", 0.0)
                        
                        matrix.append({
                            "occupation_display": occupation.display_name,
                            "occupation_name": occupation.name,
                            "prenda_type": prenda.display_name or prenda.prenda_type,
                            "size_group": size_group,
                            "local_group": local_name,
                            "price": price
                        })
        
        return matrix

    def get_all_occupations(self) -> List[Occupation]:
        """Get all occupations."""
        return self.unified_config.occupations

    def add_occupation(self, occupation: Occupation) -> bool:
        """Add a new occupation to the configuration."""
        # Check if occupation already exists
        if any(occ.name == occupation.name for occ in self.unified_config.occupations):
            self.logger.warning(f"Occupation {occupation.name} already exists")
            return False
        
        self.unified_config.occupations.append(occupation)
        return True

    def update_occupation(self, occupation: Occupation) -> bool:
        """Update an existing occupation."""
        for i, occ in enumerate(self.unified_config.occupations):
            if occ.name == occupation.name:
                self.unified_config.occupations[i] = occupation
                return True
        return False

    def delete_occupation(self, occupation_name: str) -> bool:
        """Delete an occupation."""
        self.unified_config.occupations = [
            occ for occ in self.unified_config.occupations 
            if occ.name != occupation_name
        ]
        return True

    def add_prenda_to_occupation(self, occupation_name: str, prenda: OccupationPrenda) -> bool:
        """Add a prenda to an existing occupation."""
        occupation = self.get_occupation(occupation_name)
        if not occupation:
            self.logger.error(f"Occupation {occupation_name} not found")
            return False
        
        # Check if prenda already exists
        if any(p.prenda_type == prenda.prenda_type for p in occupation.prendas):
            self.logger.warning(f"Prenda {prenda.prenda_type} already exists in {occupation_name}")
            return False
        
        occupation.prendas.append(prenda)
        return True

    def update_prenda_in_occupation(self, occupation_name: str, prenda: OccupationPrenda) -> bool:
        """Update a prenda in an occupation."""
        occupation = self.get_occupation(occupation_name)
        if not occupation:
            self.logger.error(f"Occupation {occupation_name} not found")
            return False
        
        for i, p in enumerate(occupation.prendas):
            if p.prenda_type == prenda.prenda_type:
                occupation.prendas[i] = prenda
                return True
        
        self.logger.warning(f"Prenda {prenda.prenda_type} not found in {occupation_name}")
        return False

    def delete_prenda_from_occupation(self, occupation_name: str, prenda_type: str) -> bool:
        """Delete a prenda from an occupation."""
        occupation = self.get_occupation(occupation_name)
        if not occupation:
            self.logger.error(f"Occupation {occupation_name} not found")
            return False
        
        occupation.prendas = [p for p in occupation.prendas if p.prenda_type != prenda_type]
        return True

    def add_synonym_to_occupation(self, occupation_name: str, synonym: str) -> bool:
        """Add a synonym to an occupation."""
        occupation = self.get_occupation(occupation_name)
        if not occupation:
            self.logger.error(f"Occupation {occupation_name} not found")
            return False
        
        synonym_upper = synonym.upper().strip()
        if synonym_upper not in occupation.synonyms:
            occupation.synonyms.append(synonym_upper)
            return True
        
        self.logger.warning(f"Synonym {synonym} already exists in {occupation_name}")
        return False

    def remove_synonym_from_occupation(self, occupation_name: str, synonym: str) -> bool:
        """Remove a synonym from an occupation."""
        occupation = self.get_occupation(occupation_name)
        if not occupation:
            self.logger.error(f"Occupation {occupation_name} not found")
            return False
        
        synonym_upper = synonym.upper().strip()
        if synonym_upper in occupation.synonyms:
            occupation.synonyms.remove(synonym_upper)
            return True
        
        return False

    def get_prenda_from_occupation(self, occupation_name: str, prenda_type: str) -> Optional[OccupationPrenda]:
        """Get a specific prenda from an occupation."""
        occupation = self.get_occupation(occupation_name)
        if not occupation:
            return None
        
        for prenda in occupation.prendas:
            if prenda.prenda_type.upper() == prenda_type.upper():
                return prenda
        
        return None

    def update_prenda_pricing(self, occupation_name: str, prenda_type: str, 
                               size_group: str, local_group: str, price: float) -> bool:
        """
        Update pricing for a specific prenda.
        
        Args:
            occupation_name: Name of the occupation (e.g., "MOZO", "PRODUCCION")
            prenda_type: Type of prenda (e.g., "POLO", "CAMISA")
            size_group: Size group (e.g., "sml", "xl", "xxl")
            local_group: Location group (e.g., "other", "tarapoto", "san_isidro", "lima_ica", "patios_comida")
            price: New price value
            
        Returns:
            True if price was updated, False otherwise.
        """
        prenda = self.get_prenda_from_occupation(occupation_name, prenda_type)
        if not prenda:
            # Try to find occupation and add the prenda if it doesn't exist
            occupation = self.get_occupation(occupation_name)
            if not occupation:
                self.logger.warning(f"Occupation {occupation_name} not found for pricing update")
                return False
            
            # Create new prenda with this price
            new_prenda = OccupationPrenda(prenda_type=prenda_type)
            occupation.prendas.append(new_prenda)
            prenda = new_prenda
            self.logger.info(f"Created new prenda {prenda_type} in {occupation_name}")
        
        # Build the price attribute name
        # Map new location groups to old field names if needed
        local_mapping = {
            'lima_ica': 'other',
            'patios_comida': 'other',
            'villa_steakhouse': 'san_isidro',
        }
        
        # Use mapped local if available, otherwise use original
        mapped_local = local_mapping.get(local_group.lower(), local_group.lower())
        
        # Normalize size_group
        size_norm = size_group.lower()
        if size_norm in ['s', 'm', 'l', 's/m/l']:
            size_norm = 'sml'
        
        price_attr = f"price_{size_norm}_{mapped_local}"
        
        # Check if attribute exists
        if hasattr(prenda, price_attr):
            setattr(prenda, price_attr, price)
            self.logger.debug(f"Updated {occupation_name}/{prenda_type} {price_attr} = {price}")
            return True
        else:
            self.logger.warning(f"Price attribute {price_attr} not found on prenda")
            return False

    def validate_occupation(self, occupation: Occupation) -> List[str]:
        """
        Validate an occupation configuration.
        Returns a list of validation errors (empty if valid).
        """
        errors = []
        
        if not occupation.name or not occupation.name.strip():
            errors.append("Occupation name is required")
        
        if not occupation.display_name or not occupation.display_name.strip():
            errors.append("Occupation display name is required")
        
        if not occupation.synonyms or len(occupation.synonyms) == 0:
            errors.append("At least one synonym is required")
        
        if not occupation.prendas or len(occupation.prendas) == 0:
            errors.append("At least one prenda is required")
        
        # Validate each prenda
        for i, prenda in enumerate(occupation.prendas):
            prenda_errors = self.validate_prenda(prenda)
            if prenda_errors:
                errors.extend([f"Prenda {i+1} ({prenda.prenda_type}): {err}" for err in prenda_errors])
        
        return errors

    def validate_prenda(self, prenda: OccupationPrenda) -> List[str]:
        """
        Validate a prenda configuration.
        Returns a list of validation errors (empty if valid).
        """
        errors = []
        
        if not prenda.prenda_type or not prenda.prenda_type.strip():
            errors.append("Prenda type is required")
        
        # Validate prices are non-negative
        price_fields = [
            'price_sml_other', 'price_xl_other', 'price_xxl_other',
            'price_sml_tarapoto', 'price_xl_tarapoto', 'price_xxl_tarapoto',
            'price_sml_san_isidro', 'price_xl_san_isidro', 'price_xxl_san_isidro'
        ]
        
        for field in price_fields:
            price = getattr(prenda, field, 0.0)
            if price < 0:
                errors.append(f"{field} cannot be negative")
        
        return errors

    def export_to_dict(self) -> Dict:
        """Export the entire configuration to a dictionary for easy serialization."""
        return {
            "occupations": [
                {
                    "name": occ.name,
                    "display_name": occ.display_name,
                    "synonyms": occ.synonyms,
                    "prendas": [
                        {
                            "prenda_type": p.prenda_type,
                            "display_name": p.display_name,
                            "has_sizes": p.has_sizes,
                            "garment_type": p.garment_type,
                            "is_required": p.is_required,
                            "default_quantity": p.default_quantity,
                            "is_primary": p.is_primary,
                            "price_sml_other": p.price_sml_other,
                            "price_xl_other": p.price_xl_other,
                            "price_xxl_other": p.price_xxl_other,
                            "price_sml_tarapoto": p.price_sml_tarapoto,
                            "price_xl_tarapoto": p.price_xl_tarapoto,
                            "price_xxl_tarapoto": p.price_xxl_tarapoto,
                            "price_sml_san_isidro": p.price_sml_san_isidro,
                            "price_xl_san_isidro": p.price_xl_san_isidro,
                            "price_xxl_san_isidro": p.price_xxl_san_isidro,
                        }
                        for p in occ.prendas
                    ],
                    "is_active": occ.is_active,
                    "description": occ.description
                }
                for occ in self.unified_config.occupations
            ],
            "default_occupation": self.unified_config.default_occupation,
            "default_local_group": self.unified_config.default_local_group
        }

