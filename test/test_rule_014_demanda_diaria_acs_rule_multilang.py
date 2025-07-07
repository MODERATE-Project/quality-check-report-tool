import json
import sys, os

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/back"))
sys.path.insert(0, path)

from rules.rule_014_demanda_diaria_acs_rule_multilang import DemandaDiariaACSRule
from core.epc_dto import EpcDto

# Rutas a los directorios y archivos
DATA_DIR = os.path.join(path,"data")
CACHE_JSON_PATH = os.path.join(path,os.path.join("core","rules_cache.json"))
EPC_FILE_PATH = "D:\\Proyectos\\2024\\MODERATE\\Ficheros\\02_XMLs\\Example_Dwelling.xml" #os.path.join(DATA_DIR, "1 Bloque de viviendas.xml")
EXCEL_FILE_PATH = os.path.join(DATA_DIR, "Listado Poblaciones Zonificación Climática Comunidad Valenciana.xlsx")

with open(EPC_FILE_PATH, "r", encoding="utf-8") as epc_file:
    epc_content = epc_file.read()
epc = EpcDto(epc_content)

with open(CACHE_JSON_PATH, "r", encoding="utf-8") as cache_file:
    cache_data = json.load(cache_file)

rule_data = next(
    (rule for rule in cache_data["rules"]["common_rules"] if rule["class"] == "DemandaDiariaACSRule"),
    None
)

if not rule_data:
    raise ValueError("No se encontró la regla 'DemandaDiariaACSRule' en el JSON de caché.")

rule = DemandaDiariaACSRule(rule_data)

# Simulamos respuesta del usuario con 3 dormitorios
questions = {"rule_014_0": 3}

result = rule.validate(epc, questions)

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
