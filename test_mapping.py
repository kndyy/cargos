"""Quick test of occupation mappings"""
import pandas as pd
import json

df = pd.read_excel('sources/precios.xlsm', sheet_name='Movimientos', engine='openpyxl')
excel_occs = set(df['CARGO ESTANDAR'].dropna().unique())

with open('config.json', 'r') as f:
    config = json.load(f)

config_occs = set()
config_synonyms = {}
for occ in config.get('occupations', []):
    config_occs.add(occ['name'].upper())
    for syn in occ.get('synonyms', []):
        config_synonyms[syn.upper()] = occ['name']

print('=== OCCUPATION MAPPING ===\n')
for excel_occ in sorted(excel_occs):
    upper = excel_occ.upper()
    if upper in config_occs:
        print(f'  ✅ {excel_occ:25} -> DIRECT')
    elif upper in config_synonyms:
        print(f'  ✅ {excel_occ:25} -> {config_synonyms[upper]}')
    else:
        print(f'  ❌ {excel_occ:25} -> NOT FOUND')
