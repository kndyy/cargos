#!/usr/bin/env python3
"""Analyze job names from informacion-uniformes.xlsx and precios.xlsx."""
import pandas as pd


def analyze_uniformes(file_path: str):
    """Read rows 6,7,8 from sheets to see job names."""
    print(f"=== ANALYZING {file_path} ===")
    
    with pd.ExcelFile(file_path) as excel:
        print(f"\nSheets: {excel.sheet_names}")
        
        for sheet in ['MIRAFLORES', 'TARAPOTO']:
            if sheet in excel.sheet_names:
                print(f"\n--- Sheet: {sheet} ---")
                # Read header rows
                df = pd.read_excel(excel, sheet_name=sheet, header=None, nrows=10)
                print(f"Rows 6-8 (0-indexed 5-7):")
                for i in range(5, 8):
                    if i < len(df):
                        # Get non-null values
                        row_data = df.iloc[i].dropna().tolist()
                        print(f"  Row {i+1}: {row_data[:20]}...")  # First 20 values


def analyze_precios(file_path: str):
    """Get unique occupations from precios.xlsx."""
    print(f"\n=== ANALYZING {file_path} ===")
    
    df = pd.read_excel(file_path, sheet_name='Precios', header=0)
    
    print(f"\nUnique CARGO ESTANDAR ({df['CARGO ESTANDAR'].nunique()}):")
    for cargo in sorted(df['CARGO ESTANDAR'].unique()):
        print(f"  - {cargo}")
    
    print(f"\nUnique GRUPO ({df['GRUPO'].nunique()}):")
    for grupo in sorted(df['GRUPO'].unique()):
        print(f"  - {grupo}")
    
    # Find gendered materials
    print(f"\nGendered MATERIALS (containing HOMBRE or MUJER):")
    for mat in sorted(df['MATERIAL'].unique()):
        mat_upper = str(mat).upper()
        if 'HOMBRE' in mat_upper or 'MUJER' in mat_upper:
            print(f"  - {mat}")
    
    # Find materials with BLUSA (female) vs CAMISA (male)
    print(f"\nGendered by type (BLUSA=female, CAMISA=male):")
    blusa_cargos = set()
    camisa_cargos = set()
    for _, row in df.iterrows():
        mat = str(row['MATERIAL']).upper()
        cargo = row['CARGO ESTANDAR']
        if 'BLUSA' in mat:
            blusa_cargos.add(cargo)
        if 'CAMISA' in mat:
            camisa_cargos.add(cargo)
    
    print(f"  BLUSA occupations: {blusa_cargos}")
    print(f"  CAMISA occupations: {camisa_cargos}")
    print(f"  Both (gendered): {blusa_cargos & camisa_cargos}")


if __name__ == "__main__":
    analyze_uniformes("sources/informacion-uniformes.xlsx")
    analyze_precios("sources/precios.xlsx")
