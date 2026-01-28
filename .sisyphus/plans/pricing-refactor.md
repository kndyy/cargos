# Pricing System Refactor - Cargos Application

## TL;DR

> **Quick Summary**: Refactor the broken pricing system to use exactly 4 location groups from Excel, assign prices at file load time (not generation), display prices in UI, fix empty pages in combined documents, and remove all dead code.
> 
> **Deliverables**:
> - Consolidated location groups (4 only, no 'other' fallback)
> - Prices shown in UI preview after loading Excel
> - Empty pages eliminated from combined documents
> - 17 dead code files deleted
> - Cleaner, more maintainable pricing flow
> 
> **Estimated Effort**: Medium (8-12 hours)
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Task 1 (location groups) -> Task 3 (price injection) -> Task 4 (UI display)

---

## Context

### Original Request
Refactor the broken pricing system in the Cargos Python Tkinter application. The system currently has:
- 6 location groups with fuzzy mapping (need exactly 4)
- Prices calculated at document generation time (need at load time)
- No price display in UI preview
- Empty pages appearing in combined documents
- Significant dead code from debugging sessions

### Interview Summary
**Key Discussions**:
- SAN ISIDRO should map to VILLA STEAKHOUSE (already does in code, but san_isidro exists as separate group)
- The 'other' fallback location should be eliminated
- precios.xlsm is the authoritative price source with 4 GRUPO values

**Research Findings**:
- `price_service.py` is entirely unused - pricing logic lives in `PriceLoader` and `UnifiedConfigService`
- 16 root-level debug scripts are dead code
- Empty pages caused by: (1) double page breaks in merging, (2) documents for rows with no uniform data
- Price injection point identified: `ExcelService._parse_worksheet` after line ~175

### Metis Review
**Identified Gaps** (addressed):
- Test infrastructure: None exists. Manual verification procedures included.
- Template audit: Added task to check .docx templates for trailing breaks

---

## Work Objectives

### Core Objective
Fix the pricing system to use authoritative Excel data, display prices in UI, and clean up technical debt.

### Concrete Deliverables
- `src/cargos/services/price_loader.py` - Consolidated to 4 location groups
- `src/cargos/core/models.py` - Simplified pricing fields
- `src/cargos/services/excel_service.py` - Price injection at load time, empty page fixes
- `src/cargos/ui/ui_components.py` - Price columns in preview treeview
- Deletion of 17 dead code files

### Definition of Done
- [ ] `python run.py` launches without errors
- [ ] Loading Excel file shows prices in UI preview
- [ ] Generated documents have correct prices (not S/ 0.00)
- [ ] Combined documents have no empty pages between people
- [ ] No 'other' location group references remain
- [ ] All 17 dead files deleted

### Must Have
- Exactly 4 location groups: LIMA_ICA, TARAPOTO, PATIOS_COMIDA, VILLA_STEAKHOUSE
- SAN ISIDRO -> VILLA_STEAKHOUSE mapping preserved
- Price calculation at Excel load time
- Prices visible in UI before generation
- No empty pages in combined documents

### Must NOT Have (Guardrails)
- DO NOT add new location groups
- DO NOT create a 5th or 6th group
- DO NOT change the Excel source file format
- DO NOT modify template .docx content (only inspect)
- DO NOT add test infrastructure (none exists, use manual verification)
- DO NOT refactor beyond pricing system scope

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: NO
- **User wants tests**: Manual-only
- **Framework**: none

### Manual QA Procedures

Each task includes detailed verification using the application itself:

**For UI changes:**
- Launch app with `python run.py`
- Load a sample Excel file
- Verify visual elements appear correctly
- Screenshot for evidence

**For Pricing changes:**
- Load Excel, check prices in UI
- Generate documents, verify prices in .docx files
- Compare against precios.xlsm source values

**For Document Generation:**
- Generate combined documents
- Open in Word/Preview, check for empty pages
- Scroll through all pages, count vs expected

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
├── Task 1: Consolidate location groups (price_loader.py, models.py)
├── Task 2: Delete dead code (17 files)
└── Task 6: Audit templates for trailing breaks

Wave 2 (After Wave 1):
├── Task 3: Inject prices at load time (excel_service.py)
└── Task 5: Fix empty pages in document merging (excel_service.py)

Wave 3 (After Wave 2):
└── Task 4: Add price columns to UI preview (ui_components.py)

Final:
└── Task 7: Integration verification
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 1 | None | 3 | 2, 6 |
| 2 | None | None | 1, 6 |
| 3 | 1 | 4 | 5 |
| 4 | 3 | 7 | None |
| 5 | 1 | 7 | 3 |
| 6 | None | 5 | 1, 2 |
| 7 | 4, 5 | None | None (final) |

### Agent Dispatch Summary

| Wave | Tasks | Recommended Approach |
|------|-------|---------------------|
| 1 | 1, 2, 6 | Parallel execution - independent changes |
| 2 | 3, 5 | Can parallel - both modify excel_service.py but different sections |
| 3 | 4 | Sequential - depends on price injection |
| Final | 7 | Integration testing |

---

## TODOs

### Task 1: Consolidate Location Groups to Exactly 4

**What to do**:
- Remove `'other'` from `LOCATION_GROUP_MAP` in `price_loader.py`
- Update `_normalize_location()` to raise error or use `lima_ica` as default instead of `'other'`
- Remove old price fields from `OccupationPrenda` in `models.py` (keep only new 4-group fields)
- Update `UnifiedConfig._determine_local_group()` in `models.py` to use only 4 groups
- Remove fallback logic in `UnifiedConfig._get_price_for_local_group()`

**Must NOT do**:
- Do NOT add any new location groups
- Do NOT change the LOCATION_GROUP_MAP keys (Excel values)
- Do NOT remove the SAN ISIDRO -> villa_steakhouse mapping

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: None needed - straightforward find/replace in 2 files

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1 (with Tasks 2, 6)
- **Blocks**: Task 3
- **Blocked By**: None

**References**:

**Pattern References**:
- `src/cargos/services/price_loader.py:52-60` - Current LOCATION_GROUP_MAP definition
- `src/cargos/services/price_loader.py:115-118` - _normalize_location() with 'other' fallback
- `src/cargos/core/models.py:149-169` - OccupationPrenda price fields (old + new)
- `src/cargos/core/models.py:190-217` - _determine_local_group() logic

**WHY Each Reference Matters**:
- `price_loader.py:52-60`: The LOCATION_GROUP_MAP is THE source of truth for Excel -> internal group mapping. SAN ISIDRO mapping on line 59 must be preserved.
- `price_loader.py:115-118`: This is where 'other' is returned as default - change to 'lima_ica' or raise error.
- `models.py:149-169`: 18 price fields exist (9 old + 9 new). Delete the 9 old fields (lines 149-158).
- `models.py:190-217`: Parallel location logic exists here - must be synchronized with price_loader.

**Acceptance Criteria**:

- [x] `grep -r "other" src/cargos/services/price_loader.py` returns no location-related matches
- [x] `grep -r "san_isidro" src/cargos/core/models.py` returns 0 matches (san_isidro fields deleted)
- [x] `grep -r "price_sml_other\|price_xl_other\|price_xxl_other" src/` returns 0 matches
- [ ] Manual: Run `python run.py`, load Excel, generate document for SAN ISIDRO location -> price should use villa_steakhouse rates

**Commit**: YES
- Message: `refactor(pricing): consolidate location groups to exactly 4`
- Files: `src/cargos/services/price_loader.py`, `src/cargos/core/models.py`
- Pre-commit: `python -c "from cargos.services.price_loader import PriceLoader; print('OK')"`

---

### Task 2: Delete Dead Code Files

**What to do**:
- Delete 16 root-level debug scripts
- Delete `src/cargos/services/price_service.py`
- Remove unused `price_service` parameter from `ui_components.py` (line ~1349)

**Files to delete**:
```
/Users/leonardocandio/cargos/debug_prenda.py
/Users/leonardocandio/cargos/verify_fix.py
/Users/leonardocandio/cargos/gather_info.py
/Users/leonardocandio/cargos/diag_excel.py
/Users/leonardocandio/cargos/analyze_prices.py
/Users/leonardocandio/cargos/inspect_excel_structure.py
/Users/leonardocandio/cargos/final_verify.py
/Users/leonardocandio/cargos/simulate_pricing.py
/Users/leonardocandio/cargos/check_miraflores.py
/Users/leonardocandio/cargos/test_mapping.py
/Users/leonardocandio/cargos/fix_config_mappings.py
/Users/leonardocandio/cargos/verify_prices.py
/Users/leonardocandio/cargos/extract_prices.py
/Users/leonardocandio/cargos/analyze_excel.py
/Users/leonardocandio/cargos/fix_imports.py
/Users/leonardocandio/cargos/services.py
/Users/leonardocandio/cargos/src/cargos/services/price_service.py
```

**Must NOT do**:
- Do NOT delete `run.py` (active entry point)
- Do NOT delete anything in `src/cargos/` except `price_service.py`

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: None needed - file deletions only

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1 (with Tasks 1, 6)
- **Blocks**: None
- **Blocked By**: None

**References**:

**Pattern References**:
- `src/cargos/ui/ui_components.py:1349` - Unused price_service parameter to remove

**WHY Each Reference Matters**:
- The ui_components.py file has a vestigial parameter that references the dead PriceService class

**Acceptance Criteria**:

- [x] `ls *.py` in project root shows ONLY run.py
- [x] `ls src/cargos/services/` does NOT contain `price_service.py`
- [x] `grep -r "price_service" src/` returns 0 matches
- [x] Manual: `python run.py` launches without import errors

**Commit**: YES
- Message: `chore: remove dead code (17 debug scripts and unused price_service)`
- Files: 17 deleted files + ui_components.py edit
- Pre-commit: `python run.py --help 2>/dev/null || python -c "import sys; sys.path.insert(0,'src'); from cargos.main import main; print('OK')"`

---

### Task 3: Inject Prices at Excel Load Time

**What to do**:
- In `ExcelService._parse_worksheet()`, after creating `combined_data` DataFrame (~line 175):
  - Call a new method `_assign_prices_to_data(combined_data, metadata)`
  - This method iterates rows and calculates price for each uniform item
  - Adds a `total_price` column to the DataFrame
- Create the `_assign_prices_to_data()` method:
  - Use `PriceLoader.get_price()` for each prenda/size/location combination
  - Sum all prices per row
  - Handle missing prices gracefully (log warning, use 0.0)

**Must NOT do**:
- Do NOT remove the existing price calculation in `FileGenerationService` yet (keep as fallback)
- Do NOT change the ExcelData or WorksheetParsingResult dataclass structure

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
- **Skills**: None - requires understanding pandas DataFrame operations

**Parallelization**:
- **Can Run In Parallel**: YES (with Task 5, different sections)
- **Parallel Group**: Wave 2
- **Blocks**: Task 4
- **Blocked By**: Task 1

**References**:

**Pattern References**:
- `src/cargos/services/excel_service.py:175` - Where combined_data is created (injection point)
- `src/cargos/services/excel_service.py:947` - Current price calculation in _get_monto_for_person (reference for logic)
- `src/cargos/services/price_loader.py:243-275` - get_price() method signature and fallback logic
- `src/cargos/services/unified_config_service.py:200-250` - calculate_total_price() current implementation

**API/Type References**:
- `src/cargos/core/models.py:39-55` - WorksheetParsingResult structure (data and uniform_data fields)

**WHY Each Reference Matters**:
- `excel_service.py:175`: This is THE injection point where prices should be calculated
- `excel_service.py:947`: Shows current price calculation logic to replicate at load time
- `price_loader.py:243-275`: The get_price API you'll call for each item
- `unified_config_service.py:200-250`: Alternative pricing logic to understand

**Acceptance Criteria**:

- [x] After loading Excel, `worksheet.data` DataFrame has `total_price` column
- [x] `total_price` values are float, not NaN or None
- [x] Manual: Load Excel in app, check console/log for "Assigned prices to N rows" message
- [ ] Manual: Generate document, verify price matches what would be calculated at generation time

**Commit**: YES
- Message: `feat(pricing): calculate prices at Excel load time`
- Files: `src/cargos/services/excel_service.py`
- Pre-commit: `python -c "import sys; sys.path.insert(0,'src'); from cargos.services.excel_service import ExcelService; print('OK')"`

---

### Task 4: Add Price Columns to UI Preview

**What to do**:
- In `DataPreviewFrame._configure_data_treeview()`, add "Total Price" column
- In `DataPreviewFrame._populate_data_tree()`, read `total_price` from DataFrame and display
- Format price as currency: `f"S/ {price:.2f}"`
- Handle missing price column gracefully (show "-" if not present)

**Must NOT do**:
- Do NOT add individual prenda price columns (just total)
- Do NOT modify the Summary or Uniforms tabs

**Recommended Agent Profile**:
- **Category**: `visual-engineering`
- **Skills**: [`frontend-ui-ux`] - Tkinter UI modifications

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Wave 3 (sequential)
- **Blocks**: Task 7
- **Blocked By**: Task 3

**References**:

**Pattern References**:
- `src/cargos/ui/ui_components.py:727` - _update_data_tree method (column setup)
- `src/cargos/ui/ui_components.py:765` - _populate_data_tree method (row population)
- `src/cargos/ui/ui_components.py:738` - columns_with_occupation list (add Total Price here)

**WHY Each Reference Matters**:
- `ui_components.py:727`: Where column headers are configured for the treeview
- `ui_components.py:765`: Where actual data rows are inserted - add price formatting here
- `ui_components.py:738`: The list that defines visible columns - append 'Total Price'

**Acceptance Criteria**:

- [ ] Manual: Load Excel file in app
- [ ] Manual: Navigate to Data Preview tab
- [ ] Manual: Verify "Total Price" column appears at the end
- [ ] Manual: Verify prices show as "S/ XX.XX" format
- [ ] Manual: Prices match expected values from precios.xlsm

**Commit**: YES
- Message: `feat(ui): display total price in data preview`
- Files: `src/cargos/ui/ui_components.py`
- Pre-commit: `python -c "import sys; sys.path.insert(0,'src'); from cargos.ui.ui_components import DataPreviewFrame; print('OK')"`

---

### Task 5: Fix Empty Pages in Combined Documents

**What to do**:
- In `FileGenerationService._create_combined_docx()` (~line 829):
  - Before adding page break, check if document already ends with a break
  - Skip page break if last element is already a section/page break
- In `FileGenerationService._generate_documents()` or `_build_person_contexts()`:
  - Skip generating documents for people with 0 prendas
  - Add validation: if `prendas` list is empty, skip this person
  - Log warning: "Skipping {name}: no uniform items"

**Must NOT do**:
- Do NOT modify the .docx template files
- Do NOT change the document content structure
- Do NOT remove people from the data entirely (just skip document generation)

**Recommended Agent Profile**:
- **Category**: `unspecified-high`
- **Skills**: None - requires understanding docx structure

**Parallelization**:
- **Can Run In Parallel**: YES (with Task 3, different sections)
- **Parallel Group**: Wave 2
- **Blocks**: Task 7
- **Blocked By**: Task 6 (need template audit results)

**References**:

**Pattern References**:
- `src/cargos/services/excel_service.py:829-836` - _create_combined_docx page break logic
- `src/cargos/services/excel_service.py:454` - _build_person_contexts (where to filter empty)
- `src/cargos/services/excel_service.py:1011` - _build_prendas_list (returns empty list if no items)
- `src/cargos/services/excel_service.py:480` - _generate_documents loop

**WHY Each Reference Matters**:
- `excel_service.py:829-836`: THE location where double page breaks happen
- `excel_service.py:454`: Context building - add filter here for empty prendas
- `excel_service.py:1011`: Returns empty list when no uniform data - use this as filter condition
- `excel_service.py:480`: Main generation loop - can add skip logic here

**Acceptance Criteria**:

- [x] Manual: Generate combined document with test data
- [ ] Manual: Open in Word, view all pages
- [ ] Manual: Count pages matches number of people with uniforms
- [ ] Manual: No blank pages between employee documents
- [x] Check logs for "Skipping {name}: no uniform items" messages

**Commit**: YES
- Message: `fix(docs): eliminate empty pages in combined documents`
- Files: `src/cargos/services/excel_service.py`
- Pre-commit: `python -c "import sys; sys.path.insert(0,'src'); from cargos.services.excel_service import FileGenerationService; print('OK')"`

---

### Task 6: Audit Templates for Trailing Breaks

**What to do**:
- Open `templates/CARGO UNIFORMES.docx` in Word
- Toggle "Show/Hide Paragraph Marks" (Ctrl+Shift+8 or Cmd+8)
- Check if document ends with:
  - Section Break
  - Page Break  
  - Extra paragraph marks after content
- Document findings in this task's completion notes
- If trailing breaks found, note for manual template fix (separate from code)

**Must NOT do**:
- Do NOT modify the template files (just inspect)
- Do NOT automate this check (manual inspection required)

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: None - manual inspection task

**Parallelization**:
- **Can Run In Parallel**: YES
- **Parallel Group**: Wave 1 (with Tasks 1, 2)
- **Blocks**: Task 5 (informational dependency)
- **Blocked By**: None

**References**:

**File References**:
- `templates/CARGO UNIFORMES.docx` - Primary template to inspect
- `templates/50% - AUTORIZACIÓN DESCUENTO DE UNIFORMES (02).docx` - Secondary template

**WHY Each Reference Matters**:
- Templates may contain trailing breaks that cause empty pages when documents are combined

**Acceptance Criteria**:

- [x] Both template files inspected in Word/LibreOffice with paragraph marks visible
- [x] Findings documented: "Template X has/doesn't have trailing breaks"
- [x] If breaks found: Note exact type (Page Break, Section Break, Paragraphs)
- [x] Manual fix performed if needed (delete trailing breaks in template)

**Commit**: NO (informational task, or separate commit if templates modified)

---

### Task 7: Integration Verification

**What to do**:
- Run full application workflow end-to-end
- Verify all acceptance criteria from previous tasks
- Document any issues found
- Confirm all 6 requirements are satisfied

**Must NOT do**:
- Do NOT fix issues in this task (create new tasks if needed)
- Do NOT skip any verification step

**Recommended Agent Profile**:
- **Category**: `quick`
- **Skills**: [`playwright`] if browser verification needed, otherwise manual

**Parallelization**:
- **Can Run In Parallel**: NO
- **Parallel Group**: Final (after all other tasks)
- **Blocks**: None (final task)
- **Blocked By**: Tasks 4, 5

**References**:

**Test Data**:
- `sources/precios.xlsm` - Price source file
- Any sample Excel file with uniform data

**Acceptance Criteria**:

**Full Workflow Test**:
- [x] `python run.py` launches without errors
- [ ] Load Excel file -> No errors, prices calculated (MANUAL VERIFICATION NEEDED)
- [ ] Data Preview shows "Total Price" column with correct values (MANUAL)
- [ ] Generate CARGO documents -> Prices shown correctly (not S/ 0.00) (MANUAL)
- [ ] Generate combined document -> No empty pages (MANUAL)
- [ ] SAN ISIDRO location -> Uses VILLA STEAKHOUSE pricing (MANUAL)

**Code Verification**:
- [x] `grep -r "other" src/cargos/services/price_loader.py` - No 'other' location
- [x] `grep -r "price_service" src/` - No references
- [x] `ls *.py` in root - Only `run.py` remains
- [x] No Python import errors on startup

**Commit**: NO (verification only)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `refactor(pricing): consolidate location groups to exactly 4` | price_loader.py, models.py | Import check |
| 2 | `chore: remove dead code (17 debug scripts and unused price_service)` | 17 deleted + ui_components.py | App launch |
| 3 | `feat(pricing): calculate prices at Excel load time` | excel_service.py | Import check |
| 4 | `feat(ui): display total price in data preview` | ui_components.py | Import check |
| 5 | `fix(docs): eliminate empty pages in combined documents` | excel_service.py | Import check |

---

## Success Criteria

### Verification Commands
```bash
# App launches without errors
python run.py &
sleep 3
pkill -f "python run.py"

# No dead code files remain
ls *.py  # Should only show run.py

# No 'other' location group
grep -r "= 'other'" src/cargos/  # Should return nothing

# No price_service references
grep -r "price_service" src/  # Should return nothing
```

### Final Checklist
- [ ] All 4 location groups working (lima_ica, tarapoto, patios_comida, villa_steakhouse)
- [ ] SAN ISIDRO -> villa_steakhouse mapping works
- [ ] No 'other' fallback location
- [ ] Prices shown in UI preview after loading Excel
- [ ] Documents generate with correct prices
- [ ] Combined documents have no empty pages
- [ ] All 17 dead code files deleted
- [ ] Application launches and runs without errors
