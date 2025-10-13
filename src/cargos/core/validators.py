"""
Validation utilities for the File Generator application.
"""
from pathlib import Path
from typing import List
from cargos.core.models import AppConfig


class TemplateValidator:
    """Utility class for template file validation."""
    
    @staticmethod
    def validate_template_files(config: AppConfig) -> List[str]:
        """
        Validate that template files exist.
        
        Args:
            config: Application configuration
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check CARGO template
        if not Path(config.cargo_template_path).exists():
            errors.append(f"CARGO template not found: {config.cargo_template_path}")
        
        # Check AUTORIZACION template
        if not Path(config.autorizacion_template_path).exists():
            errors.append(f"AUTORIZACION template not found: {config.autorizacion_template_path}")
        
        return errors

    @staticmethod
    def validate_autorizacion_template(config: AppConfig) -> List[str]:
        """Validate only the AUTORIZACION template path."""
        errors = []
        if not Path(config.autorizacion_template_path).exists():
            errors.append(f"AUTORIZACION template not found: {config.autorizacion_template_path}")
        return errors
