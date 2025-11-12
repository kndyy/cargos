"""
Configuration persistence manager for saving and loading user settings.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

from cargos.core.models import AppConfig
from cargos.core.constants import DEFAULT_OUTPUT_DIR, DEFAULT_TEMPLATES_DIR, DEFAULT_PREVIEW_ROWS


class ConfigManager:
    """Manages persistent configuration settings stored in config.json."""

    def __init__(self, config_file: str | Path | None = None):
        self.config_file = Path(config_file) if config_file else Path("config.json")
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ensure_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data.setdefault("app_settings", {})
        data.setdefault("occupations", [])
        data.setdefault("default_occupation", "MOZO")
        data.setdefault("default_local_group", "OTHER")
        return data

    def _load_file_data(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            return self._ensure_structure({})

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                content = json.load(f)
            return self._ensure_structure(content)
        except Exception as error:  # pragma: no cover - defensive
            self.logger.error(f"Failed to read config file '{self.config_file}': {error}")
            return self._ensure_structure({})

    def _write_file_data(self, data: Dict[str, Any]) -> bool:
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as error:  # pragma: no cover - defensive
            self.logger.error(f"Failed to write config file '{self.config_file}': {error}")
            return False

    # ------------------------------------------------------------------
    # Application (UI) configuration
    # ------------------------------------------------------------------
    def load_config(self) -> AppConfig:
        data = self._load_file_data()
        settings = data.get("app_settings", {})

        destination_path = str(
            Path(settings.get("destination_path", f"{DEFAULT_OUTPUT_DIR}/"))
        )
        cargo_template = str(
            Path(
                settings.get(
                    "cargo_template_path",
                    f"{DEFAULT_TEMPLATES_DIR}/CARGO UNIFORMES.docx",
                )
            )
        )
        autorizacion_template = str(
            Path(
                settings.get(
                    "autorizacion_template_path",
                    f"{DEFAULT_TEMPLATES_DIR}/50% - AUTORIZACIÓN DESCUENTO DE UNIFORMES (02).docx",
                )
            )
        )
        preview_limit = settings.get("preview_rows_limit", DEFAULT_PREVIEW_ROWS)

        return AppConfig(
            destination_path=destination_path,
            cargo_template_path=cargo_template,
            autorizacion_template_path=autorizacion_template,
            preview_rows_limit=preview_limit,
        )

    def save_config(self, config: AppConfig, unified_config: Any = None) -> bool:
        data = self._load_file_data()

        data["app_settings"] = {
            "destination_path": str(Path(config.destination_path)),
            "cargo_template_path": str(Path(config.cargo_template_path)),
            "autorizacion_template_path": str(Path(config.autorizacion_template_path)),
            "preview_rows_limit": config.preview_rows_limit,
        }

        if unified_config is not None:
            data["occupations"] = [
                {
                    "name": occ.name,
                    "display_name": occ.display_name,
                    "synonyms": occ.synonyms,
                    "prendas": [
                        {
                            "prenda_type": pr.prenda_type,
                            "display_name": pr.display_name,
                            "has_sizes": pr.has_sizes,
                            "garment_type": pr.garment_type,
                            "is_required": pr.is_required,
                            "default_quantity": pr.default_quantity,
                            "is_primary": pr.is_primary,
                            "price_sml_other": pr.price_sml_other,
                            "price_xl_other": pr.price_xl_other,
                            "price_xxl_other": pr.price_xxl_other,
                            "price_sml_tarapoto": pr.price_sml_tarapoto,
                            "price_xl_tarapoto": pr.price_xl_tarapoto,
                            "price_xxl_tarapoto": pr.price_xxl_tarapoto,
                            "price_sml_san_isidro": pr.price_sml_san_isidro,
                            "price_xl_san_isidro": pr.price_xl_san_isidro,
                            "price_xxl_san_isidro": pr.price_xxl_san_isidro,
                        }
                        for pr in occ.prendas
                    ],
                    "is_active": occ.is_active,
                    "description": occ.description,
                }
                for occ in unified_config.occupations
            ]
            data["default_occupation"] = unified_config.default_occupation
            data["default_local_group"] = unified_config.default_local_group

        return self._write_file_data(data)

    # ------------------------------------------------------------------
    # Unified configuration helpers
    # ------------------------------------------------------------------
    def load_unified_config_data(self) -> Dict[str, Any]:
        data = self._load_file_data()
        return {
            "occupations": data.get("occupations", []),
            "default_occupation": data.get("default_occupation", "MOZO"),
            "default_local_group": data.get("default_local_group", "OTHER"),
        }
