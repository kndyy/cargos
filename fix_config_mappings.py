"""
Fix config.json occupation mappings:
1. Add base synonyms (CAJA, STAFF ADMINISTRATIVO, ANFITRIONAJE) to gendered occupations
2. Add missing occupations (AUDITORIA, COUNTER)
"""
import json

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Track changes
changes = []

# 1. Add synonyms to existing occupations
synonym_additions = {
    "CAJA (HOMBRE)": ["CAJA", "CAJERO"],
    "CAJA (MUJER)": ["CAJERA"],
    "STAFF ADMINISTRATIVO (HOMBRE)": ["STAFF ADMINISTRATIVO", "ADMINISTRATIVO", "ADMIN"],
    "STAFF ADMINISTRATIVO (MUJER)": ["ADMINISTRATIVA"],
    "ANFITRIONAJE (HOMBRE)": ["ANFITRION"],
    "ANFITRIONAJE (MUJER)": ["ANFITRIONAJE", "ANFITRIONA"],
}

for occ in config.get('occupations', []):
    name = occ.get('name', '')
    if name in synonym_additions:
        current_synonyms = set(occ.get('synonyms', []))
        new_synonyms = synonym_additions[name]
        for syn in new_synonyms:
            if syn not in current_synonyms:
                occ['synonyms'].append(syn)
                changes.append(f"Added synonym '{syn}' to {name}")

# 2. Add missing occupations
# Check if AUDITORIA exists
auditoria_exists = any(o['name'] == 'AUDITORIA' for o in config['occupations'])
if not auditoria_exists:
    config['occupations'].append({
        "name": "AUDITORIA",
        "display_name": "Auditoría",
        "synonyms": ["AUDITORIA", "AUDITORÍA", "AUDITOR", "AUDITORA"],
        "prendas": [
            {
                "prenda_type": "POLO",
                "display_name": "Polo",
                "has_sizes": True,
                "garment_type": "UPPER",
                "is_required": False,
                "default_quantity": 0,
                "is_primary": True,
                "price_sml_other": 13.5,
                "price_xl_other": 13.5,
                "price_xxl_other": 15.0,
                "price_sml_tarapoto": 0.0,
                "price_xl_tarapoto": 0.0,
                "price_xxl_tarapoto": 0.0,
                "price_sml_san_isidro": 0.0,
                "price_xl_san_isidro": 0.0,
                "price_xxl_san_isidro": 0.0
            }
        ],
        "is_active": True,
        "description": "Personal de auditoría"
    })
    changes.append("Added occupation AUDITORIA")

# Check if COUNTER exists
counter_exists = any(o['name'] == 'COUNTER' for o in config['occupations'])
if not counter_exists:
    config['occupations'].append({
        "name": "COUNTER",
        "display_name": "Counter",
        "synonyms": ["COUNTER", "COUNTER F/T", "COUNTER P/T"],
        "prendas": [
            {
                "prenda_type": "POLO",
                "display_name": "Polo",
                "has_sizes": True,
                "garment_type": "UPPER",
                "is_required": False,
                "default_quantity": 0,
                "is_primary": True,
                "price_sml_other": 13.5,
                "price_xl_other": 13.5,
                "price_xxl_other": 15.0,
                "price_sml_tarapoto": 0.0,
                "price_xl_tarapoto": 0.0,
                "price_xxl_tarapoto": 0.0,
                "price_sml_san_isidro": 0.0,
                "price_xl_san_isidro": 0.0,
                "price_xxl_san_isidro": 0.0
            },
            {
                "prenda_type": "GORRA",
                "display_name": "Gorra",
                "has_sizes": False,
                "garment_type": "UPPER",
                "is_required": False,
                "default_quantity": 0,
                "is_primary": False,
                "price_sml_other": 5.0,
                "price_xl_other": 5.0,
                "price_xxl_other": 5.0,
                "price_sml_tarapoto": 0.0,
                "price_xl_tarapoto": 0.0,
                "price_xxl_tarapoto": 0.0,
                "price_sml_san_isidro": 0.0,
                "price_xl_san_isidro": 0.0,
                "price_xxl_san_isidro": 0.0
            }
        ],
        "is_active": True,
        "description": "Personal de counter/mostrador"
    })
    changes.append("Added occupation COUNTER")

# Save updated config
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print("=== CONFIG.JSON UPDATED ===\n")
for change in changes:
    print(f"  ✓ {change}")

if not changes:
    print("  No changes needed - all mappings already exist")

print(f"\n{len(changes)} changes made to config.json")
