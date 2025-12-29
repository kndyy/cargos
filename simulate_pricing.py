"""Dump quantities and pricing info for the test file"""
import pandas as pd
import json
import os
import sys

# Simulation of ExcelService/UnifiedConfig logic
def normalize_prenda_type(col_name):
    parts = col_name.split("_")
    # This matches the current logic in excel_service.py
    if len(parts) >= 3:
        return "_".join(parts[2:])
    return col_name

# Load config
with open('config.json', 'r') as f:
    config_data = json.load(f)

# Build a mapping for easier lookup
class MockUnifiedConfig:
    def __init__(self, data):
        self.occupations = data['occupations']
        self.synonyms = {}
        for occ in self.occupations:
            for syn in occ['synonyms']:
                self.synonyms[syn.upper().strip()] = occ
    
    def normalize_occupation(self, cargo):
        occ = self.synonyms.get(str(cargo).upper().strip())
        return occ['name'] if occ else str(cargo).upper()

    def get_occupation(self, name):
        for occ in self.occupations:
            if occ['name'] == name:
                return occ
        return None

mock_service = MockUnifiedConfig(config_data)

# Load Excel
file_path = 'sources/pruebitaaaaa uniformes} (2).xlsx'
df = pd.read_excel(file_path, sheet_name='MIRAFLORES', header=7, engine='openpyxl')

# Identify uniform columns (starting from col J / index 9)
uniform_cols = df.columns[9:]
print(f"Detected {len(uniform_cols)} uniform columns starting from {uniform_cols[0]}")

# Manual mapping (since we're simulating the service)
# This mimics UNIFORM_COLUMN_MAPPING from constants.py
col_mapping = {
    9: "LIMA_ICA_SALON_CAMISA",
    10: "LIMA_ICA_SALON_BLUSA",
    11: "LIMA_ICA_SALON_MANDILON",
    12: "LIMA_ICA_SALON_ANDARIN",
    33: "LIMA_ICA_CAJA_CAMISA",
    34: "LIMA_ICA_CAJA_SACO_H",
    35: "LIMA_ICA_CAJA_BLUSA",
    36: "LIMA_ICA_CAJA_SACO_M",
    39: "LIMA_ICA_MANTENIMIENTO_CHAQUETA",
    40: "LIMA_ICA_MANTENIMIENTO_POLO",
    41: "LIMA_ICA_MANTENIMIENTO_PANTALON",
    42: "LIMA_ICA_ADMINISTRACION_CAMISA",
    43: "LIMA_ICA_ADMINISTRACION_SACO_H",
}

print("\n=== Person Analysis ===\n")
for i, row in df.iterrows():
    name = row.get('APELLIDOS Y NOMBRES')
    cargo = row.get('CARGO')
    if pd.isna(name) or pd.isna(cargo): continue
    
    norm_cargo = mock_service.normalize_occupation(cargo)
    occ_obj = mock_service.get_occupation(norm_cargo)
    
    found_prendas = []
    total_price = 0
    
    # Scan columns
    for col_idx in range(9, len(row)):
        val = row.iloc[col_idx]
        if pd.notna(val) and val != "" and (isinstance(val, (int, float)) and val > 0):
            col_name = col_mapping.get(col_idx, f"COL_{col_idx}")
            prenda_type = normalize_prenda_type(col_name)
            
            # Lookup price in config
            price = 0
            if occ_obj:
                # Find prenda in occupation
                # Some prendas in config are "CAMISA", but prenda_type is "SALON_CAMISA" or "CAJA_CAMISA"
                # This is the likely bug!
                target = prenda_type
                # Try to clean it: if it contains a _, take the part after the first _
                # but only if it matches something
                # Wait, Produccion has HORNERO, PARRILLERO, etc.
                # All map to PRODUCCION in config.
                # In config, Produccion has "PANTALON", "CHAQUETA", etc.
                # In Excel, MANTENIMIENTO has "MANTENIMIENTO_PANTALON"
                
                # Let's see what normalize_prenda_type returns
                found = False
                for p in occ_obj['prendas']:
                    if p['prenda_type'].upper() == prenda_type.upper():
                        price = p.get('price_sml_other', 0)
                        found = True
                        break
                
                # Try fallback if not found
                if not found and "_" in prenda_type:
                    base_type = prenda_type.split("_")[-1]
                    for p in occ_obj['prendas']:
                        if p['prenda_type'].upper() == base_type.upper():
                            price = p.get('price_sml_other', 0)
                            found = True
                            prenda_type = f"{prenda_type} (mapped to {base_type})"
                            break
            
            found_prendas.append(f"{prenda_type} x{val} (@{price})")
            total_price += price * val

    print(f"[{i+9}] {name[:20]:20} | Cargo: {cargo:15} -> {norm_cargo:15} | Total: {total_price:6.2f}")
    if found_prendas:
        print(f"      Prendas: {', '.join(found_prendas)}")
