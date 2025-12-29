"""
Script to extract prices from precios.xlsm and generate config.json updates
"""
import pandas as pd
import json
from pathlib import Path

def extract_prices(file_path: str = 'sources/precios.xlsm') -> dict:
    """Extract all unique prices from the Movimientos sheet."""
    df = pd.read_excel(file_path, sheet_name='Movimientos', engine='openpyxl')
    
    # Get all unique prices
    prices = df[['GRUPO', 'CARGO ESTANDAR', 'MATERIAL', 'TALLA', 'Precio Unit']].drop_duplicates()
    prices = prices.sort_values(['GRUPO', 'CARGO ESTANDAR', 'MATERIAL', 'TALLA'])
    
    # Create a structured dict
    price_config = {}
    for _, row in prices.iterrows():
        grupo = row['GRUPO']
        cargo = row['CARGO ESTANDAR']
        material = row['MATERIAL']
        talla = row['TALLA']
        price = float(row['Precio Unit'])
        
        if grupo not in price_config:
            price_config[grupo] = {}
        if cargo not in price_config[grupo]:
            price_config[grupo][cargo] = {}
        if material not in price_config[grupo][cargo]:
            price_config[grupo][cargo][material] = {}
        price_config[grupo][cargo][material][talla] = price
    
    return price_config

def print_prices(price_config: dict):
    """Print prices in readable format."""
    for grupo, cargos in price_config.items():
        print(f"\n### {grupo} ###")
        for cargo, materials in cargos.items():
            print(f"\n  {cargo}:")
            for material, tallas in materials.items():
                for talla, price in tallas.items():
                    print(f"    {material[:40]:42} | {talla:5} | S/{price}")

def normalize_prenda_type(material: str) -> str:
    """Normalize material name to prenda type."""
    material_upper = material.upper()
    
    known_prendas = {
        'POLO': ['POLO'],
        'CAMISA': ['CAMISA'],
        'BLUSA': ['BLUSA'],
        'CHAQUETA': ['CHAQUETA'],
        'PANTALON': ['PANTALON', 'PANTALÓN'],
        'PECHERA': ['PECHERA'],
        'GARIBALDI': ['GARIBALDI'],
        'MANDILON': ['MANDILON', 'MANDILÓN'],
        'ANDARIN': ['ANDARIN'],
        'SACO': ['SACO'],
        'GORRA': ['GORRA', 'GORRO'],
        'CASACA': ['CASACA'],
    }
    
    for prenda_type, keywords in known_prendas.items():
        for keyword in keywords:
            if keyword in material_upper:
                return prenda_type
    
    return 'OTHER'

def generate_config_updates(price_config: dict) -> dict:
    """Generate config.json updates from price data."""
    updates = {}
    
    for grupo, cargos in price_config.items():
        # Map grupo to location key
        if 'LIMA' in grupo or 'ICA' in grupo:
            loc_key = 'lima_ica'
        elif 'PATIO' in grupo:
            loc_key = 'patios_comida'
        elif 'VILLA' in grupo or 'SAN ISIDRO' in grupo:
            loc_key = 'villa_steakhouse'
        else:
            loc_key = 'other'
        
        for cargo, materials in cargos.items():
            # Normalize cargo name
            cargo_key = cargo.upper().replace(' / ', '_').replace(' ', '_')
            
            if cargo_key not in updates:
                updates[cargo_key] = {}
            
            for material, tallas in materials.items():
                prenda_type = normalize_prenda_type(material)
                
                if prenda_type not in updates[cargo_key]:
                    updates[cargo_key][prenda_type] = {}
                
                for talla, price in tallas.items():
                    talla_key = 'sml' if talla == 'SML' else ('xl' if talla == 'XL' else 'xxl')
                    price_key = f"price_{talla_key}_{loc_key}"
                    updates[cargo_key][prenda_type][price_key] = price
    
    return updates

if __name__ == '__main__':
    print("=== Extracting prices from precios.xlsm ===")
    
    price_config = extract_prices()
    print_prices(price_config)
    
    print("\n\n=== Generated Config Updates ===")
    updates = generate_config_updates(price_config)
    print(json.dumps(updates, indent=2, ensure_ascii=False))
