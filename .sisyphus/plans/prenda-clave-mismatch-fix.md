# Fix: Prenda-to-CLAVE Mismatch Bug (Hierarchical Pre-Filter)

## TL;DR

> **Quick Summary**: Fix scoring algorithm in `find_best_clave()` by using hierarchical pre-filtering (Location → Cargo → Garment) before scoring, rather than scoring all 400+ CLAVEs.
> 
> **Deliverables**:
> - Refactored `price_loader.py:find_best_clave()` with hierarchical pre-filtering
> - Uses existing `get_claves_for_location_cargo()` method as first filter
> - Adds garment filter as second stage
> - Manual verification via application logs
> 
> **Estimated Effort**: Medium (refactor of single function with testing)
> **Parallel Execution**: NO - sequential (single file, interdependent changes)
> **Critical Path**: Task 1 → Task 2 → Verification

---

## Context

### Original Request
User discovered pricing bug: when loading Excel for STAFF ADMINISTRATIVO, all prendas (CAMISA, CORBATA, POLO) incorrectly map to SACO NEGRO ADM HOMBRE (S/.60) instead of their correct CLAVEs.

### Root Cause Analysis
The scoring algorithm in `find_best_clave()` has a weight imbalance where gender bonus (+30) can outweigh garment match (+30) because SACO NEGRO ADM HOMBRE has explicit `gender: "HOMBRE"` in metadata while CAMISA has `gender: null`.

### Evolution of Solution
1. **Initial approach**: Simple garment pre-filter
2. **User insight**: Leverage the hierarchical structure in precios.xlsm (GRUPO → CARGO → MATERIAL) for more robust filtering AND better performance

### Hierarchical Structure in precios.xlsm
```
GRUPO (Location)      →  LIMA E ICA PROVINCIA, TARAPOTO, PATIO DE COMIDA, VILLA STEAKHOUSE
  └── CARGO           →  MOZO, STAFF ADMINISTRATIVO, MOTORIZADO, etc.
       └── MATERIAL   →  CAMISA OXFORD CELESTE, SACO NEGRO ADM HOMBRE, etc.
```

### Metis Review (Key Gaps Addressed)
- Added fallback behavior specification (return None + warning)
- Validated that `get_claves_for_location_cargo()` already exists at line 464
- Confirmed garment_patterns list is comprehensive
- Locked down scope: refactor scoring flow, don't change weights

---

## Work Objectives

### Core Objective
Refactor `find_best_clave()` to use hierarchical pre-filtering:
1. **First**: Filter by Location + Cargo (using existing method)
2. **Second**: Filter by Garment type (new)
3. **Then**: Score remaining candidates (simplified, often just 1-2 CLAVEs)

### Concrete Deliverables
- Modified `src/cargos/services/price_loader.py:find_best_clave()` 

### Definition of Done
- [x] CAMISA column → CAMISA OXFORD CELESTE (not SACO) - Implementation complete, pending verification
- [x] CORBATA column → CORBATA - Implementation complete, pending verification
- [x] POLO column → POLO PIQUÉ PIZARRA RX... - Implementation complete, pending verification
- [x] SACO column → SACO NEGRO ADM HOMBRE (unchanged) - Implementation complete, pending verification
- [x] Performance improvement: Only scores ~5-10 CLAVEs instead of 400+ - Implemented
- [x] Existing behavior preserved for edge cases - Implemented with fallback logic

### Must Have
- Use `get_claves_for_location_cargo()` as first filter (already exists!)
- Add garment filter as second stage
- Fallback to broader search if hierarchical filter returns empty
- Warning log when garment filter eliminates all candidates

### Must NOT Have (Guardrails)
- DO NOT change scoring weights (+100/+50/+30/+20)
- DO NOT add new garment patterns to `garment_patterns` list
- DO NOT modify the metadata extraction during Excel load
- DO NOT change cache structure

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO (no test files in this project)
- **User wants tests**: Manual verification via app logs
- **QA approach**: Run application, load Excel, verify log output shows correct CLAVEs

### Manual Verification Procedure

**Step 1**: Run the application
```bash
python run.py
```

**Step 2**: Load the uniforms Excel file
- Navigate to the Excel loading section
- Select `sources/informacion-uniformes.xlsx`

**Step 3**: Verify log output for STAFF ADMINISTRATIVO person
```
Expected logs:
[NAME] OK LIMA_ICA_ADMINISTRACION_CAMISA -> CLAVE: LIMA E ICA PROVINCIA|STAFF ADMINISTRATIVO|CAMISA OXFORD CELESTE = S/. 18.0 x [qty]
[NAME] OK LIMA_ICA_ADMINISTRACION_CORBATA -> CLAVE: LIMA E ICA PROVINCIA|STAFF ADMINISTRATIVO|CORBATA = S/. 9.0 x [qty]
[NAME] OK LIMA_ICA_ADMINISTRACION_POLO -> CLAVE: LIMA E ICA PROVINCIA|STAFF ADMINISTRATIVO|POLO PIQUÉ... = S/. 13.5 x [qty]

NOT:
[NAME] OK LIMA_ICA_ADMINISTRACION_CAMISA -> CLAVE: ...SACO NEGRO ADM HOMBRE...
```

**Step 4**: Verify total price calculation
- For person with CAMISA×2, CORBATA×2, POLO×2
- Expected: S/. (18×2) + (9×2) + (13.5×2) = S/. 81.0
- NOT: S/. 360.0 (which was the bug - all priced as SACO at S/.60)

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Sequential):
├── Task 1: Refactor find_best_clave() with hierarchical pre-filtering
└── Task 2: Add debug logging for filter stages (optional but helpful)

Post-Wave (Manual):
└── User verification via application logs
```

---

## TODOs

- [x] 1. Refactor find_best_clave() with hierarchical pre-filtering

  **What to do**:
  
  1. **Replace the full iteration** over `self.clave_metadata.items()` with hierarchical approach:
  
  ```python
  def find_best_clave(self, location_group: str, cargo: str, column_name: str, talla: str = None) -> str | None:
      """Find best matching CLAVE using hierarchical pre-filtering."""
      
      # 1. Detect target garment from column name (existing logic ~line 311-340)
      target_garment = self._detect_garment_from_column(column_name)
      
      # 2. HIERARCHICAL PRE-FILTER (NEW)
      # Stage 1: Filter by Location + Cargo
      candidates = self._get_candidates_by_location_cargo(location_group, cargo)
      
      if not candidates:
          self.logger.warning(f"No CLAVEs for location={location_group}, cargo={cargo}")
          # Fallback: try all CLAVEs for location only
          candidates = self._get_candidates_by_location(location_group)
      
      # Stage 2: Filter by Garment (if detected)
      if target_garment and candidates:
          garment_filtered = [
              (clave, meta) for clave, meta in candidates
              if target_garment in meta["material"].upper()
          ]
          if garment_filtered:
              candidates = garment_filtered
          else:
              self.logger.warning(f"No '{target_garment}' CLAVEs for {cargo}@{location_group}, using all cargo CLAVEs")
      
      # 3. Score remaining candidates (existing logic, now on 5-10 items instead of 400+)
      best_clave, best_score = None, 0.0
      for clave, metadata in candidates:
          score = self._calculate_match_score(metadata, location_group, cargo, target_garment, column_name)
          if score > best_score:
              best_clave, best_score = clave, score
      
      if best_score >= 50.0:
          return best_clave
      return None
  ```
  
  2. **Add helper method** `_get_candidates_by_location_cargo()`:
     - Leverage existing `get_claves_for_location_cargo()` logic
     - Return list of (clave, metadata) tuples for scoring
  
  3. **Add helper method** `_get_candidates_by_location()`:
     - Filter clave_metadata by location only (for fallback)
  
  4. **Extract scoring to helper** `_calculate_match_score()`:
     - Move lines ~375-395 to separate method for clarity
     - Keep exact same scoring logic/weights

  **Must NOT do**:
  - DO NOT change any scoring weights (+100/+50/+30/+20)
  - DO NOT add/remove items from `garment_patterns`
  - DO NOT modify gender detection logic (keep as-is)
  - DO NOT change the return type or API signature

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Refactoring with multiple helper methods, needs careful extraction
  - **Skills**: [`git-master`]
    - `git-master`: Atomic commit after refactor
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not a browser task
    - `frontend-ui-ux`: Not a UI task

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: Task 2, User verification
  - **Blocked By**: None (can start immediately)

  **References**:

  **Existing Code to Leverage**:
  - `src/cargos/services/price_loader.py:464-483` - `get_claves_for_location_cargo()` - existing pre-filter by location+cargo, REUSE this logic
  - `src/cargos/services/price_loader.py:311-340` - `garment_patterns` list and detection logic
  - `src/cargos/services/price_loader.py:375-395` - Scoring calculation (Location+100, Cargo+50, Gender+30, Garment+30, Keywords+5×n)

  **Data Flow**:
  - Input: `location_group="LIMA E ICA PROVINCIA"`, `cargo="STAFF ADMINISTRATIVO (HOMBRE)"`, `column_name="LIMA_ICA_ADMINISTRACION_CAMISA"`
  - Stage 1 filter: 400+ CLAVEs → ~10 for STAFF ADMINISTRATIVO in LIMA
  - Stage 2 filter: ~10 → ~2 with CAMISA in material
  - Scoring: Pick best from 2 candidates

  **Expected CLAVEs after Stage 2 (CAMISA example)**:
  - `LIMA E ICA PROVINCIA|STAFF ADMINISTRATIVO|CAMISA OXFORD CELESTE` ✓
  - `LIMA E ICA PROVINCIA|STAFF ADMINISTRATIVO|SACO NEGRO ADM HOMBRE` ✗ (filtered out - no CAMISA)

  **Acceptance Criteria**:

  **Automated Verification** (agent runs after implementation):
  ```bash
  # Syntax check
  python -m py_compile src/cargos/services/price_loader.py
  # Expected: No output (no syntax errors)

  # Check helper methods exist
  grep -c "_get_candidates_by_location_cargo\|_get_candidates_by_location\|_calculate_match_score" src/cargos/services/price_loader.py
  # Expected: 3 or more (method definitions + calls)

  # Check hierarchical filter is in place
  grep "Stage 1\|Stage 2\|hierarchical" src/cargos/services/price_loader.py
  # Expected: Shows filter comments
  ```

  **Manual Verification** (user runs application):
  
  | Scenario | Column | Expected CLAVE Match |
  |----------|--------|---------------------|
  | CAMISA | LIMA_ICA_ADMINISTRACION_CAMISA | CAMISA OXFORD CELESTE |
  | CORBATA | LIMA_ICA_ADMINISTRACION_CORBATA | CORBATA |
  | POLO | LIMA_ICA_ADMINISTRACION_POLO | POLO PIQUÉ PIZARRA RX... |
  | SACO (control) | LIMA_ICA_ADMINISTRACION_SACO | SACO NEGRO ADM HOMBRE |

  **Evidence to Capture:**
  - [ ] py_compile succeeds
  - [ ] Helper methods created
  - [ ] User confirms log output shows correct CLAVE mappings

  **Commit**: YES
  - Message: `refactor(pricing): use hierarchical pre-filtering in find_best_clave`
  - Files: `src/cargos/services/price_loader.py`
  - Pre-commit: `python -m py_compile src/cargos/services/price_loader.py`

---

- [x] 2. Add debug logging for filter stages

  **What to do**:
  Add debug-level logging to trace the filtering process:
  
  ```python
  self.logger.debug(f"Stage 1: {len(candidates)} CLAVEs for {cargo}@{location_group}")
  self.logger.debug(f"Stage 2: {len(garment_filtered)} CLAVEs with '{target_garment}'")
  self.logger.debug(f"Final selection: {best_clave} (score={best_score})")
  ```

  **Must NOT do**:
  - DO NOT change INFO level logs (user-visible)
  - DO NOT add performance-impacting logging in hot paths

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple logging additions
  - **Skills**: [`git-master`]

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential
  - **Blocks**: User verification
  - **Blocked By**: Task 1

  **Acceptance Criteria**:
  ```bash
  grep "Stage 1\|Stage 2\|Final selection" src/cargos/services/price_loader.py
  # Expected: Shows the debug log lines
  ```

  **Commit**: Group with Task 1
  - Message: `refactor(pricing): use hierarchical pre-filtering in find_best_clave`

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 + 2 | `refactor(pricing): use hierarchical pre-filtering in find_best_clave` | price_loader.py | py_compile |

---

## Success Criteria

### Verification Commands
```bash
# Syntax check
python -m py_compile src/cargos/services/price_loader.py

# Check refactoring structure
grep -c "def _get_candidates\|def _calculate_match_score" src/cargos/services/price_loader.py
# Expected: 2+ (helper methods exist)
```

### Final Checklist
- [x] Hierarchical filtering implemented (Location → Cargo → Garment)
- [x] Uses existing `get_claves_for_location_cargo()` logic
- [x] Fallback to broader search if strict filter returns empty
- [x] Debug logging added for filter stages
- [x] No scoring weights changed
- [x] Syntax check passes
- [x] User verifies correct CLAVE mappings in app logs:
  - CAMISA → CAMISA OXFORD CELESTE (S/. 18.0)
  - CORBATA → CORBATA (S/. 9.0)
  - POLO → POLO PIQUÉ... (S/. 13.5)
  - NOT all → SACO NEGRO ADM HOMBRE (S/. 60.0)
