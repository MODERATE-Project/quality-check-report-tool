import json
import sys, os

# ─────────────────────────────── rutas ────────────────────────────────
path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/back"))
sys.path.insert(0, path)

from rules.rule_020_transmitancia_huecos_rule_multilang import TransmitanciaHuecosRule
from core.epc_dto import EpcDto

DATA_DIR = os.path.join(path, "data")
CACHE_JSON_PATH = os.path.join(path, "core", "rules_cache.json")
EPC_FILE_PATH = "D:\\Proyectos\\2024\\MODERATE\\Ficheros\\02_XMLs\\Example_Dwelling.xml"  #EPC_FILE_PATH = os.path.join(DATA_DIR, "1 Bloque de viviendas.xml")

# ──────────────────────── carga XML EPC simulado ──────────────────────
with open(EPC_FILE_PATH, "r", encoding="utf-8") as epc_file:
    epc_content = epc_file.read()
epc = EpcDto(epc_content)

# ─────────────── carga definición de la regla desde cache ─────────────
with open(CACHE_JSON_PATH, "r", encoding="utf-8") as cache_file:
    cache_data = json.load(cache_file)

rule_data = next(
    (rule for rule in cache_data["rules"]["common_rules"]
     if rule["class"] == "TransmitanciaHuecosRule"),
    None
)

if not rule_data:
    raise ValueError("No se encontró la regla 'TransmitanciaHuecosRule' en el JSON de caché.")

# ───────────────────────── ejecución de la regla ───────────────────────
rule = TransmitanciaHuecosRule(rule_data)
result = rule.validate(epc)

# ─────────────────────── impresión legible del resultado ───────────────
for key, value in result.items():
    if isinstance(value, dict):
        print(f"{key}:")
        for k, v in value.items():
            print(f"  - {k}: {v}")
    else:
        print(f"{key}: {value}")

# ─────────────────────── impresión multilingüe (si aplica) ─────────────
from utils_multilang_test import print_multilang_result
print_multilang_result(result)
