import json
import sys, os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/back"))
sys.path.insert(0, path)

from rules.rule_013_imagen_base64_edificio_rule_multilang import ImagenBase64EdificioRule
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
    (rule for rule in cache_data["rules"]["common_rules"] if rule["class"] == "ImagenBase64EdificioRule"),
    None
)

if not rule_data:
    raise ValueError("No se encontró la regla 'ImagenBase64EdificioRule' en el JSON de caché.")

rule = ImagenBase64EdificioRule(rule_data)
result = rule.validate(epc)

if isinstance(result, dict):
    for key, value in result.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                print(f"  - {k}: {v}")
        else:
            print(f"{key}: {value}")
else:
    print(result)

from utils_multilang_test import print_multilang_result
print_multilang_result(result)
