import json
import sys, os

# Ajustar el path
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/back'))
sys.path.insert(0, path)

from rules.example_multilang_rule import ExampleMultilangRule
from core.epc_dto import EpcDto

# Datos simulados
xml = """<?xml version="1.0" encoding="UTF-8"?>
<Ruta>
    <Ejemplo>VALOR</Ejemplo>
</Ruta>"""

epc = EpcDto(xml)

# Cargar regla desde archivo json
with open("../rules/example_multilang_rule.json", "r", encoding="utf-8") as f:
    rule_data = json.load(f)


# Instanciar y validar
rule = ExampleMultilangRule(rule_data)
result = rule.validate(epc)

# Usar utilidad de impresión
from utils_multilang_test import print_multilang_result
print_multilang_result(result)