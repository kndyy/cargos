"""
Script to inspect the Excel file structure for hierarchical pricing.
Analyzes rows 5, 6, and 7 to understand the location/occupation/prenda hierarchy.
"""
import pandas as pd
from pathlib import Path

# Read the Excel file without headers to see raw structure
file_path = Path("sources/informacion-uniformes.xlsx")

print("=" * 80)
print(f"Inspecting: {file_path}")
print("=" * 80)

# Read entire sheet without headers
xl = pd.ExcelFile(file_path)
print(f"\nSheets available: {xl.sheet_names}")

for sheet_name in xl.sheet_names[:2]:  # First 2 sheets
    print(f"\n{'='*80}")
    print(f"SHEET: {sheet_name}")
    print("=" * 80)
    
    df = pd.read_excel(xl, sheet_name=sheet_name, header=None)
    
    # Show first 10 rows to understand structure
    print(f"\nTotal rows: {len(df)}, Total columns: {len(df.columns)}")
    
    # Focus on rows 5, 6, 7 (0-indexed: 4, 5, 6) which contain location and occupation headers
    print("\n--- ROW 5 (0-indexed row 4) - Likely LOCATION GROUP headers ---")
    row5 = df.iloc[4] if len(df) > 4 else pd.Series()
    # Show non-empty values
    for col_idx, val in enumerate(row5):
        if pd.notna(val) and str(val).strip():
            col_letter = chr(65 + col_idx) if col_idx < 26 else f"A{chr(65 + col_idx - 26)}"
            print(f"  Column {col_idx} ({col_letter}): {val}")
    
    print("\n--- ROW 6 (0-indexed row 5) - Likely OCCUPATION headers ---")
    row6 = df.iloc[5] if len(df) > 5 else pd.Series()
    for col_idx, val in enumerate(row6):
        if pd.notna(val) and str(val).strip():
            col_letter = chr(65 + col_idx) if col_idx < 26 else f"A{chr(65 + col_idx - 26)}"
            print(f"  Column {col_idx} ({col_letter}): {val}")
    
    print("\n--- ROW 7 (0-indexed row 6) - Likely PRENDA TYPE headers ---")
    row7 = df.iloc[6] if len(df) > 6 else pd.Series()
    for col_idx, val in enumerate(row7):
        if pd.notna(val) and str(val).strip():
            col_letter = chr(65 + col_idx) if col_idx < 26 else f"A{chr(65 + col_idx - 26)}"
            print(f"  Column {col_idx} ({col_letter}): {val}")
    
    print("\n--- ROW 8 (0-indexed row 7) - Likely DATA HEADERS (DNI, CARGO, etc.) ---")
    row8 = df.iloc[7] if len(df) > 7 else pd.Series()
    for col_idx, val in enumerate(row8):
        if pd.notna(val) and str(val).strip():
            col_letter = chr(65 + col_idx) if col_idx < 26 else f"A{chr(65 + col_idx - 26)}"
            print(f"  Column {col_idx} ({col_letter}): {val}")
    
    # Also show some data rows to see cargo values
    print("\n--- SAMPLE DATA ROWS (first 5) ---")
    for row_idx in range(8, min(13, len(df))):
        row_data = df.iloc[row_idx]
        # Get cargo column (usually around column 3)
        cargo_val = row_data.iloc[3] if len(row_data) > 3 else ""
        name_val = row_data.iloc[2] if len(row_data) > 2 else ""
        tienda = row_data.iloc[1] if len(row_data) > 1 else ""
        print(f"  Row {row_idx + 1}: Tienda={tienda}, Name={name_val}, Cargo={cargo_val}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
