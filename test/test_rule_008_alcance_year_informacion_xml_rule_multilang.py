import json
import sys
import os

# Ajustar sys.path para que encuentre los módulos desde src/back
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/back")))

from rules.rule_008_alcance_year_informacion_xml_rule_multilang import AlcanceYearInformacionXMLRule
from core.epc_dto import EpcDto
from utils_multilang_test import print_multilang_result

def cargar_epc(xml_filename):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/back/data"))
    path = os.path.join(base_dir, xml_filename)
    with open(path, "r", encoding="utf-8") as f:
        return EpcDto(f.read())

def cargar_regla():
    cache_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/back/core/rules_cache.json"))
    with open(cache_path, "r", encoding="utf-8") as f:
        rules = json.load(f)
    rule_data = next(
        (r for r in rules["rules"]["common_rules"] if r["id"] == "rule_008"),
        None
    )
    if not rule_data:
        raise ValueError("No se encontró rule_008 en rules_cache.json")
    return AlcanceYearInformacionXMLRule(rule_data)

def test_regla(epc, questions=None):
    regla = cargar_regla()
    question = regla.get_question(epc)
    print("🟡 Pregunta generada:", question)
    result = regla.validate(epc, questions)
    print_multilang_result(result)

# === CASO 1: Compatible directamente ===
print("=== CASO 1: VÁLIDO ===")
epc_valido = cargar_epc("Certificado_008_valido.xml")
test_regla(epc_valido)

# === CASO 2: Requiere confirmación ===
print("\n=== CASO 2: CONFIRMADO POR USUARIO ===")
epc_confirmable = cargar_epc("Certificado_008_confirmable.xml")
test_regla(epc_confirmable, {"rule_008": {"0": True}})

# === CASO 3: Error sin pregunta (por año incompatible con tipo "nuevo") ===
print("\n=== CASO 3: ERROR POR AÑO INCOMPATIBLE ===")
epc_invalido = cargar_epc("Certificado_008_invalido.xml")
test_regla(epc_invalido)
