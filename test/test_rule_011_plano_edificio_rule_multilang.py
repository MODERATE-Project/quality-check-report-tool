import json
import sys, os

# Ajustar el path para importar módulos desde la carpeta src/back
path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/back"))
sys.path.insert(0, path)

from rules.rule_011_plano_edificio_rule_multilang import PlanoEdificioRule
from core.epc_dto import EpcDto

# Rutas a los directorios y archivos
DATA_DIR = os.path.join(path, "data")
CACHE_JSON_PATH = os.path.join(path, "core", "rules_cache.json")
EPC_FILE_PATH = os.path.join(DATA_DIR, "1 Bloque de viviendas.xml")

# Cargar el archivo EPC
with open(EPC_FILE_PATH, "r", encoding="utf-8") as epc_file:
    epc_content = epc_file.read()

# Crear una instancia de EpcDto con el XML
epc = EpcDto(epc_content)

# Cargar las reglas desde el JSON de caché
with open(CACHE_JSON_PATH, "r", encoding="utf-8") as cache_file:
    cache_data = json.load(cache_file)

# Buscar la regla de tipo 'PlanoEdificioRule'
rule_data = next(
    (rule for rule in cache_data["rules"]["common_rules"] if rule["class"] == "PlanoEdificioRule"),
    None
)

if not rule_data:
    raise ValueError("No se encontró una regla de tipo 'PlanoEdificioRule' en el JSON de caché.")

# Instanciar la regla
rule = PlanoEdificioRule(rule_data)

# Validar el documento EPC
result = rule.validate(epc)

# Imprimir el resultado de manera legible
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

# Mostrar resultados multilingües
from utils_multilang_test import print_multilang_result
print_multilang_result(result)
