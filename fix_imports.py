#!/usr/bin/env python3
"""
Script to fix imports in refactored files.
"""
import re
from pathlib import Path

# Define import mappings
IMPORT_MAPPINGS = {
    # Old import -> New import
    r'from models import': 'from cargos.core.models import',
    r'from constants import': 'from cargos.core.constants import',
    r'from validators import': 'from cargos.core.validators import',
    r'from services import': 'from cargos.services.excel_service import',
    r'from config_manager import': 'from cargos.services.config_manager import',
    r'from unified_config_service import': 'from cargos.services.unified_config_service import',
    r'from ui_components import': 'from cargos.ui.ui_components import',
    r'^import models$': 'from cargos.core import models',
    r'^import constants$': 'from cargos.core import constants',
    r'^import validators$': 'from cargos.core import validators',
}

def fix_file_imports(file_path: Path):
    """Fix imports in a single file."""
    if not file_path.exists():
        return False
    
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    # Apply each mapping
    for old_pattern, new_import in IMPORT_MAPPINGS.items():
        content = re.sub(old_pattern, new_import, content, flags=re.MULTILINE)
    
    # Write back if changed
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print(f"✅ Fixed: {file_path}")
        return True
    else:
        print(f"⏭️  Skipped: {file_path} (no changes needed)")
        return False

def main():
    """Fix all imports in src/cargos."""
    src_dir = Path("src/cargos")
    
    if not src_dir.exists():
        print("❌ src/cargos directory not found!")
        return
    
    print("🔧 Fixing imports in refactored files...")
    print()
    
    # Find all Python files
    python_files = list(src_dir.rglob("*.py"))
    
    fixed_count = 0
    for file_path in python_files:
        if file_path.name == "__init__.py":
            continue  # Skip __init__.py files
        
        if fix_file_imports(file_path):
            fixed_count += 1
    
    print()
    print(f"✅ Fixed {fixed_count} files")

if __name__ == "__main__":
    main()

