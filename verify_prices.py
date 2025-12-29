"""
Price Verification Script - Compare prices from precios.xlsm with config.json
"""
import pandas as pd
import json

# Load prices from Excel
print("Loading precios.xlsm...")
df = pd.read_excel('sources/precios.xlsm', sheet_name='Movimientos', engine='openpyxl')
excel_prices = df[['GRUPO', 'CARGO ESTANDAR', 'MATERIAL', 'TALLA', 'Precio Unit']].drop_duplicates()

# Load config.json
print("Loading config.json...")
with open('config.json', 'r') as f:
    config = json.load(f)

print("\n=== ALL PRICES FROM precios.xlsm ===\n")
excel_prices_sorted = excel_prices.sort_values(['GRUPO', 'CARGO ESTANDAR', 'MATERIAL'])
for _, row in excel_prices_sorted.iterrows():
    print(f"{row['GRUPO'][:25]:25} | {row['CARGO ESTANDAR'][:20]:20} | {row['MATERIAL'][:35]:35} | {row['TALLA']:5} | S/{row['Precio Unit']}")

print("\n\n=== CONFIG.JSON OCCUPATION PRICES ===\n")
for occ in config.get('occupations', []):
    print(f"\n{occ['name']} ({occ['display_name']}):")
    for p in occ.get('prendas', []):
        pt = p.get('prenda_type', '?')
        sml_other = p.get('price_sml_other', 0)
        sml_tarapoto = p.get('price_sml_tarapoto', 0)
        sml_san_isidro = p.get('price_sml_san_isidro', 0)
        if sml_other > 0 or sml_tarapoto > 0 or sml_san_isidro > 0:
            print(f"  {pt:20}: other={sml_other}, tarapoto={sml_tarapoto}, san_isidro={sml_san_isidro}")

print("\n\n=== MAPPING CHECK ===")
print("GRUPO in Excel -> price field in config.json:")
print("  'LIMA E ICA PROVINCIA' -> 'other' (since most locations are here)")
print("  'PATIO DE COMIDA' -> 'other' (mapped same as LIMA)")
print("  'TARAPOTO' -> 'tarapoto' (for Tarapoto stores)")
print("  'SAN ISIDRO' -> 'san_isidro' (for San Isidro/Villa stores)")
