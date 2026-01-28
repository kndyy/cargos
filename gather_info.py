
import json
import pandas as pd
import logging
import sys

# Configure basic logging
logging.basicConfig(level=logging.ERROR)

def gather_info():
    # 1. Load Occupations from config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        occupations = [o['name'] for o in config.get('occupations', [])]
        print(f"✅ Loaded {len(occupations)} Configured Occupations:")
        for occ in sorted(occupations):
            print(f"  - {occ}")
    except Exception as e:
        print(f"❌ Error loading config.json: {e}")

    # 2. Load Excel Headers
    excel_path = 'sources/informacion-uniformes.xlsx'
    try:
        df = pd.read_excel(excel_path, sheet_name='miraflores', header=None, nrows=10)
        
        # Row 7 (Index 6) - Occupation/Location Groups
        occ_row = df.iloc[6].tolist()
        # Row 8 (Index 7) - Items
        item_row = df.iloc[7].tolist()
        
        print("\n✅ Excel Column Mapping (Columns J-BS / 9-70):")
        print(f"{'IDX':<4} | {'GROUP HEADER (Row 7)':<30} | {'ITEM HEADER (Row 8)':<20}")
        print("-" * 60)
        
        current_group = ""
        for i in range(9, len(occ_row)):
            val_group = str(occ_row[i]).strip()
            val_item = str(item_row[i]).strip()
            
            if val_group != 'nan' and val_group != '':
                current_group = val_group
            
            if i > 70: break # Stop at known end
            
            print(f"{i:<4} | {current_group:<30} | {val_item:<20}")

    except Exception as e:
        print(f"❌ Error loading Excel headers: {e}")

if __name__ == "__main__":
    gather_info()
