# Learnings - Pricing Refactor

## Conventions


## Task 1: Consolidate Location Groups (6 -> 4)

### Changes Made
- `price_loader.py`: Changed `_normalize_location()` default from 'other' to 'lima_ica'
- `models.py`: 
  - Deleted 6 old price fields: price_*_other (3) and price_*_san_isidro (3)
  - Kept tarapoto fields (3) for backward compatibility
  - Changed `default_local_group` from "OTHER" to "lima_ica"
  - Updated `_determine_local_group()` to return 'lima_ica' as default
  - Simplified `_get_price_for_local_group()` by removing fallback logic

### Additional Cleanup Required
Beyond the task-specified files, references existed in:
- `config_manager.py`: Removed old field serialization
- `unified_config_service.py`: Removed old field deserialization, validation, and export
- `excel_service.py`: Changed sample price logging from price_sml_other to price_sml_lima_ica

### Final Location Groups (4 total)
1. lima_ica (default)
2. patios_comida
3. villa_steakhouse
4. tarapoto

### SAN ISIDRO Mapping
SAN ISIDRO is mapped to villa_steakhouse in LOCATION_GROUP_MAP (preserved).

## Dead Code Cleanup (Task 2 - Wave 1)

**Date:** 2026-01-27

**Completed:**
- Deleted 16 root-level debug scripts (debug_prenda.py, verify_fix.py, gather_info.py, diag_excel.py, analyze_prices.py, inspect_excel_structure.py, final_verify.py, simulate_pricing.py, check_miraflores.py, test_mapping.py, fix_config_mappings.py, verify_prices.py, extract_prices.py, analyze_excel.py, fix_imports.py, services.py)
- Deleted src/cargos/services/price_service.py (obsolete service)
- Removed price_service parameter from ConfigurationTab.__init__() in ui_components.py
- Removed self.price_service instance variable assignment

**Verification:**
- Root directory now contains only run.py
- No price_service.py in services directory
- No references to price_service remain in codebase (grep returned 0 matches)
- Application imports successfully (tested with venv activation)

**Key Finding:**
ConfigurationTab was instantiated in main.py (line 110) with only 3 parameters (parent, config, unified_service), so removing the 4th optional parameter (price_service=None) had no breaking changes.

**Pre-existing LSP Warnings:**
LSP reported 11 errors in ui_components.py, but these are unrelated to our changes:
- pandas DataFrame boolean conditional warnings
- Type annotation issues with None/dict parameters
- These existed before the price_service parameter removal

**Impact:**
Codebase is cleaner with 17 fewer files. No functionality broken since price_service was never used (optional parameter never passed by caller).
