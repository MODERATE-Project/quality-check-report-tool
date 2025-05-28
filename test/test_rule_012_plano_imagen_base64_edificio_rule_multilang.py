import json
import sys, os

# Añadir el path al backend
path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/back"))
sys.path.insert(0, path)

from rules.rule_012_plano_imagen_base64_edificio_rule_multilang import PlanoImagenBase64EdificioRule
from core.epc_dto import EpcDto

DATA_DIR = os.path.join(path, "data")
CACHE_JSON_PATH = os.path.join(path, "core", "rules_cache.json")
EPC_FILE_PATH = os.path.join(DATA_DIR, "Ejemplo xml CYPETHERM.xml")

with open(EPC_FILE_PATH, "r", encoding="utf-8") as epc_file:
    epc_content = epc_file.read()
epc = EpcDto(epc_content)

with open(CACHE_JSON_PATH, "r", encoding="utf-8") as cache_file:
    cache_data = json.load(cache_file)

rule_data = next(
    (rule for rule in cache_data["rules"]["common_rules"] if rule["class"] == "PlanoImagenBase64EdificioRule"),
    None
)
if not rule_data:
    raise ValueError("No se encontró la regla 'PlanoImagenBase64EdificioRule' en el JSON de caché.")

rule = PlanoImagenBase64EdificioRule(rule_data)
result = rule.validate(epc)

if isinstance(result, dict):
    for key, value in result.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  - {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")
else:
    print(result)

from utils_multilang_test import print_multilang_result
print_multilang_result(result)
