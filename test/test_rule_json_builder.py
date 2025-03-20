
import json
import os.path, sys
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/back'))
sys.path.insert(0, path)
from core.rule_json_builder import RuleJsonBuilder


builder = RuleJsonBuilder(
    rule_directory="rules_json",
    base_file="rules_base.json",
    cache_file="rules_cache.json"
)
# Construir las reglas (usará el caché si no hay cambios)
rules = builder.build_rules()

# Mostrar las reglas ensambladas
print(json.dumps(rules, indent=4, ensure_ascii=False))