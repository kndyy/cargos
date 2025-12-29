"""Analyze MIRAFLORES sheet for all occupations"""
import pandas as pd
import json

# Load the MIRAFLORES sheet
df = pd.read_excel('sources/pruebitaaaaa uniformes} (2).xlsx', 
                   sheet_name='MIRAFLORES', header=7, engine='openpyxl')

print('=== MIRAFLORES Sheet Analysis ===')
print(f'Total rows: {len(df)}')
print(f'Columns: {list(df.columns)[:10]}')

# Get all unique CARGOs
if 'CARGO' in df.columns:
    cargos = df['CARGO'].dropna().unique()
    print(f'\nAll unique CARGOs ({len(cargos)}):')
    for cargo in sorted(cargos):
        count = len(df[df['CARGO'] == cargo])
        print(f'  - {cargo} ({count} rows)')

# Load config for mapping check
with open('config.json', 'r') as f:
    config = json.load(f)

config_occs = set()
config_synonyms = {}
for occ in config.get('occupations', []):
    config_occs.add(occ['name'].upper())
    for syn in occ.get('synonyms', []):
        config_synonyms[syn.upper()] = occ['name']

print('\n=== MAPPING CHECK ===')
for cargo in sorted(cargos):
    upper = str(cargo).upper().strip()
    if upper in config_occs:
        print(f'  ✅ {cargo:30} -> DIRECT')
    elif upper in config_synonyms:
        print(f'  ✅ {cargo:30} -> {config_synonyms[upper]}')
    else:
        print(f'  ❌ {cargo:30} -> NOT FOUND (will get 0.0 price)')
