
import pandas as pd
import numpy as np

file_path = 'sources/informacion-uniformes.xlsx'
df = pd.read_excel(file_path, sheet_name='miraflores', header=None)

# Headers are at Row 8 (Index 7)
headers = df.iloc[7].tolist()
occupations = df.iloc[6].tolist()

print(f"{'NAME':<30} | {'CARGO':<20} | {'NON-ZERO COLS'}")
print("-" * 80)

# Search for some problematic names from the logs
target_names = [
    'ALDAZ GARCIA GUISELA',
    'RAMIREZ SOLANO CECI LEONOR',
    'TORRES SALAS ANGEL MANUEL',
    'HUAMAN GARCIA CESAR ENRIQUE'
]

for idx, row in df.iloc[8:100].iterrows():
    name = str(row[2]).strip()
    cargo = str(row[3]).strip()
    
    # Check if this name matches any of our targets
    found = False
    for t in target_names:
        if t in name:
            found = True
            break
    
    if found:
        # Find non-zero uniform columns (9 to 70)
        non_zeros = []
        for col_idx in range(9, 71):
            val = row[col_idx]
            if pd.notna(val) and val != 0:
                item_name = str(headers[col_idx])
                occ_group = str(occupations[col_idx])
                non_zeros.append(f"[{col_idx}] {occ_group}/{item_name}={val}")
        
        print(f"{name:<30} | {cargo:<20} | {', '.join(non_zeros)}")

print("\n=== CHECKING OFFSET DISCREPANCY ===")
# Let's check a few generic rows to see if people have values in columns matching their CARGO
for idx, row in df.iloc[8:30].iterrows():
    name = str(row[2]).strip()
    cargo = str(row[3]).strip()
    if cargo == 'nan' or name == 'nan': continue
    
    non_zeros = []
    for col_idx in range(9, 71):
        if pd.notna(row[col_idx]) and row[col_idx] != 0:
            non_zeros.append(col_idx)
    
    print(f"{name:<30} | {cargo:<20} | Indices: {non_zeros}")
