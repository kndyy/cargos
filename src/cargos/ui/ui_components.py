"""
UI components for the File Generator application.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from typing import Callable, Optional, List
from datetime import datetime
import pandas as pd

from cargos.core.models import ExcelData, AppConfig, Occupation, OccupationPrenda
from cargos.core.constants import (
    GENERATION_DIALOG_WIDTH, GENERATION_DIALOG_HEIGHT, GENERATION_DIALOG_CANVAS_HEIGHT,
    TREE_COLUMN_WIDTH_PEOPLE, TREE_COLUMN_WIDTH_STATUS, TREE_COLUMN_WIDTH_UNIFORM, TREE_COLUMN_WIDTH_DATA
)
from cargos.services.unified_config_service import UnifiedConfigService


class CompactFileSelectionFrame:
    """Compact frame for file and path selection."""
    
    def __init__(self, parent, config: AppConfig):
        self.config = config
        self.frame = ttk.LabelFrame(parent, text="Files", padding=8)
        
        # Variables for file paths
        self.excel_file_var = tk.StringVar()
        self.cargo_template_var = tk.StringVar(value=config.cargo_template_path)
        self.autorizacion_template_var = tk.StringVar(value=config.autorizacion_template_path)
        self.destination_path_var = tk.StringVar(value=config.destination_path)
        
        # Template enable/disable toggles (both enabled by default)
        self.cargo_enabled_var = tk.BooleanVar(value=True)
        self.autorizacion_enabled_var = tk.BooleanVar(value=True)
        
        # Callbacks
        self.on_excel_file_changed: Optional[Callable] = None
        self.on_cargo_template_changed: Optional[Callable] = None
        self.on_autorizacion_template_changed: Optional[Callable] = None
        self.on_destination_path_changed: Optional[Callable] = None
        self.on_load_excel: Optional[Callable] = None
        self.on_reload_excel: Optional[Callable] = None
        self.on_template_toggles_changed: Optional[Callable] = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create and layout widgets."""
        from pathlib import Path
        
        # Formato Uniforme file selection (compact)
        ttk.Label(self.frame, text="Formato Uniforme:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.excel_path_label = ttk.Label(self.frame, text="(no file)", width=30, anchor="w", foreground="gray")
        self.excel_path_label.grid(row=0, column=1, sticky="w", padx=(0, 5))
        ttk.Button(self.frame, text="Browse", command=self._browse_excel_file).grid(row=0, column=2)
        self.load_button = ttk.Button(self.frame, text="Load", command=self._load_excel, state="disabled")
        self.load_button.grid(row=0, column=3, padx=(5, 0))
        self.reload_button = ttk.Button(self.frame, text="Reload", command=self._reload_excel, state="disabled")
        self.reload_button.grid(row=0, column=4, padx=(2, 0))
        
        # CARGO file (with toggle)
        self.cargo_checkbox = ttk.Checkbutton(self.frame, text="CARGO:", variable=self.cargo_enabled_var, 
                                            command=self._on_cargo_toggle)
        self.cargo_checkbox.grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(3, 0))
        self.cargo_path_label = ttk.Label(self.frame, text=Path(self.cargo_template_var.get()).name if self.cargo_template_var.get() else "(no file)", 
                                         width=30, anchor="w", foreground="gray", font=("TkDefaultFont", 8))
        self.cargo_path_label.grid(row=1, column=1, sticky="w", padx=(0, 5), pady=(3, 0))
        self.cargo_browse_btn = ttk.Button(self.frame, text="Browse", command=self._browse_cargo_template)
        self.cargo_browse_btn.grid(row=1, column=2, pady=(3, 0))
        
        # AUTORIZACION file (with toggle)
        self.autorizacion_checkbox = ttk.Checkbutton(self.frame, text="AUTORIZACION:", variable=self.autorizacion_enabled_var, 
                                                   command=self._on_autorizacion_toggle)
        self.autorizacion_checkbox.grid(row=2, column=0, sticky="w", padx=(0, 5), pady=(3, 0))
        self.autorizacion_path_label = ttk.Label(self.frame, text=Path(self.autorizacion_template_var.get()).name if self.autorizacion_template_var.get() else "(no file)", 
                                               width=30, anchor="w", foreground="gray", font=("TkDefaultFont", 8))
        self.autorizacion_path_label.grid(row=2, column=1, sticky="w", padx=(0, 5), pady=(3, 0))
        self.autorizacion_browse_btn = ttk.Button(self.frame, text="Browse", command=self._browse_autorizacion_template)
        self.autorizacion_browse_btn.grid(row=2, column=2, pady=(3, 0))
        
        # Destination folder (compact)
        ttk.Label(self.frame, text="Destination:", font=("TkDefaultFont", 8)).grid(row=3, column=0, sticky="w", padx=(0, 5), pady=(3, 0))
        self.destination_path_label = ttk.Label(self.frame, text=Path(self.destination_path_var.get()).name if self.destination_path_var.get() else "(no folder)", 
                                              width=30, anchor="w", foreground="gray", font=("TkDefaultFont", 8))
        self.destination_path_label.grid(row=3, column=1, sticky="w", padx=(0, 5), pady=(3, 0))
        ttk.Button(self.frame, text="Browse", command=self._browse_destination_folder).grid(row=3, column=2, pady=(3, 0))
        
        # Configure grid weights
        self.frame.columnconfigure(1, weight=1)
    
    def _browse_excel_file(self):
        """Browse and select Excel file."""
        file_path = filedialog.askopenfilename(
            title="Select Formato Uniforme File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if file_path:
            from pathlib import Path
            self.excel_file_var.set(file_path)
            self.excel_path_label.configure(text=Path(file_path).name, foreground="black")
            self.config.excel_file_path = file_path
            
            # Enable load and reload buttons
            self.load_button.configure(state="normal")
            self.reload_button.configure(state="normal")
            
            if self.on_excel_file_changed:
                self.on_excel_file_changed(file_path)
    
    def _load_excel(self):
        """Handle load Excel button click."""
        if self.on_load_excel:
            self.on_load_excel()
    
    def _reload_excel(self):
        """Handle reload Excel button click."""
        if self.on_reload_excel:
            self.on_reload_excel()
    
    def _on_cargo_toggle(self):
        """Handle CARGO template toggle."""
        enabled = self.cargo_enabled_var.get()
        self.cargo_browse_btn.configure(state="normal" if enabled else "disabled")
        self.cargo_path_label.configure(foreground="black" if enabled else "gray")
        if self.on_template_toggles_changed:
            self.on_template_toggles_changed()
    
    def _on_autorizacion_toggle(self):
        """Handle AUTORIZACION template toggle."""
        enabled = self.autorizacion_enabled_var.get()
        self.autorizacion_browse_btn.configure(state="normal" if enabled else "disabled")
        self.autorizacion_path_label.configure(foreground="black" if enabled else "gray")
        if self.on_template_toggles_changed:
            self.on_template_toggles_changed()
    
    def _browse_cargo_template(self):
        """Browse and select CARGO template file."""
        file_path = filedialog.askopenfilename(
            title="Select CARGO Template",
            filetypes=[("Word documents", "*.docx"), ("All files", "*.*")]
        )
        if file_path:
            from pathlib import Path
            self.cargo_template_var.set(file_path)
            self.cargo_path_label.configure(text=Path(file_path).name, foreground="black")
            self.config.cargo_template_path = file_path
            if self.on_cargo_template_changed:
                self.on_cargo_template_changed(file_path)
    
    def _browse_autorizacion_template(self):
        """Browse and select AUTORIZACION template file."""
        file_path = filedialog.askopenfilename(
            title="Select AUTORIZACION Template",
            filetypes=[("Word documents", "*.docx"), ("All files", "*.*")]
        )
        if file_path:
            from pathlib import Path
            self.autorizacion_template_var.set(file_path)
            self.autorizacion_path_label.configure(text=Path(file_path).name, foreground="black")
            self.config.autorizacion_template_path = file_path
            if self.on_autorizacion_template_changed:
                self.on_autorizacion_template_changed(file_path)
    
    def _browse_destination_folder(self):
        """Browse and select destination folder."""
        folder_path = filedialog.askdirectory(title="Select Destination Folder")
        if folder_path:
            from pathlib import Path
            # Use pathlib for cross-platform path handling
            folder_path = str(Path(folder_path))
            self.destination_path_var.set(folder_path)
            self.destination_path_label.configure(text=Path(folder_path).name, foreground="black")
            self.config.destination_path = folder_path
            if self.on_destination_path_changed:
                self.on_destination_path_changed(folder_path)
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
    
    def is_cargo_enabled(self) -> bool:
        """Check if CARGO template is enabled."""
        return self.cargo_enabled_var.get()
    
    def is_autorizacion_enabled(self) -> bool:
        """Check if AUTORIZACION template is enabled."""
        return self.autorizacion_enabled_var.get()
    
    def get_enabled_templates(self) -> List[str]:
        """Get list of enabled template names."""
        enabled = []
        if self.is_cargo_enabled():
            enabled.append("CARGO")
        if self.is_autorizacion_enabled():
            enabled.append("AUTORIZACION")
        return enabled


class GenerateButtonFrame:
    """Frame for generate files button at bottom."""
    
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        
        # Callbacks
        self.on_generate_files: Optional[Callable] = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create and layout widgets."""
        # Create a prominent generate button
        self.generate_btn = ttk.Button(
            self.frame, 
            text="Generate Documents", 
            command=self._generate_files,
            state="disabled"
        )
        # Make button bigger, taller, and centered
        self.generate_btn.configure(width=25)
        self.generate_btn.pack(expand=True, padx=10, pady=10, ipady=8)
    
    def _generate_files(self):
        """Handle generate files button click."""
        if self.on_generate_files:
            self.on_generate_files()
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the generate button."""
        self.generate_btn.configure(state="normal" if enabled else "disabled")
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)


class WorksheetSummaryFrame:
    """Frame for showing worksheet parsing summary."""
    
    def __init__(self, parent):
        self.frame = ttk.LabelFrame(parent, text="Worksheet Summary", padding=10)
        self._create_widgets()
    
    def _create_widgets(self):
        """Create and layout widgets."""
        from cargos.core.constants import DEFAULT_TREE_HEIGHT
        
        # Create treeview for worksheet summary
        columns = ("Sheet", "People", "Errors", "Status")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=DEFAULT_TREE_HEIGHT)
        
        # Configure columns
        self.tree.heading("Sheet", text="Sheet Name")
        self.tree.heading("People", text="People Parsed")
        self.tree.heading("Errors", text="Errors")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("Sheet", width=180, minwidth=120)
        self.tree.column("People", width=TREE_COLUMN_WIDTH_PEOPLE, minwidth=100)
        self.tree.column("Errors", width=80, minwidth=60)
        self.tree.column("Status", width=TREE_COLUMN_WIDTH_STATUS, minwidth=80)
        
        self.tree.pack(fill="both", expand=True)
        
        # Add double-click binding to view worksheet details
        self.tree.bind("<Double-1>", self._on_worksheet_double_click)
        
        # Callback for worksheet selection
        self.on_worksheet_selected: Optional[Callable] = None
    
    def _on_worksheet_double_click(self, event):
        """Handle double-click on worksheet."""
        selection = self.tree.selection()
        if selection and self.on_worksheet_selected:
            item = self.tree.item(selection[0])
            sheet_name = item['values'][0]
            self.on_worksheet_selected(sheet_name)
    
    def update_data(self, excel_data: ExcelData):
        """Update treeview with worksheet summary."""
        # Clear existing data
        self._clear_treeview(self.tree)
        
        if not excel_data.is_loaded:
            return
        
        # Add worksheet summary rows
        for worksheet in excel_data.worksheets:
            if worksheet.data is None:
                status = "✗ Failed"
            else:
                # Check for critical errors that prevent generation
                has_critical_errors = self._has_critical_errors(worksheet)
                if has_critical_errors:
                    status = "⚠ Skipped"
                else:
                    # Check for occupation mapping issues
                    has_occupation_issues = self._has_occupation_mapping_issues(worksheet)
                    if has_occupation_issues:
                        status = "⚠ Mapping Issues"
                    else:
                        status = "✓ Success"
            
            error_count = len(worksheet.errors)
            
            self.tree.insert("", "end", values=(
                worksheet.metadata.sheet_name,
                worksheet.people_parsed,
                error_count,
                status
            ))
    
    def _clear_treeview(self, tree):
        """Clear all items from a treeview."""
        for item in tree.get_children():
            tree.delete(item)
    
    def _has_critical_errors(self, worksheet):
        """Check if worksheet has critical errors that prevent generation."""
        # Check for missing tienda (critical for folder structure)
        if not worksheet.metadata.tienda or str(worksheet.metadata.tienda).strip() == "":
            return True
        
        # Check for DNI errors (critical for document generation)
        dni_errors = [error for error in worksheet.errors if "missing DNI" in error]
        if dni_errors:
            return True
        
        return False
    
    def _has_occupation_mapping_issues(self, worksheet):
        """Check if worksheet has occupation mapping issues."""
        if worksheet.data is None or 'cargo' not in worksheet.data.columns:
            return False
        
        # Check if any cargo values don't map directly to configured occupations
        for cargo in worksheet.data['cargo'].dropna().unique():
            if cargo and str(cargo).strip():
                # This is a simplified check - in practice, you'd need access to the unified service
                # For now, we'll check if the cargo contains common mapping indicators
                cargo_str = str(cargo).upper()
                if any(indicator in cargo_str for indicator in ['(A)', '(B)', '(C)', 'P/T', 'PT']):
                    return True
        
        return False
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)


class DataPreviewFrame:
    """Frame for data preview with treeview."""
    
    def __init__(self, parent, unified_service: UnifiedConfigService):
        self.frame = ttk.LabelFrame(parent, text="Data Preview", padding=10)
        self.current_excel_data: Optional[ExcelData] = None
        self.unified_service = unified_service
        self._create_widgets()
    
    def _create_widgets(self):
        """Create and layout widgets."""
        # Create notebook for different views
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Summary tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")
        
        # Worksheet summary
        self.worksheet_summary = WorksheetSummaryFrame(self.summary_frame)
        self.worksheet_summary.pack(fill="both", expand=True)
        self.worksheet_summary.on_worksheet_selected = self._show_worksheet_details
        
        # Details tab (will be populated dynamically)
        self.details_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.details_frame, text="Details")
        
        # Uniform Data tab
        self.uniform_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.uniform_frame, text="Uniforms")
        
        # Logs tab
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Logs")
        
        # Create details content
        self._create_details_widgets()
        
        # Create uniform data content
        self._create_uniform_widgets()
        
        # Create logs content
        self._create_logs_widgets()
    
    def _create_details_widgets(self):
        """Create widgets for details tab."""
        # Worksheet selector
        selector_frame = ttk.Frame(self.details_frame)
        selector_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(selector_frame, text="Select Worksheet:").pack(side="left", padx=(0, 5))
        self.worksheet_var = tk.StringVar()
        self.worksheet_combo = ttk.Combobox(selector_frame, textvariable=self.worksheet_var, state="readonly")
        self.worksheet_combo.pack(side="left", padx=(0, 10))
        self.worksheet_combo.bind("<<ComboboxSelected>>", self._on_worksheet_selected)
        
        ttk.Button(selector_frame, text="Refresh", command=self._refresh_worksheet_details).pack(side="left")
        
        # Data treeview (expanded to take full space)
        data_frame = ttk.LabelFrame(self.details_frame, text="Data", padding=5)
        data_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Metadata footnote (one line at bottom of data frame)
        self.metadata_label = ttk.Label(data_frame, text="", font=("TkDefaultFont", 8), foreground="gray")
        self.metadata_label.pack(side="bottom", fill="x", pady=(2, 0))
        
        self.data_tree = ttk.Treeview(data_frame)
        self.data_tree.pack(fill="both", expand=True, pady=(0, 2))
        
        # Scrollbars for data treeview
        data_scroll_y = ttk.Scrollbar(data_frame, orient="vertical", command=self.data_tree.yview)
        data_scroll_y.pack(side="right", fill="y")
        self.data_tree.configure(yscrollcommand=data_scroll_y.set)
        
        data_scroll_x = ttk.Scrollbar(data_frame, orient="horizontal", command=self.data_tree.xview)
        data_scroll_x.pack(side="bottom", fill="x")
        self.data_tree.configure(xscrollcommand=data_scroll_x.set)
        # Link double-click in Details to open Uniforms for that person
        self.data_tree.bind("<Double-1>", self._on_data_row_double_click)
    
    def _create_logs_widgets(self):
        """Create widgets for logs tab."""
        # Control buttons
        control_frame = ttk.Frame(self.logs_frame)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(control_frame, text="Clear Logs", command=self.clear_logs).pack(side="right", padx=2)
        ttk.Label(control_frame, text="Application Logs:", font=("TkDefaultFont", 9)).pack(side="left")
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            self.logs_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 9),
            state="disabled"
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=(0, 5))
    
    def _create_uniform_widgets(self):
        """Create widgets for uniform data tab."""
        # Worksheet selector for uniform data
        selector_frame = ttk.Frame(self.uniform_frame)
        selector_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(selector_frame, text="Select Worksheet:").pack(side="left", padx=(0, 5))
        self.uniform_worksheet_var = tk.StringVar()
        self.uniform_worksheet_combo = ttk.Combobox(selector_frame, textvariable=self.uniform_worksheet_var, state="readonly")
        self.uniform_worksheet_combo.pack(side="left", padx=(0, 10))
        self.uniform_worksheet_combo.bind("<<ComboboxSelected>>", self._on_uniform_worksheet_selected)
        
        ttk.Button(selector_frame, text="Refresh", command=self._refresh_uniform_details).pack(side="left")
        
        # Uniform data treeview
        uniform_data_frame = ttk.LabelFrame(self.uniform_frame, text="Uniforms by Person", padding=5)
        uniform_data_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Metadata footnote for uniform data
        self.uniform_metadata_label = ttk.Label(uniform_data_frame, text="", font=("TkDefaultFont", 8), foreground="gray")
        self.uniform_metadata_label.pack(side="bottom", fill="x", pady=(2, 0))
        
        self.uniform_data_tree = ttk.Treeview(uniform_data_frame)
        self.uniform_data_tree.pack(fill="both", expand=True, pady=(0, 2))
        
        # Scrollbars for uniform data treeview
        uniform_scroll_y = ttk.Scrollbar(uniform_data_frame, orient="vertical", command=self.uniform_data_tree.yview)
        uniform_scroll_y.pack(side="right", fill="y")
        self.uniform_data_tree.configure(yscrollcommand=uniform_scroll_y.set)
        
        uniform_scroll_x = ttk.Scrollbar(uniform_data_frame, orient="horizontal", command=self.uniform_data_tree.xview)
        uniform_scroll_x.pack(side="bottom", fill="x")
        self.uniform_data_tree.configure(xscrollcommand=uniform_scroll_x.set)
    
    def _show_worksheet_details(self, sheet_name: str):
        """Show details for a specific worksheet."""
        self.worksheet_var.set(sheet_name)
        self._refresh_worksheet_details()
        self.notebook.select(1)  # Switch to details tab
    
    def _on_worksheet_selected(self, event):
        """Handle worksheet selection from combobox."""
        self._refresh_worksheet_details()
    
    def _refresh_worksheet_details(self):
        """Refresh the worksheet details view."""
        if not self.current_excel_data or not self.worksheet_var.get():
            return
        
        sheet_name = self.worksheet_var.get()
        worksheet = self.current_excel_data.get_worksheet_by_name(sheet_name)
        
        if not worksheet:
            return
        
        # Update metadata footnote (one line)
        metadata_info = f"Sheet: {worksheet.metadata.sheet_name} | "
        metadata_info += f"Fecha: {worksheet.metadata.fecha_solicitud} | "
        metadata_info += f"Tienda: {worksheet.metadata.tienda} | "
        metadata_info += f"Admin: {worksheet.metadata.administrador}"
        
        if worksheet.errors:
            metadata_info += f" | Errors: {len(worksheet.errors)}"
        if worksheet.warnings:
            metadata_info += f" | Warnings: {len(worksheet.warnings)}"
        
        self.metadata_label.configure(text=metadata_info)
        
        # Update data treeview
        self._update_data_tree(worksheet)
    
    def _on_uniform_worksheet_selected(self, event):
        """Handle uniform worksheet selection from combobox."""
        self._refresh_uniform_details()
    
    def _refresh_uniform_details(self):
        """Refresh the uniform worksheet details view."""
        if not self.current_excel_data or not self.uniform_worksheet_var.get():
            return
        
        sheet_name = self.uniform_worksheet_var.get()
        worksheet = self.current_excel_data.get_worksheet_by_name(sheet_name)
        
        if not worksheet:
            return
        
        # Update uniform metadata footnote (one line)
        metadata_info = f"Sheet: {worksheet.metadata.sheet_name} | "
        metadata_info += f"Fecha: {worksheet.metadata.fecha_solicitud} | "
        metadata_info += f"Tienda: {worksheet.metadata.tienda} | "
        metadata_info += f"Admin: {worksheet.metadata.administrador}"
        
        if worksheet.uniform_data is not None:
            metadata_info += f" | Uniform Rows: {len(worksheet.uniform_data)}"
        else:
            metadata_info += " | No uniform data"
        
        self.uniform_metadata_label.configure(text=metadata_info)
        
        # Update uniform data treeview
        self._update_uniform_data_tree(worksheet)
    
    def _update_uniform_data_tree(self, worksheet):
        """Update uniform data treeview with per-person view: Name, Cargo, Talla*, and role-specific uniform columns."""
        # Clear existing data
        self._clear_treeview(self.uniform_data_tree)
        
        if worksheet.data is None or worksheet.data.empty:
            return
        
        # Setup columns and treeview
        columns = self._setup_uniform_columns(worksheet)
        self._configure_uniform_treeview(columns)
        
        # Insert data rows
        self._populate_uniform_data(worksheet, columns)
    
    def _setup_uniform_columns(self, worksheet):
        """Setup column structure for uniform data treeview."""
        main_df = worksheet.data
        uniform_df = worksheet.uniform_data if worksheet.uniform_data is not None else None
        
        # Define column groups
        talla_cols = [col for col in main_df.columns if "talla" in str(col).lower()]
        packer_cols = ["packerpolo", "packergorra"]
        mozo_cols = ["camisa", "blusa", "mandilon", "andarin"]
        
        # Other uniform columns
        other_uniform_cols = []
        if uniform_df is not None and not uniform_df.empty:
            for col in uniform_df.columns:
                if col not in packer_cols and col not in mozo_cols:
                    other_uniform_cols.append(col)
        
        # Combine all columns in stable order
        uniform_cols_order = packer_cols + mozo_cols + other_uniform_cols
        return ["Name", "Cargo"] + [str(c) for c in talla_cols] + [str(c) for c in uniform_cols_order]
    
    def _configure_uniform_treeview(self, columns):
        """Configure the uniform data treeview with columns."""
        self.uniform_data_tree["columns"] = columns
        self.uniform_data_tree["show"] = "headings"
        
        for col in columns:
            self.uniform_data_tree.heading(col, text=str(col))
            width = 120 if col in ("Name", "Cargo") else TREE_COLUMN_WIDTH_UNIFORM
            self.uniform_data_tree.column(col, width=width, minwidth=70)
    
    def _populate_uniform_data(self, worksheet, columns):
        """Populate the uniform data treeview with actual data."""
        main_df = worksheet.data
        uniform_df = worksheet.uniform_data if worksheet.uniform_data is not None else None
        
        # Define column groups for role-based display
        packer_cols = ["packerpolo", "packergorra"]
        mozo_cols = ["camisa", "blusa", "mandilon", "andarin"]
        talla_cols = [col for col in main_df.columns if "talla" in str(col).lower()]
        
        # Insert rows (limit to 100 for performance)
        max_rows = min(len(main_df), 100)
        for idx in range(max_rows):
            main_row = main_df.iloc[idx]
            name, cargo = self._extract_name_and_cargo(main_row)
            cargo_upper = str(cargo).upper().strip()
            
            # Build row values
            row_values = [str(name), str(cargo)]
            
            # Add talla values
            for tcol in talla_cols:
                val = main_row.get(tcol, "")
                row_values.append(str(val) if pd.notna(val) else "")
            
            # Add uniform values based on role
            uniform_row = None
            if uniform_df is not None and idx < len(uniform_df):
                uniform_row = uniform_df.iloc[idx]
            
            uniform_cols_order = packer_cols + mozo_cols + [col for col in uniform_df.columns if col not in packer_cols and col not in mozo_cols] if uniform_df is not None else []
            
            for ucol in uniform_cols_order:
                display = self._get_uniform_display_value(uniform_row, ucol, cargo_upper, packer_cols, mozo_cols)
                row_values.append(display)
            
            self.uniform_data_tree.insert("", "end", iid=str(idx), values=row_values)
    
    def _extract_name_and_cargo(self, series):
        """Extract name and cargo from a pandas Series."""
        name_val = ""
        cargo_val = ""
        lowered = {str(k).lower(): k for k in series.index}
        
        # Extract cargo
        for key in lowered:
            if "cargo" in key:
                cargo_val = series[lowered[key]]
                break
        
        # Extract name: try combined first, then components
        combined = None
        for key in lowered:
            if "nombre" in key and "apellido" in key:
                combined = series[lowered[key]]
                break
        
        if pd.notna(combined) and str(combined).strip():
            name_val = combined
        else:
            first = None
            last = None
            for key in lowered:
                if first is None and ("nombre" in key or "name" in key):
                    first = series[lowered[key]]
                if last is None and ("apellido" in key or "last" in key):
                    last = series[lowered[key]]
            
            if pd.notna(first) and pd.notna(last):
                name_val = f"{str(first).strip()} {str(last).strip()}".strip()
            elif pd.notna(first):
                name_val = str(first).strip()
            else:
                # Fallback: first non-null string field
                for key in series.index:
                    val = series[key]
                    if pd.notna(val) and isinstance(val, str) and len(val.strip()) > 2:
                        name_val = val
                        break
        
        return str(name_val) if pd.notna(name_val) else "", str(cargo_val) if pd.notna(cargo_val) else ""
    
    def _get_uniform_display_value(self, uniform_row, ucol, cargo_upper, packer_cols, mozo_cols):
        """Get display value for a uniform column based on role."""
        if uniform_row is None or ucol not in uniform_row.index:
            return ""
        
        # Determine if this column should be displayed for this cargo
        should_display = False
        if cargo_upper == "PACKER" and ucol in packer_cols:
            should_display = True
        elif ("MOZO" in cargo_upper or "AZAFATA" in cargo_upper) and ucol in mozo_cols:
            should_display = True
        elif cargo_upper not in ("PACKER",) and ucol not in packer_cols and ucol not in mozo_cols:
            should_display = True
        
        if not should_display:
            return ""
        
        return self._format_uniform_count(uniform_row[ucol])
    
    def _safe_int_conversion(self, value, default=None):
        """Safely convert a value to integer with fallback."""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default
        
        try:
            return int(value)
        except Exception:
            try:
                return int(str(value).strip())
            except Exception:
                return default
    
    def _clear_treeview(self, tree):
        """Clear all items from a treeview."""
        for item in tree.get_children():
            tree.delete(item)
    
    def _format_uniform_count(self, value):
        """Format uniform count value for display."""
        n = self._safe_int_conversion(value)
        if n is None or n <= 0:
            return ""
        elif n == 1:
            return "✓"
        else:
            return "✓" * min(n, 3)
    
    def _update_data_tree(self, worksheet):
        """Update data treeview with worksheet data."""
        # Clear existing data
        self._clear_treeview(self.data_tree)
        
        if worksheet.data is None or worksheet.data.empty:
            return
        
        # Setup and configure treeview
        columns = list(worksheet.data.columns)
        # Add occupation column at the beginning
        columns_with_occupation = ["Occupation"] + columns
        self._configure_data_treeview(columns_with_occupation)
        
        # Identify date columns for special formatting
        fecha_cols = self._identify_fecha_columns(columns)
        
        # Populate with data
        self._populate_data_tree(worksheet.data, columns, columns_with_occupation, fecha_cols)
    
    def _configure_data_treeview(self, columns):
        """Configure the data treeview with columns and headers."""
        self.data_tree["columns"] = columns
        self.data_tree["show"] = "headings"
        
        for col in columns:
            self.data_tree.heading(col, text=str(col))
            self.data_tree.column(col, width=TREE_COLUMN_WIDTH_DATA, minwidth=50)
    
    def _identify_fecha_columns(self, columns):
        """Identify columns that contain date information for special formatting."""
        fecha_cols = set()
        for col in columns:
            col_l = str(col).lower()
            if ("fecha" in col_l and "ingreso" in col_l) or col_l.strip() in ("fecha de ingreso", "fecha ingreso"):
                fecha_cols.add(col)
        return fecha_cols
    
    def _populate_data_tree(self, data, original_columns, columns_with_occupation, fecha_cols):
        """Populate the data treeview with actual data."""
        for index, row in data.head(100).iterrows():  # Limit to 100 rows for performance
            row_values = []
            
            # Add occupation column first
            cargo = ""
            # Try to find cargo/occupation column with different possible names
            cargo_keys = ["cargo", "CARGO", "Cargo", "occupation", "OCCUPATION", "Occupation"]
            for key in cargo_keys:
                if key in row.index:
                    cargo = self._to_scalar(row[key])
                    break
            
            if cargo and str(cargo).strip():
                # Get normalized occupation name
                normalized_occupation = self.unified_service.normalize_occupation(str(cargo))
                row_values.append(normalized_occupation)
            else:
                row_values.append("")
            
            # Add other columns
            for col in original_columns:
                val = self._to_scalar(row[col])
                if col in fecha_cols:
                    row_values.append(self._format_date_only(val))
                else:
                    row_values.append(self._format_cell_value(val))
            self.data_tree.insert("", "end", iid=str(index), values=row_values)
    
    def _to_scalar(self, value):
        """Convert pandas Series to scalar value (handles duplicate column names)."""
        if isinstance(value, pd.Series):
            # Choose first non-null value
            for v in value.values:
                try:
                    if not pd.isna(v):
                        return v
                except Exception:
                    return v
            return None
        return value
    
    def _format_date_only(self, value):
        """Format date value to show only date part (no time)."""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return ""
        
        try:
            ts = pd.to_datetime(value, errors="coerce")
            if pd.isna(ts):
                return str(value)
            return ts.date().isoformat()
        except Exception:
            return str(value)
    
    def _format_cell_value(self, val):
        """Format a cell value for display in the treeview."""
        try:
            return "" if pd.isna(val) else str(val)
        except Exception:
            return str(val) if val is not None else ""

    def _on_data_row_double_click(self, event):
        """On double-click in Details, show the same person in Uniforms tab."""
        selection = self.data_tree.selection()
        if not selection:
            return
        iid = selection[0]
        # Ensure uniform worksheet matches
        if self.worksheet_var.get() != self.uniform_worksheet_var.get():
            self.uniform_worksheet_var.set(self.worksheet_var.get())
            self._refresh_uniform_details()
        # Select same row in uniform tree and switch tab
        try:
            self.uniform_data_tree.selection_set(iid)
            self.uniform_data_tree.see(iid)
        except Exception:
            pass
        self.notebook.select(2)
    
    def update_data(self, excel_data: ExcelData):
        """Update preview with Excel data."""
        self.current_excel_data = excel_data
        
        # Update summary
        self.worksheet_summary.update_data(excel_data)
        
        # Update worksheet selector
        if excel_data.worksheets:
            sheet_names = [w.metadata.sheet_name for w in excel_data.worksheets]
            self.worksheet_combo['values'] = sheet_names
            self.uniform_worksheet_combo['values'] = sheet_names
            if sheet_names:
                self.worksheet_var.set(sheet_names[0])
                self.uniform_worksheet_var.set(sheet_names[0])
                self._refresh_worksheet_details()
                self._refresh_uniform_details()
        else:
            self.worksheet_combo['values'] = []
            self.uniform_worksheet_combo['values'] = []
            self.worksheet_var.set("")
            self.uniform_worksheet_var.set("")
    
    def add_log_message(self, message: str, level: str = "INFO"):
        """Add message to log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}\n"
        
        # Temporarily enable to insert text
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        
        # Auto-switch to logs tab if there's an error
        if level == "ERROR":
            self.notebook.select(3)  # Logs tab (now 4th tab: Summary, Details, Uniforms, Logs)
    
    def clear_logs(self):
        """Clear log display."""
        # Temporarily enable to clear text
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
        self.add_log_message("Logs cleared")
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)




class CargosTab:
    """Main tab for Cargos functionality with optimized layout."""
    
    def __init__(self, parent, config: AppConfig, unified_service: UnifiedConfigService):
        self.frame = ttk.Frame(parent)
        self.config = config
        self.unified_service = unified_service
        
        # Create main container
        self.main_frame = ttk.Frame(self.frame)
        self.main_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Create UI components
        self.file_selection = CompactFileSelectionFrame(self.main_frame, config)
        self.data_preview = DataPreviewFrame(self.main_frame, unified_service)
        self.generate_button = GenerateButtonFrame(self.main_frame)
        
        # Layout components
        self._layout_components()
        
        # Callbacks
        self.on_load_excel: Optional[Callable] = None
        self.on_generate_files: Optional[Callable] = None
        self.on_config_changed: Optional[Callable] = None
        
        # Setup callbacks
        self._setup_callbacks()
    
    def _layout_components(self):
        """Layout all components with optimized space usage."""
        # File selection at top (compact)
        self.file_selection.pack(fill="x", pady=(0, 8))
        
        # Data preview takes most space
        self.data_preview.pack(fill="both", expand=True, pady=(0, 8))
        
        # Generate button at bottom
        self.generate_button.pack(fill="x", pady=(0, 8))
    
    def _setup_callbacks(self):
        """Setup component callbacks."""
        self.file_selection.on_excel_file_changed = self._on_excel_file_changed
        self.file_selection.on_cargo_template_changed = self._on_cargo_template_changed
        self.file_selection.on_autorizacion_template_changed = self._on_autorizacion_template_changed
        self.file_selection.on_destination_path_changed = self._on_destination_path_changed
        self.file_selection.on_load_excel = self._on_load_excel
        self.file_selection.on_reload_excel = self._on_reload_excel
        self.file_selection.on_template_toggles_changed = self._on_template_toggles_changed
        
        self.generate_button.on_generate_files = self._on_generate_files
    
    def _on_excel_file_changed(self, file_path: str):
        """Handle Excel file path change."""
        self.log_message(f"Excel file selected: {file_path}")
    
    def _on_cargo_template_changed(self, path: str):
        """Handle CARGO template path change."""
        self.log_message(f"CARGO template selected: {path}")
        # Trigger configuration save
        if hasattr(self, 'on_config_changed') and self.on_config_changed:
            self.on_config_changed()
    
    def _on_autorizacion_template_changed(self, path: str):
        """Handle AUTORIZACION template path change."""
        self.log_message(f"AUTORIZACION template selected: {path}")
        # Trigger configuration save
        if hasattr(self, 'on_config_changed') and self.on_config_changed:
            self.on_config_changed()
    
    def _on_destination_path_changed(self, path: str):
        """Handle destination path change."""
        self.log_message(f"Destination folder selected: {path}")
        self.config.destination_path = path
        if self.on_config_changed:
            self.on_config_changed()
    
    def _on_template_toggles_changed(self):
        """Handle template toggle changes."""
        enabled_templates = self.file_selection.get_enabled_templates()
        self.log_message(f"Template selection changed: {', '.join(enabled_templates) if enabled_templates else 'None selected'}")
        self._update_generate_enablement()
    
    def _on_load_excel(self):
        """Handle load Excel button click."""
        if self.on_load_excel:
            self.on_load_excel()
    
    def _on_reload_excel(self):
        """Handle reload Excel button click."""
        if self.on_load_excel:  # Use same callback as load
            self.on_load_excel()
    
    def _on_generate_files(self):
        """Handle generate files button click."""
        # Open generation options dialog and, on confirm, call callback
        try:
            locales = []
            if self.data_preview.current_excel_data and self.data_preview.current_excel_data.worksheets:
                for w in self.data_preview.current_excel_data.worksheets:
                    if w.metadata.tienda:
                        locales.append(str(w.metadata.tienda))
            locales = sorted(set(locales))
            selected_locales, combine = self._open_generation_options_dialog(locales)
            if selected_locales is None:
                return  # canceled
            # Stash selections for retrieval by controller
            self._selected_locales = selected_locales
            self._combine_per_local = combine
            
            if self.on_generate_files:
                self.on_generate_files()
        except Exception as e:
            self.show_error("Error", f"Failed to open generation options: {e}")

    
    def update_data_preview(self, excel_data: ExcelData):
        """Update data preview."""
        self.data_preview.update_data(excel_data)
        self._update_generate_enablement()
    
    def log_message(self, message: str, level: str = "INFO"):
        """Add message to log."""
        self.data_preview.add_log_message(message, level)
    
    def show_error(self, title: str, message: str):
        """Show error message box."""
        messagebox.showerror(title, message)
    
    def show_info(self, title: str, message: str):
        """Show info message box."""
        messagebox.showinfo(title, message)

    def _update_generate_enablement(self):
        """Enable generate if we have data, valid autorizacion template, destination, and at least one locale selected."""
        try:
            has_data = hasattr(self, 'data_preview') and self.data_preview.current_excel_data and self.data_preview.current_excel_data.successful_worksheets > 0
            # We defer locale selection to the dialog; just require that there exist locales
            has_locales_available = False
            if has_data:
                for w in self.data_preview.current_excel_data.worksheets:
                    if w.metadata.tienda:
                        has_locales_available = True
                        break
            # Check template validation for enabled templates only
            from cargos.core.validators import TemplateValidator
            enabled_templates = self.file_selection.get_enabled_templates()
            templates_ok = len(enabled_templates) > 0  # At least one template must be enabled
            
            if templates_ok and "AUTORIZACION" in enabled_templates:
                autorizacion_errors = TemplateValidator.validate_autorizacion_template(self.config)
                if autorizacion_errors:
                    templates_ok = False
            
            if templates_ok and "CARGO" in enabled_templates:
                # CARGO template validation is handled by TemplateValidator
                # For now, just check if cargo template path exists
                from pathlib import Path
                if not Path(self.config.cargo_template_path).exists():
                    templates_ok = False
            
            dest_ok = bool(self.config.destination_path)
            self.generate_button.set_enabled(has_data and has_locales_available and templates_ok and dest_ok)
        except Exception:
            self.generate_button.set_enabled(False)

    def get_selected_locales(self) -> List[str]:
        return getattr(self, '_selected_locales', [])

    def get_combine_per_local(self) -> bool:
        return bool(getattr(self, '_combine_per_local', False))
    
    def get_enabled_template_states(self) -> dict:
        """Get the current state of template toggles."""
        return {
            "cargo_enabled": self.file_selection.is_cargo_enabled(),
            "autorizacion_enabled": self.file_selection.is_autorizacion_enabled()
        }


    def _open_generation_options_dialog(self, locales: List[str]):
        """Open a modal dialog to select locales and combine option.
        Returns (selected_locales, combine_per_local) or (None, None) if cancelled."""
        # Get the root window properly
        root = self.frame.winfo_toplevel()
        dlg = tk.Toplevel(root)
        dlg.title("Generation Options")
        dlg.transient(root)
        dlg.grab_set()
        dlg.resizable(False, False)
        
        # Center the dialog (cross-platform)
        dlg.geometry(f"{GENERATION_DIALOG_WIDTH}x{GENERATION_DIALOG_HEIGHT}")
        dlg.update_idletasks()
        width, height = GENERATION_DIALOG_WIDTH, GENERATION_DIALOG_HEIGHT
        screen_width = dlg.winfo_screenwidth()
        screen_height = dlg.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        dlg.geometry(f"{width}x{height}+{x}+{y}")
        
        # Ensure proper cleanup on window close
        result = {"ok": False}
        def _on_close():
            result["ok"] = False
            try:
                dlg.destroy()
            except tk.TclError:
                pass  # Dialog already destroyed
        
        dlg.protocol("WM_DELETE_WINDOW", _on_close)
        container = ttk.Frame(dlg, padding=10)
        container.pack(fill="both", expand=True)
        
        # Create two-column layout
        left_frame = ttk.Frame(container)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        right_frame = ttk.Frame(container)
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)
        
        # Left side: Locale selection with checkboxes
        ttk.Label(left_frame, text="Select Locales:", font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Checkbox frame with scrollbar
        checkbox_frame_container = ttk.Frame(left_frame)
        checkbox_frame_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create canvas with scrollbar
        canvas = tk.Canvas(checkbox_frame_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(checkbox_frame_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Create canvas window for scrollable frame
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        def _update_scroll_region(event=None):
            """Update the scroll region of the canvas based on scrollable frame size."""
            canvas.update_idletasks()
            # Update the canvas scroll region to match the scrollable frame size
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update scrollable frame width to match canvas
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:  # Only update if canvas has been rendered
                canvas.itemconfig(canvas_window, width=canvas_width)
        
        def _on_canvas_configure(event):
            """Update scrollable frame width when canvas is resized."""
            # Set scrollable frame width to match canvas width (minus scrollbar if visible)
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
            # Update scroll region
            canvas.after_idle(_update_scroll_region)
        
        def _on_frame_configure(event):
            """Update canvas scroll region when scrollable frame is configured."""
            # Update the canvas scroll region
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def _on_mousewheel(event):
            """Handle mouse wheel scrolling (Windows/Mac)."""
            # Windows and Mac use delta
            if hasattr(event, 'delta') and event.delta:
                # Windows: delta is in multiples of 120
                # Mac: delta can be fractional
                delta = -1 * (event.delta / 120) if abs(event.delta) >= 120 else -1 * event.delta
                canvas.yview_scroll(int(delta), "units")
        
        def _on_linux_mousewheel(event):
            """Handle mouse wheel when over frame (Linux)."""
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
        
        # Bind scrollable frame configuration to update scroll region
        scrollable_frame.bind("<Configure>", _on_frame_configure)
        
        # Bind canvas resize to update scrollable frame width
        canvas.bind("<Configure>", _on_canvas_configure)
        
        # Function to bind mouse wheel to a widget and propagate to children
        def _bind_mousewheel(widget):
            """Bind mouse wheel events to widget and all its children recursively."""
            # Windows/Mac
            widget.bind("<MouseWheel>", _on_mousewheel)
            # Linux
            widget.bind("<Button-4>", _on_linux_mousewheel)
            widget.bind("<Button-5>", _on_linux_mousewheel)
            # Recursively bind to children
            for child in widget.winfo_children():
                try:
                    _bind_mousewheel(child)
                except tk.TclError:
                    pass  # Some widgets don't support binding
        
        # Configure scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas and scrollable frame
        _bind_mousewheel(canvas)
        _bind_mousewheel(scrollable_frame)
        
        # Create checkboxes for each locale
        locale_vars = {}
        for locale in locales:
            var = tk.BooleanVar(value=True)  # Default all selected
            locale_vars[locale] = var
            cb = ttk.Checkbutton(scrollable_frame, text=locale, variable=var, command=lambda: _update_preview())
            cb.pack(anchor="w", pady=1, padx=2)
            # Bind mouse wheel to each checkbox
            _bind_mousewheel(cb)
        
        # Update scroll region after all checkboxes are created and dialog is shown
        def _initial_update():
            canvas.update_idletasks()
            _update_scroll_region()
            # Ensure canvas has proper size
            canvas.update_idletasks()
        
        # Schedule update after dialog is fully rendered
        dlg.update_idletasks()
        dlg.after(50, _initial_update)
        
        # Control buttons
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill="x", pady=(0, 10))
        
        def _select_all():
            for var in locale_vars.values():
                var.set(True)
            _update_preview()
        
        def _deselect_all():
            for var in locale_vars.values():
                var.set(False)
            _update_preview()
        
        ttk.Button(btn_frame, text="Select All", command=_select_all).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="Deselect All", command=_deselect_all).pack(side="left")
        
        # Combine option
        combine_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(left_frame, text="Also generate combined DOCX per local", variable=combine_var, command=lambda: _update_preview()).pack(anchor="w", pady=(5, 0))
        
        # Right side: Preview
        ttk.Label(right_frame, text="Documents to Generate:", font=("TkDefaultFont", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        preview_text = tk.Text(right_frame, wrap=tk.WORD, height=20, width=40, font=("Consolas", 9))
        preview_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=preview_text.yview)
        preview_text.configure(yscrollcommand=preview_scroll.set)
        
        preview_text.pack(side="left", fill="both", expand=True)
        preview_scroll.pack(side="right", fill="y")
        
        def _update_preview():
            preview_text.delete(1.0, tk.END)
            selected_locales = [loc for loc, var in locale_vars.items() if var.get()]
            
            if not selected_locales:
                preview_text.insert(tk.END, "No locales selected.\nPlease select at least one locale.")
                return
            
            # Get enabled templates from the file selection
            enabled_templates = self.file_selection.get_enabled_templates()
            if not enabled_templates:
                preview_text.insert(tk.END, "No templates enabled.\nPlease enable at least one template (CARGO or AUTORIZACION).")
                return
            
            total_docs = 0
            for locale in selected_locales:
                # Count people in this locale (approximation)
                people_count = 0
                if hasattr(self, 'data_preview') and self.data_preview.current_excel_data:
                    for ws in self.data_preview.current_excel_data.worksheets:
                        if str(ws.metadata.tienda) == locale and ws.data is not None:
                            people_count += len(ws.data)
                
                preview_text.insert(tk.END, f"📁 {locale}/\n")
                if people_count > 0:
                    # Show documents for each enabled template
                    for template in enabled_templates:
                        for i in range(min(people_count, 3)):  # Show first 3
                            preview_text.insert(tk.END, f"   📄 {template}_person_{i+1}.docx\n")
                        if people_count > 3:
                            preview_text.insert(tk.END, f"   ... and {people_count - 3} more {template} documents\n")
                        total_docs += people_count
                    
                    # Show combined documents if enabled
                    if combine_var.get():
                        for template in enabled_templates:
                            preview_text.insert(tk.END, f"   📄 {template}_COMBINED_{locale}.docx\n")
                            total_docs += 1
                else:
                    preview_text.insert(tk.END, "   (No people found)\n")
                preview_text.insert(tk.END, "\n")
            
            preview_text.insert(tk.END, f"Total documents: {total_docs}")
            preview_text.insert(tk.END, f"\nEnabled templates: {', '.join(enabled_templates)}")
        
        # Initial preview update
        _update_preview()
        
        # Action buttons
        actions = ttk.Frame(container)
        actions.grid(row=1, column=0, columnspan=2, sticky="e", pady=(10, 0))
        
        def _ok():
            selected_locales = [loc for loc, var in locale_vars.items() if var.get()]
            if selected_locales:
                result["ok"] = True
                result["selected"] = selected_locales
                result["combine"] = combine_var.get()
                try:
                    dlg.destroy()
                except tk.TclError:
                    pass
            else:
                messagebox.showerror("Validation", "Please select at least one locale")
        
        def _cancel():
            result["ok"] = False
            try:
                dlg.destroy()
            except tk.TclError:
                pass
        
        ttk.Button(actions, text="Cancel", command=_cancel).pack(side="right")
        ttk.Button(actions, text="Generate", command=_ok).pack(side="right", padx=(6, 8))
        
        try:
            dlg.wait_window(dlg)
        except tk.TclError:
            return None, None
        
        if not result["ok"]:
            return None, None
        
        return result.get("selected", []), result.get("combine", False)


class ConfigurationTab:
    """Unified configuration tab for managing occupations and their integrated pricing."""
    
    def __init__(self, parent, config: AppConfig, unified_service: UnifiedConfigService, price_service=None):
        self.parent = parent
        self.config = config
        self.unified_service = unified_service
        self.price_service = price_service  # Optional price service for loading from Excel
        
        # Create main frame
        self.frame = ttk.Frame(parent)
        self._create_widgets()
        self._load_data()
    
    def _create_widgets(self):
        """Create the unified configuration widgets."""
        # Main container with scrollbar
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create notebook for different configuration sections
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # Occupations tab
        self._create_occupations_tab()
        
        # Pricing Matrix tab
        self._create_pricing_matrix_tab()
        
        # Buttons frame
        button_frame = ttk.Frame(main_container)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ttk.Button(button_frame, text="Save Configuration", command=self._save_config).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_to_defaults).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Add Occupation", command=self._add_occupation).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Add Prenda", command=self._add_prenda).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="📁 Reload Prices from Excel", command=self._reload_prices_from_excel).pack(side="left")
    
    def _create_occupations_tab(self):
        """Create the occupations management tab."""
        occupations_frame = ttk.Frame(self.notebook)
        self.notebook.add(occupations_frame, text="Occupations")
        
        # Treeview for occupations
        columns = ("Name", "Display Name", "Synonyms", "Prendas", "Active", "Description")
        self.occupations_tree = ttk.Treeview(occupations_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.occupations_tree.heading("Name", text="Name")
        self.occupations_tree.heading("Display Name", text="Display Name")
        self.occupations_tree.heading("Synonyms", text="Synonyms")
        self.occupations_tree.heading("Prendas", text="Prendas")
        self.occupations_tree.heading("Active", text="Active")
        self.occupations_tree.heading("Description", text="Description")
        
        self.occupations_tree.column("Name", width=100, minwidth=80)
        self.occupations_tree.column("Display Name", width=120, minwidth=100)
        self.occupations_tree.column("Synonyms", width=200, minwidth=150)
        self.occupations_tree.column("Prendas", width=150, minwidth=100)
        self.occupations_tree.column("Active", width=60, minwidth=50)
        self.occupations_tree.column("Description", width=200, minwidth=150)
        
        # Scrollbar for occupations tree
        occupations_scrollbar = ttk.Scrollbar(occupations_frame, orient="vertical", command=self.occupations_tree.yview)
        self.occupations_tree.configure(yscrollcommand=occupations_scrollbar.set)
        
        # Pack widgets
        self.occupations_tree.pack(side="left", fill="both", expand=True)
        occupations_scrollbar.pack(side="right", fill="y")
        
        # Bind double-click to edit
        self.occupations_tree.bind("<Double-1>", self._edit_occupation)
    
    def _create_pricing_matrix_tab(self):
        """Create the pricing matrix tab."""
        pricing_frame = ttk.Frame(self.notebook)
        self.notebook.add(pricing_frame, text="Pricing Matrix")
        
        # Treeview for pricing data
        columns = ("Occupation", "Prenda Type", "Size Group", "Local Group", "Price")
        self.pricing_tree = ttk.Treeview(pricing_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        for col in columns:
            self.pricing_tree.heading(col, text=col)
            self.pricing_tree.column(col, width=120, minwidth=80)
        
        # Scrollbar for pricing tree
        pricing_scrollbar = ttk.Scrollbar(pricing_frame, orient="vertical", command=self.pricing_tree.yview)
        self.pricing_tree.configure(yscrollcommand=pricing_scrollbar.set)
        
        # Pack widgets
        self.pricing_tree.pack(side="left", fill="both", expand=True)
        pricing_scrollbar.pack(side="right", fill="y")
        
        # Bind double-click to edit
        self.pricing_tree.bind("<Double-1>", self._edit_price_entry)
    
    def _load_data(self):
        """Load configuration data into the trees."""
        # Load occupations
        self.occupations_tree.delete(*self.occupations_tree.get_children())
        for occupation in self.unified_service.unified_config.occupations:
            prendas_str = ", ".join([p.prenda_type for p in occupation.prendas])
            synonyms_str = ", ".join(occupation.synonyms)
            active_str = "✓" if occupation.is_active else "✗"
            
            self.occupations_tree.insert("", "end", values=(
                occupation.name,
                occupation.display_name,
                synonyms_str,
                prendas_str,
                active_str,
                occupation.description
            ))
        
        # Load pricing matrix
        self.pricing_tree.delete(*self.pricing_tree.get_children())
        try:
            configuration_matrix = self.unified_service.get_configuration_matrix()
            
            for config in configuration_matrix:
                if config["price"] > 0:  # Only show entries with prices
                    self.pricing_tree.insert("", "end", values=(
                        config["occupation_display"],
                        config["prenda_type"],
                        config["size_group"],
                        config["local_group"],
                        f"S/ {config['price']:.2f}"
                    ))
        except Exception as e:
            # Log error but don't crash the UI
            import logging
            logging.error(f"Error loading configuration matrix: {e}")
            self.pricing_tree.insert("", "end", values=("Error", "Loading", "Failed", "", ""))
    
    def _save_config(self):
        """Save unified configuration."""
        if self.unified_service.save():
            messagebox.showinfo("Success", "Configuration saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save configuration!")
    
    def _reset_to_defaults(self):
        """Reset to default configuration."""
        messagebox.showwarning(
            "Not Available", 
            "Reset to defaults is not available. All configuration is loaded from config.json.\n\n"
            "To reset, please edit config.json directly or delete it to start fresh."
        )
    
    def _reload_prices_from_excel(self):
        """Reload prices from Excel file (precios.xlsx)."""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select Price Excel File",
            filetypes=[("Excel files", "*.xlsm *.xlsx"), ("All files", "*.*")],
            initialdir="sources",
            initialfile="precios.xlsx"
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Use the unified service's price loader
            if self.unified_service.reload_prices_from_excel(file_path):
                summary = self.unified_service.get_price_summary()
                
                messagebox.showinfo(
                    "Prices Reloaded", 
                    f"Loaded {summary['total_entries']} price entries\n"
                    f"Occupations: {len(summary['occupations'])}\n"
                    f"Prendas: {len(summary['prendas'])}\n"
                    f"Locations: {', '.join(summary['locations'])}"
                )
            else:
                messagebox.showerror("Error", f"Failed to load prices from {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error loading prices: {str(e)}")
    
    def _add_occupation(self):
        """Add a new occupation."""
        self._edit_occupation(None)
    
    def _edit_occupation(self, event):
        """Edit an occupation."""
        # Get selected item or create new
        selected = self.occupations_tree.selection()
        if selected:
            item = self.occupations_tree.item(selected[0])
            values = item['values']
            occupation_name = values[0]
            occupation = self.unified_service.get_occupation(occupation_name)
        else:
            occupation = None
        
        # Create edit dialog
        self._show_occupation_edit_dialog(occupation)
    
    def _add_prenda(self):
        """Add a new prenda to an occupation."""
        # Show occupation selection dialog first
        self._show_prenda_edit_dialog(None, None)
    
    def _edit_price_entry(self, event):
        """Edit a price entry."""
        # Get selected item
        selected = self.pricing_tree.selection()
        if not selected:
            return
        
        item = self.pricing_tree.item(selected[0])
        values = item['values']
        occupation_name = values[0]
        prenda_type = values[1]
        size_group = values[2]
        local_group = values[3]
        price = float(values[4].replace("S/ ", ""))
        
        # Create edit dialog
        self._show_price_edit_dialog(occupation_name, prenda_type, size_group, local_group, price)
    
    def _create_centered_dialog(self, title, width, height):
        """Create a centered dialog window."""
        dlg = tk.Toplevel(self.frame)
        dlg.title(title)
        dlg.transient(self.frame)
        dlg.grab_set()
        dlg.resizable(False, False)
        
        # Center dialog
        dlg.geometry(f"{width}x{height}")
        dlg.update_idletasks()
        x = (dlg.winfo_screenwidth() // 2) - (width // 2)
        y = (dlg.winfo_screenheight() // 2) - (height // 2)
        dlg.geometry(f"{width}x{height}+{x}+{y}")
        return dlg
    
    def _show_occupation_edit_dialog(self, occupation):
        """Show occupation edit dialog."""
        dlg = self._create_centered_dialog(
            "Edit Occupation" if occupation else "Add Occupation", 600, 500
        )
        
        # Form fields
        ttk.Label(dlg, text="Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        name_var = tk.StringVar(value=occupation.name if occupation else "")
        ttk.Entry(dlg, textvariable=name_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dlg, text="Display Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        display_var = tk.StringVar(value=occupation.display_name if occupation else "")
        ttk.Entry(dlg, textvariable=display_var, width=40).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dlg, text="Synonyms (one per line):").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        synonyms_text = scrolledtext.ScrolledText(dlg, width=40, height=8)
        synonyms_text.grid(row=2, column=1, padx=5, pady=5)
        if occupation:
            synonyms_text.insert("1.0", "\n".join(occupation.synonyms))
        
        ttk.Label(dlg, text="Description:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        desc_text = scrolledtext.ScrolledText(dlg, width=40, height=4)
        desc_text.grid(row=3, column=1, padx=5, pady=5)
        if occupation:
            desc_text.insert("1.0", occupation.description)
        
        active_var = tk.BooleanVar(value=occupation.is_active if occupation else True)
        ttk.Checkbutton(dlg, text="Active", variable=active_var).grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dlg)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def save_occupation():
            synonyms_text_content = synonyms_text.get("1.0", tk.END).strip()
            synonyms_list = [s.strip() for s in synonyms_text_content.split("\n") if s.strip()]
            description = desc_text.get("1.0", tk.END).strip()
            
            new_occupation = Occupation(
                name=name_var.get(),
                display_name=display_var.get(),
                synonyms=synonyms_list,
                prendas=occupation.prendas if occupation else [],
                is_active=active_var.get(),
                description=description
            )
            
            try:
                if occupation:
                    if self.unified_service.update_occupation(new_occupation):
                        # Persist to config.json
                        if not self.unified_service.save():
                            messagebox.showwarning("Warning", "Occupation updated but failed to save to file!")
                        self._load_data()
                        dlg.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to update occupation!")
                else:
                    if self.unified_service.add_occupation(new_occupation):
                        # Persist to config.json
                        if not self.unified_service.save():
                            messagebox.showwarning("Warning", "Occupation added but failed to save to file!")
                        self._load_data()
                        dlg.destroy()
                    else:
                        messagebox.showerror("Error", "Failed to add occupation!")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        ttk.Button(button_frame, text="Save", command=save_occupation).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dlg.destroy).pack(side="left", padx=5)
    
    def _show_prenda_edit_dialog(self, occupation_name, prenda):
        """Show prenda edit dialog."""
        dlg = self._create_centered_dialog(
            "Edit Prenda" if prenda else "Add Prenda", 500, 600
        )
        
        # Form fields
        ttk.Label(dlg, text="Occupation:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        occ_var = tk.StringVar(value=occupation_name or "")
        occ_combo = ttk.Combobox(dlg, textvariable=occ_var, values=[occ.name for occ in self.unified_service.unified_config.occupations], width=37)
        occ_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dlg, text="Prenda Type:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        prenda_var = tk.StringVar(value=prenda.prenda_type if prenda else "")
        ttk.Entry(dlg, textvariable=prenda_var, width=40).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dlg, text="Display Name:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        display_name_var = tk.StringVar(value=prenda.display_name if prenda else "")
        ttk.Entry(dlg, textvariable=display_name_var, width=40).grid(row=2, column=1, padx=5, pady=5)
        
        has_sizes_var = tk.BooleanVar(value=prenda.has_sizes if prenda else True)
        ttk.Checkbutton(dlg, text="Has Sizes", variable=has_sizes_var).grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        is_required_var = tk.BooleanVar(value=prenda.is_required if prenda else False)
        ttk.Checkbutton(dlg, text="Required", variable=is_required_var).grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(dlg, text="Default Quantity:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        qty_var = tk.StringVar(value=str(prenda.default_quantity) if prenda else "0")
        ttk.Entry(dlg, textvariable=qty_var, width=40).grid(row=5, column=1, padx=5, pady=5)
        
        # Pricing section
        ttk.Label(dlg, text="Pricing (S/):", font=("TkDefaultFont", 10, "bold")).grid(row=6, column=0, columnspan=2, pady=(20, 5))
        
        # Create pricing grid
        pricing_frame = ttk.Frame(dlg)
        pricing_frame.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Headers
        ttk.Label(pricing_frame, text="Size\\Local").grid(row=0, column=0, padx=2, pady=2)
        ttk.Label(pricing_frame, text="OTHER").grid(row=0, column=1, padx=2, pady=2)
        ttk.Label(pricing_frame, text="TARAPOTO").grid(row=0, column=2, padx=2, pady=2)
        ttk.Label(pricing_frame, text="SAN_ISIDRO").grid(row=0, column=3, padx=2, pady=2)
        
        # Price entry variables
        price_vars = {}
        for i, size in enumerate(["SML", "XL", "XXL"], 1):
            ttk.Label(pricing_frame, text=size).grid(row=i, column=0, padx=2, pady=2)
            for j, local in enumerate(["other", "tarapoto", "san_isidro"], 1):
                price_attr = f"price_{size.lower()}_{local}"
                price_value = getattr(prenda, price_attr, 0.0) if prenda else 0.0
                price_vars[price_attr] = tk.StringVar(value=str(price_value))
                ttk.Entry(pricing_frame, textvariable=price_vars[price_attr], width=8).grid(row=i, column=j, padx=2, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(dlg)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        def save_prenda():
            try:
                default_qty = int(qty_var.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity!")
                return
            
            # Create prenda with pricing
            prenda_data = {
                "prenda_type": prenda_var.get(),
                "display_name": display_name_var.get(),
                "has_sizes": has_sizes_var.get(),
                "is_required": is_required_var.get(),
                "default_quantity": default_qty
            }
            
            # Add pricing data
            for price_attr, var in price_vars.items():
                try:
                    price_value = float(var.get())
                    prenda_data[price_attr] = price_value
                except ValueError:
                    messagebox.showerror("Error", f"Please enter a valid price for {price_attr}!")
                    return
            
            new_prenda = OccupationPrenda(**prenda_data)
            
            try:
                if self.unified_service.add_prenda_to_occupation(occ_var.get(), new_prenda):
                    self._load_data()
                    dlg.destroy()
                else:
                    messagebox.showerror("Error", "Failed to add prenda!")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        ttk.Button(button_frame, text="Save", command=save_prenda).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dlg.destroy).pack(side="left", padx=5)
    
    def _show_price_edit_dialog(self, occupation_name, prenda_type, size_group, local_group, price):
        """Show price edit dialog."""
        dlg = self._create_centered_dialog("Edit Price", 400, 300)
        
        # Form fields
        ttk.Label(dlg, text="Occupation:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        occ_var = tk.StringVar(value=occupation_name)
        ttk.Entry(dlg, textvariable=occ_var, state="readonly", width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dlg, text="Prenda Type:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        prenda_var = tk.StringVar(value=prenda_type)
        ttk.Entry(dlg, textvariable=prenda_var, state="readonly", width=30).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(dlg, text="Size Group:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        size_var = tk.StringVar(value=size_group)
        ttk.Entry(dlg, textvariable=size_var, state="readonly", width=30).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(dlg, text="Local Group:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        local_var = tk.StringVar(value=local_group)
        ttk.Entry(dlg, textvariable=local_var, state="readonly", width=30).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(dlg, text="Price:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        price_var = tk.StringVar(value=str(price))
        ttk.Entry(dlg, textvariable=price_var, width=30).grid(row=4, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dlg)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def save_price():
            try:
                price_value = float(price_var.get())
                if self.unified_service.update_prenda_pricing(
                    occ_var.get(), prenda_var.get(), size_var.get(), 
                    local_var.get(), price_value
                ):
                    self._load_data()
                    dlg.destroy()
                else:
                    messagebox.showerror("Error", "Failed to update price!")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid price!")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        ttk.Button(button_frame, text="Save", command=save_price).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dlg.destroy).pack(side="left", padx=5)


def show_gender_selection_dialog(root: tk.Tk, person_name: str, cargo: str, 
                                  male_option: str, female_option: str,
                                  male_prices: dict = None, female_prices: dict = None) -> str:
    """Show a dialog for user to select gender for ambiguous occupation.
    
    Args:
        root: The Tk root window
        person_name: Name of the person
        cargo: Original cargo from Excel
        male_option: Male occupation variant name
        female_option: Female occupation variant name
        male_prices: Dict of prenda->price for male option (optional)
        female_prices: Dict of prenda->price for female option (optional)
    
    Returns:
        'HOMBRE' or 'MUJER'
    """
    result = ['HOMBRE']  # Default if dialog is closed
    
    dlg = tk.Toplevel(root)
    dlg.title("Seleccionar Género de Uniforme")
    dlg.transient(root)
    dlg.grab_set()
    
    # Calculate size and position
    # Increase height if prices are shown
    height = 500 if (male_prices or female_prices) else 250
    width = 650
    
    # Center on parent
    try:
        x = root.winfo_x() + (root.winfo_width() - width) // 2
        y = root.winfo_y() + (root.winfo_height() - height) // 2
    except:
        x = (dlg.winfo_screenwidth() - width) // 2
        y = (dlg.winfo_screenheight() - height) // 2
        
    dlg.geometry(f"{width}x{height}+{x}+{y}")
    # Allow resizing just in case content doesn't fit
    dlg.resizable(True, True)
    
    # Main container with padding
    main_frame = ttk.Frame(dlg, padding="20")
    main_frame.pack(fill="both", expand=True)
    
    # Header info
    info_frame = ttk.Frame(main_frame)
    info_frame.pack(fill="x", pady=(0, 20))
    
    ttk.Label(info_frame, text=f"Empleado: {person_name}", font=("Helvetica", 14, "bold")).pack(anchor="center")
    ttk.Label(info_frame, text=f"Cargo: {cargo}", font=("Helvetica", 12)).pack(anchor="center", pady=(5, 0))
    ttk.Label(info_frame, text="Seleccione el tipo de uniforme:", font=("Helvetica", 11)).pack(anchor="center", pady=(15, 0))
    
    # Content area (split 50/50)
    content_frame = ttk.Frame(main_frame)
    content_frame.pack(fill="both", expand=True)
    
    # Configure grid weights to ensure equal width columns
    content_frame.columnconfigure(0, weight=1)
    content_frame.columnconfigure(1, weight=1)
    content_frame.rowconfigure(0, weight=1)
    
    # --- Male Option ---
    male_frame = ttk.LabelFrame(content_frame, text="HOMBRE", padding="15")
    male_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    
    ttk.Label(male_frame, text=male_option, font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(0, 10))
    
    if male_prices:
        ttk.Label(male_frame, text="Precios Referenciales:", font=("Helvetica", 10, "italic")).pack(anchor="w", pady=(0, 5))
        price_container = ttk.Frame(male_frame)
        price_container.pack(fill="both", expand=True)
        
        # Scrollable price list if many items (optional improvement, but simple list is usually fine)
        for i, (prenda, price) in enumerate(sorted(male_prices.items())):
            price_text = f"• {prenda}: S/{price:.2f}"
            ttk.Label(price_container, text=price_text, font=("Helvetica", 10)).pack(anchor="w", pady=2)
    else:
        ttk.Label(male_frame, text="(Precios no disponibles)", foreground="gray", font=("Helvetica", 10, "italic")).pack(pady=20)

    # --- Female Option ---
    female_frame = ttk.LabelFrame(content_frame, text="MUJER", padding="15")
    female_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
    
    ttk.Label(female_frame, text=female_option, font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(0, 10))
    
    if female_prices:
        ttk.Label(female_frame, text="Precios Referenciales:", font=("Helvetica", 10, "italic")).pack(anchor="w", pady=(0, 5))
        price_container_f = ttk.Frame(female_frame)
        price_container_f.pack(fill="both", expand=True)
        
        for i, (prenda, price) in enumerate(sorted(female_prices.items())):
            price_text = f"• {prenda}: S/{price:.2f}"
            ttk.Label(price_container_f, text=price_text, font=("Helvetica", 10)).pack(anchor="w", pady=2)
    else:
        ttk.Label(female_frame, text="(Precios no disponibles)", foreground="gray", font=("Helvetica", 10, "italic")).pack(pady=20)
    
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=(20, 0))
    
    def select_male():
        result[0] = 'HOMBRE'
        dlg.destroy()
    
    def select_female():
        result[0] = 'MUJER'
        dlg.destroy()
    
    # Buttons
    # Use larger buttons
    btn_style = ttk.Style()
    btn_style.configure("Large.TButton", font=("Helvetica", 11))
    
    ttk.Button(button_frame, text="Seleccionar HOMBRE", command=select_male, style="Large.TButton").pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=5)
    ttk.Button(button_frame, text="Seleccionar MUJER", command=select_female, style="Large.TButton").pack(side="right", fill="x", expand=True, padx=(10, 0), ipady=5)
    
    # Wait for dialog to close
    dlg.wait_window()
    
    return result[0]
