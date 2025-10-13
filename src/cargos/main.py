"""
File Generator Application - Main Entry Point

A GUI application for generating PDF files from Excel data using Word templates.
Follows clean architecture principles with separation of concerns.
"""
import tkinter as tk
from tkinter import ttk
import logging
from pathlib import Path
from typing import Optional

from cargos.core.models import ExcelData
from cargos.services import ExcelService, FileGenerationService, UnifiedConfigService
from cargos.ui import CargosTab, ConfigurationTab


class FileGeneratorApp:
    """
    Main application class that orchestrates the UI and services.

    This class acts as the controller, coordinating between the UI components
    and the business logic services.
    """

    def __init__(self, root: tk.Tk):
        """
        Initialize the application.

        Args:
            root: The main tkinter window
        """
        self.root = root
        self.root.title("Uniformes")

        from cargos.core.constants import DEFAULT_WINDOW_SIZE
        self.root.geometry(DEFAULT_WINDOW_SIZE)

        # Setup logging first (without config dependency)
        self.logger = self._setup_logging()

        # Initialize configuration service (single source of truth)
        self.unified_config_service = UnifiedConfigService(self.logger)
        self.config = self.unified_config_service.get_app_config()

        # Initialize services with logger
        self.excel_service = ExcelService(self.logger)
        self.file_generation_service = FileGenerationService(self.logger, self.unified_config_service)

        # Data storage
        self.excel_data: Optional[ExcelData] = None

        # Create UI
        self._create_ui()

        # Create default directories
        self._create_default_directories()

        self.logger.info("Application initialized successfully")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        from cargos.core.constants import DEFAULT_LOG_FILE
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(DEFAULT_LOG_FILE),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

    def _create_ui(self):
        """Create the main UI with tabs."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create Cargos tab
        self.cargos_tab = CargosTab(self.notebook, self.config, self.unified_config_service)
        self.notebook.add(self.cargos_tab.frame, text="Cargos")

        # Create Configuration tab
        self.config_tab = ConfigurationTab(self.notebook, self.config, self.unified_config_service)
        self.notebook.add(self.config_tab.frame, text="Configuration")

        # Create Stock tab (placeholder)
        self.stock_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stock_frame, text="Stock")
        self._setup_stock_tab()

        # Setup callbacks
        self._setup_callbacks()

        # Save initial configuration
        self.unified_config_service.save()

    def _setup_stock_tab(self):
        """Setup the Stock tab interface (placeholder)."""
        placeholder_label = ttk.Label(
            self.stock_frame,
            text="Stock functionality will be implemented later"
        )
        placeholder_label.pack(expand=True)

    def _setup_callbacks(self):
        """Setup callbacks between UI and business logic."""
        self.cargos_tab.on_load_excel = self._handle_load_excel
        self.cargos_tab.on_generate_files = self._handle_generate_files
        self.cargos_tab.on_config_changed = self._handle_config_changed

    def _create_default_directories(self):
        """Create default directories if they don't exist."""
        try:
            Path(self.config.destination_path).mkdir(exist_ok=True)
            from cargos.core.constants import DEFAULT_TEMPLATES_DIR
            Path(DEFAULT_TEMPLATES_DIR).mkdir(exist_ok=True)
            self.cargos_tab.log_message("Default directories created/verified")
        except Exception as e:
            error_msg = f"Error creating directories: {str(e)}"
            self.cargos_tab.log_message(error_msg, "ERROR")
            self.logger.error(error_msg)

    def _handle_load_excel(self):
        """Handle Excel file loading."""
        try:
            if not self.config.excel_file_path:
                self.cargos_tab.show_error("Error", "Please select an Excel file first")
                return

            self.cargos_tab.log_message("Loading Excel file...")

            # Load Excel data using service
            self.excel_data = self.excel_service.load_excel_file(self.config.excel_file_path)

            # Validate Excel data
            validation_result = self.excel_service.validate_excel_data(self.excel_data)

            if validation_result.is_valid:
                self.cargos_tab.update_data_preview(self.excel_data)
                self.cargos_tab.log_message(validation_result.message)
            else:
                self.cargos_tab.log_message(validation_result.message, "ERROR")
        except Exception as e:
            error_msg = f"Failed to load Excel file: {str(e)}"
            self.cargos_tab.log_message(error_msg, "ERROR")
            self.cargos_tab.show_error("Error", error_msg)
            self.logger.exception("Excel loading error")

    def _handle_generate_files(self):
        """Handle file generation process."""
        try:
            if not self.excel_data or not self.excel_data.is_loaded:
                self.cargos_tab.show_error("Error", "Please load Excel data first")
                return

            from cargos.core.validators import TemplateValidator
            config_errors = TemplateValidator.validate_template_files(self.config)
            if config_errors:
                self.cargos_tab.show_error("Configuration Error", "\n".join(config_errors))
                return

            from cargos.core.models import GenerationOptions
            selected_locales = self.cargos_tab.get_selected_locales() if hasattr(self.cargos_tab, 'get_selected_locales') else []
            combine_per_local = self.cargos_tab.get_combine_per_local() if hasattr(self.cargos_tab, 'get_combine_per_local') else False
            template_states = self.cargos_tab.get_enabled_template_states() if hasattr(self.cargos_tab, 'get_enabled_template_states') else {"cargo_enabled": True, "autorizacion_enabled": True}

            options = GenerationOptions(
                selected_locales=selected_locales,
                combine_per_local=combine_per_local,
                cargo_enabled=template_states.get("cargo_enabled", True),
                autorizacion_enabled=template_states.get("autorizacion_enabled", True)
            )

            result = self.file_generation_service.generate_files(self.excel_data, self.config, options)

            if result.success:
                self.cargos_tab.log_message(result.message)
                if result.files_generated > 0:
                    self.cargos_tab.show_info(
                        "Success",
                        f"Generated {result.files_generated} files successfully!"
                    )
            else:
                self.cargos_tab.log_message(result.message, "ERROR")
                err_text = result.message + ("\n\n" + "\n".join(result.errors) if result.errors else "")
                self.cargos_tab.show_error("Generation Error", err_text)

        except Exception as e:
            error_msg = f"Unexpected error during file generation: {str(e)}"
            self.cargos_tab.log_message(error_msg, "ERROR")
            self.cargos_tab.show_error("Error", error_msg)
            self.logger.exception("Unexpected error in file generation")

    def _handle_config_changed(self):
        """Handle configuration changes and save to file."""
        try:
            # Pass the current config to ensure destination path is saved
            success = self.unified_config_service.save(config=self.config)
            if success:
                self.logger.info("Configuration saved successfully")
            else:
                self.logger.warning("Failed to save configuration")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")

def main():
    root = tk.Tk()
    FileGeneratorApp(root)  # Keep reference to prevent garbage collection
    root.mainloop()

if __name__ == "__main__":
    main()
