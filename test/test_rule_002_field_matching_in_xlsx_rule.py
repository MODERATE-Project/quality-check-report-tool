import json
import os
import sys, os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/back'))
sys.path.insert(0, path)

from rules.rule_002_field_matching_in_xlsx_rule import FieldMatchingInXlsxRule
from core.epc_dto import EpcDto

# Rutas a los directorios y archivos
DATA_DIR = os.path.join(path,"data")
CACHE_JSON_PATH = os.path.join(path,os.path.join("core","rules_cache.json"))
EPC_FILE_PATH = os.path.join(DATA_DIR, "1 Bloque de viviendas.xml")
EXCEL_FILE_PATH = os.path.join(DATA_DIR, "Listado Poblaciones Zonificación Climática Comunidad Valenciana.xlsx")

# Cargar el archivo EPC
with open(EPC_FILE_PATH, "r", encoding="utf-8") as epc_file:
    epc_content = epc_file.read()

# Crear una instancia de EpcDto
epc = EpcDto(epc_content)

# Cargar las reglas desde el JSON de caché
with open(CACHE_JSON_PATH, "r", encoding="utf-8") as cache_file:
    cache_data = json.load(cache_file)

# Buscar la regla de tipo 'FieldMatchingInXlsxRule'
rule_data = next(
    (rule for rule in cache_data["rules"]["common_rules"] if rule["class"] == "FieldMatchingInXlsxRule"),
    None
)

if not rule_data:
    raise ValueError("No se encontró una regla de tipo 'FieldMatchingInXlsxRule' en el JSON de caché.")

# Ajustar la ruta del archivo Excel en los parámetros de la regla
rule_data["parameters"]["valid_values_source"] = EXCEL_FILE_PATH

# Instanciar la regla
rule = FieldMatchingInXlsxRule(rule_data)

# Validar el documento EPC
result = rule.validate(epc)

# Imprimir el resultado
print(result)
