
import logging
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'src'))

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('test')

from cargos.services.excel_service import ExcelService, FileGenerationService
from cargos.services.unified_config_service import UnifiedConfigService

# Load services
unified = UnifiedConfigService(logger)
excel_svc = ExcelService(logger)
file_svc = FileGenerationService(logger, unified)

# Load Excel
data = excel_svc.load_excel_file('sources/informacion-uniformes.xlsx')

# Debug prendas list for first ADMINISTRADOR
print('=== DEBUGGING PRENDAS LIST FOR ADMIN ===')
for ws in data.worksheets[:1]:
    if ws.data is None: continue
    for i in range(len(ws.data)):
        row = ws.data.iloc[i]
        cargo = row.get('CARGO', '')
        if 'ADMIN' in str(cargo).upper():
            uniform_row = ws.uniform_data.iloc[i] if ws.uniform_data is not None else None
            talla_superior = file_svc._extract_talla_superior(row)
            
            print(f'Row {i}: {cargo}')
            
            # Show non-zero uniform columns
            if uniform_row is not None:
                print(f'  Uniform Columns with non-zero values:')
                for col in uniform_row.index:
                    val = uniform_row[col]
                    if val != 0 and str(val).lower() not in ['nan', '0', '0.0', 'none']:
                        print(f'    {col} = {val}')
            
            # Build prendas list
            prendas = file_svc._build_prendas_list(uniform_row if uniform_row is not None else row, talla_superior)
            print(f'  Built Prendas:')
            for p in prendas:
                print(f'    {p}')
            break
