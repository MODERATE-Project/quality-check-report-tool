import json
import sys, os

# ─────────────────────────────── rutas ────────────────────────────────
path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/back"))
sys.path.insert(0, path)

from rules.rule_025_autoconsumo_fotovoltaico_rule_multilang import AutoconsumoFotovoltaicoRule
from core.epc_dto import EpcDto

DATA_DIR = os.path.join(path, "data")
CACHE_JSON_PATH = os.path.join(path, "core", "rules_cache.json")
EPC_FILE_PATH = os.path.join(DATA_DIR, "1 Bloque de viviendas.xml")

# ──────────────────────── carga XML EPC simulado ──────────────────────
with open(EPC_FILE_PATH, "r", encoding="utf-8") as epc_file:
    epc_content = epc_file.read()
epc = EpcDto(epc_content)

# ─────────────── carga definición de la regla desde cache ─────────────
with open(CACHE_JSON_PATH, "r", encoding="utf-8") as cache_file:
    cache_data = json.load(cache_file)

rule_data = next(
    (rule for rule in cache_data["rules"]["common_rules"]
     if rule["class"] == "AutoconsumoFotovoltaicoRule"),
    None
)

if not rule_data:
    raise ValueError("No se encontró la regla 'AutoconsumoFotovoltaicoRule' en el JSON de caché.")

# ───────────────────────── ejecución de la regla ───────────────────────
rule = AutoconsumoFotovoltaicoRule(rule_data)

user_input = {
    "rule_025_num_paneles": 10,
    "rule_025_potencia_w": 420
}

result = rule.validate(epc, user_input)

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
