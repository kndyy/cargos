# Learnings: Prenda-to-CLAVE Mismatch Fix

## Implementation Date: 2026-02-01

## What Was Built

### Hierarchical Pre-Filtering System
Refactored `find_best_clave()` in `price_loader.py` to use a three-stage filtering approach:

1. **Stage 1: Location + Cargo Filter**
   - Method: `_get_candidates_by_location_cargo()`
   - Reduces 400+ CLAVEs to ~10 relevant ones
   - Uses exact matching on normalized location and cargo

2. **Stage 2: Garment Filter**
   - Method: Built into `find_best_clave()`
   - Further reduces ~10 CLAVEs to ~2 matching the garment type
   - Filters by checking if target_garment (CAMISA, CORBATA, etc.) exists in material name

3. **Stage 3: Scoring**
   - Method: `_calculate_match_score()`
   - Scores only the remaining 1-2 candidates
   - Preserves original weights: Location+100, Cargo+50/40, Gender+30, Garment+30, Keywords+5×n

### Key Design Decisions

#### Why Hierarchical Filtering Works
The original bug occurred because SACO NEGRO ADM HOMBRE had explicit `gender: "HOMBRE"` in metadata (+30 points), while CAMISA OXFORD CELESTE had `gender: null` (0 points). Even though CAMISA had a garment match (+30), SACO's gender bonus allowed it to win.

With hierarchical filtering:
- Stage 2 removes SACO from consideration when looking for CAMISA
- SACO never gets to compete, so its gender bonus is irrelevant
- CAMISA OXFORD CELESTE wins by default as the only CAMISA candidate

#### Fallback Strategy
If Stage 1 (Location+Cargo) returns no candidates:
- Falls back to Location-only search
- This handles edge cases where cargo normalization might not match exactly

If Stage 2 (Garment) returns no candidates:
- Logs a warning but continues with Stage 1 results
- This handles cases where a garment column exists but no matching CLAVE (rare)

### Code Structure

```python
# New helper methods added:
def _get_candidates_by_location_cargo(self, loc_norm: str, cargo_norm: str) -> Dict[str, Dict[str, Any]]
def _get_candidates_by_location(self, loc_norm: str) -> Dict[str, Dict[str, Any]]
def _calculate_match_score(self, metadata: Dict[str, Any], loc_norm: str, cargo: str, 
                          target_garment: Optional[str], col_keywords_set: set) -> float

# Refactored main method:
def find_best_clave(self, location_group: str, cargo: str, column_name: str, talla: str = None) -> Optional[str]
```

### Performance Impact
- **Before**: Scored all 400+ CLAVEs for every price lookup
- **After**: Scores 5-10 CLAVEs (97.5% reduction in scoring operations)
- **Result**: Faster price calculations, especially for large Excel files

## Testing Notes

### Manual Verification Required
Since this is a Tkinter GUI application without automated tests, verification requires:
1. Running `python run.py`
2. Loading `sources/informacion-uniformes.xlsx`
3. Checking logs for STAFF ADMINISTRATIVO entries
4. Verifying correct CLAVE mappings:
   - CAMISA → CAMISA OXFORD CELESTE (S/. 18.0)
   - CORBATA → CORBATA (S/. 9.0)
   - POLO → POLO PIQUÉ PIZARRA RX... (S/. 13.5)

### Expected Log Output
```
[NAME] OK LIMA_ICA_ADMINISTRACION_CAMISA -> CLAVE: LIMA E ICA PROVINCIA|STAFF ADMINISTRATIVO|CAMISA OXFORD CELESTE = S/. 18.0 x [qty]
[NAME] OK LIMA_ICA_ADMINISTRACION_CORBATA -> CLAVE: LIMA E ICA PROVINCIA|STAFF ADMINISTRATIVO|CORBATA = S/. 9.0 x [qty]
[NAME] OK LIMA_ICA_ADMINISTRACION_POLO -> CLAVE: LIMA E ICA PROVINCIA|STAFF ADMINISTRATIVO|POLO PIQUÉ... = S/. 13.5 x [qty]
```

### Price Calculation Verification
For a person with 2× each prenda:
- **Before (bug)**: S/. 360.0 (all priced as SACO at S/. 60)
- **After (fixed)**: S/. 81.0 (18×2 + 9×2 + 13.5×2)

## Commit Reference
- **Commit**: `87c99ba refactor(pricing): use hierarchical pre-filtering in find_best_clave`
- **Files Changed**: `src/cargos/services/price_loader.py`
- **Lines Changed**: ~+150/-80 (net addition of helper methods and refactoring)

## Future Considerations

### Potential Enhancements
1. **Add automated tests**: Create `test_price_loader.py` with unit tests for the filtering logic
2. **Performance metrics**: Add timing logs to measure actual performance improvement
3. **Cache optimization**: Consider indexing CLAVEs by (location, cargo) for even faster lookups

### Edge Cases to Monitor
1. **New garment types**: If new garment types are added to `precios.xlsm`, they need to be added to `garment_patterns`
2. **Cargo synonyms**: The normalization service must keep cargo names in sync with `precios.xlsm`
3. **Multi-garment CLAVEs**: If a CLAVE ever contains multiple garment types (e.g., "CAMISA Y CORBATA SET"), the current logic would match it for either garment

## Related Files
- `src/cargos/services/price_loader.py` - Main implementation
- `src/cargos/services/excel_service.py` - Calls `find_best_clave()` during price calculation
- `prices_cache.json` - Contains CLAVE metadata used for filtering
- `config.json` - Contains cargo synonyms for normalization
