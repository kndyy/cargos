# Document Generation Fixes

## Summary
Fixed three critical issues in document generation:

1. **Prenda names in CARGO documents** - Removed occupation prefix from prenda display names
2. **Pricing showing as 0.0** - Fixed prenda type matching for price lookup
3. **Combined documents** - Added page breaks between individual documents

## Changes Made

### 1. Prenda Name Display Fix

**File**: `src/cargos/services/excel_service.py`

**Problem**: 
- Column names in Excel are now formatted as `OCCUPATION_PRENDA` (e.g., `DELIVERY_POLO`, `BAR_CAMISA`)
- Documents were showing full names like "Delivery Polo" instead of just "Polo"

**Solution**:
Modified `_normalize_prenda_type()` to extract only the prenda part:
```python
def _normalize_prenda_type(self, column_name: str) -> str:
    """
    Normalize column name to standard prenda type.
    Column names come in format: "OCCUPATION_PRENDA" (e.g., "DELIVERY_POLO")
    Returns just the prenda part (e.g., "POLO") for pricing lookup.
    """
    col_upper = str(column_name).upper().strip()
    
    # If in OCCUPATION_PRENDA format, extract just the prenda part
    if '_' in col_upper:
        # Split by underscore and take the last part (the prenda name)
        parts = col_upper.split('_')
        return parts[-1]  # Return just "POLO" from "DELIVERY_POLO"
    
    # ... fallback logic ...
```

**Result**:
- CARGO documents now show: "Polo TALLA M" instead of "Delivery Polo TALLA M"
- Prenda names are clean and consistent across all occupations

### 2. Pricing Fix

**Problem**:
- Prices were showing as S/ 0.00 in all documents
- Root cause: `calculate_total_price()` was trying to match `DELIVERY_POLO` against config entries like `POLO`
- The prenda types didn't match, so no prices were found

**Solution**:
- The fix to `_normalize_prenda_type()` also resolves this issue
- Now extracts just "POLO" from "DELIVERY_POLO" before price lookup
- Price matching works correctly: "POLO" matches "POLO" in config

**Result**:
- Prices are now calculated correctly based on:
  - Prenda type (POLO, CAMISA, etc.)
  - Size (S/M/L, XL, XXL)
  - Local (OTHER, TARAPOTO, SAN ISIDRO)
  - Quantity

### 3. Page Breaks in Combined Documents

**File**: `src/cargos/services/excel_service.py`

**Problem**:
- Combined documents concatenated all individual documents without page breaks
- Made it hard to distinguish where one person's document ended and another began
- Initial implementation with `docxcompose.Composer` was causing issues

**Solution**:
Modified `_create_combined_docx()` to use `python-docx` directly with proper page breaks:
```python
def _create_combined_docx(self, individual_docs: List[Path], output_path: Path) -> None:
    """Combine multiple DOCX files into one document with page breaks between each."""
    from docx import Document
    
    # Load the first document as the master
    master_doc = Document(str(first_doc_path))
    
    # Append remaining documents with page breaks
    for doc_path in individual_docs[1:]:
        # Add a page break before the next document
        master_doc.add_page_break()
        
        # Load the document to append
        doc_to_append = Document(str(doc_path))
        
        # Copy all elements from the document to append
        for element in doc_to_append.element.body:
            master_doc.element.body.append(element)
    
    # Save the combined document
    master_doc.save(str(output_path))
```

**Key Implementation Details**:
- Uses `python-docx` native `add_page_break()` method instead of `docxcompose.Composer`
- Directly manipulates the document XML elements to copy content
- More reliable than trying to use `Composer` with manual page breaks

**Result**:
- Each person's document starts on a new page in the combined file
- Easy to print and separate documents
- Professional formatting
- No dependency on `docxcompose` package

## Testing

To verify the fixes:

1. **Test Prenda Names**:
   - Generate CARGO documents
   - Check that prendas show as "Polo TALLA M", "Camisa TALLA L", etc.
   - Verify NO occupation prefix appears (no "Delivery Polo", "Bar Camisa", etc.)

2. **Test Pricing**:
   - Generate AUTORIZACION and CARGO documents
   - Verify monto shows actual prices (not S/ 0.00)
   - Check that prices match the configuration for the person's occupation and local

3. **Test Combined Documents**:
   - Enable "Combine per local" option
   - Generate documents for multiple people
   - Open the combined DOCX file
   - Verify each person's document starts on a new page

## Technical Details

### Column Name Flow
```
Excel Column: "DELIVERY_POLO"
    ↓
_normalize_prenda_type() extracts: "POLO"
    ↓
_get_display_name() formats: "Polo"
    ↓
_format_prenda_string() adds size: "Polo TALLA M"
    ↓
Document shows: "Polo TALLA M"
```

### Pricing Flow
```
Excel Column: "DELIVERY_POLO" with qty=2, size=M
    ↓
_normalize_prenda_type() extracts: "POLO"
    ↓
calculate_total_price() matches: "POLO" in config
    ↓
_resolve_price() gets: price_sml_other = 25.00
    ↓
Total: 25.00 × 2 = S/ 50.00
```

## Files Modified

1. `src/cargos/services/excel_service.py`:
   - `_normalize_prenda_type()` - Extract prenda part only
   - `_get_display_name()` - Updated documentation
   - `_create_combined_docx()` - Added page breaks

## Backward Compatibility

These changes maintain backward compatibility:
- Legacy column names (without occupation prefix) still work via fallback logic
- Existing config.json format unchanged
- All existing functionality preserved

