
import logging
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

from cargos.services.excel_service import ExcelService
from cargos.core.constants import LIMA_ICA_COLUMN_MAPPING

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test")

try:
    service = ExcelService(logger)
    data = service.load_excel_file('sources/informacion-uniformes.xlsx')

    print("\n=== VERIFYING ALIGNMENT ===")
    for ws in data.worksheets:
        sheet_name = ws.metadata.sheet_name if ws.metadata else "Unknown"
        print(f"\nSheet: {sheet_name}")
        
        # Check if ws has data
        if ws.data is None or ws.data.empty:
            print("  No data in this sheet.")
            continue

        # Show first 10 people and their extracted uniform data
        for i in range(min(10, len(ws.data))):
            name = ws.data.iloc[i].get('APELLIDOS_Y_NOMBRES', 'UNKNOWN')
            cargo = ws.data.iloc[i].get('CARGO', 'UNKNOWN')
            
            # Get non-zero uniform items from the uniform_data dataframe
            items = []
            if ws.uniform_data is not None and i < len(ws.uniform_data):
                row = ws.uniform_data.iloc[i]
                
                # Just list all non-zero columns for this row
                for col in row.index:
                    val = row[col]
                    try:
                        if val != 0 and str(val).lower() not in ['nan', '0', '0.0', 'none']:
                            items.append(f"{col}={val}")
                    except:
                        pass
            
            print(f"{str(name):<30} | {str(cargo):<20} | {', '.join(items[:5])}{'...' if len(items) > 5 else ''}")

    print("\n=== VERIFYING DUPLICATE COLUMNS ===")
    # Check for duplicate column names in uniform data
    for ws in data.worksheets:
        if ws.uniform_data is not None:
            cols = list(ws.uniform_data.columns)
            duplicates = [c for c in cols if cols.count(c) > 1]
            if duplicates:
                print(f"Sheet '{ws.metadata.sheet_name}': DUPLICATE COLUMNS: {set(duplicates)}")
            else:
                print(f"Sheet '{ws.metadata.sheet_name}': SUCCESS - No duplicate columns.")
        else:
            print(f"Sheet '{ws.metadata.sheet_name}': No uniform data.")

except Exception as e:
    logger.exception("Verification failed")
