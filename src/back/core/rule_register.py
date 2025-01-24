import json
import os
from typing import Dict, Type

# Registrar las clases disponibles
class_registry = {}

def register_rule_class(cls):
    """Decorador para registrar clases de reglas."""
    class_registry[cls.__name__] = cls
    return cls

# Cargar esquema general de reglas
def load_rule_schema(schema_path: str) -> Dict:
    with open(schema_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Cargar reglas individuales
def load_rule(rule_path: str) -> Dict:
    with open(rule_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Instanciar una regla a partir de su JSON
def instantiate_rule(rule_data: Dict, rule_schema: Dict) -> "BaseRule":
    rule_type = rule_data["type"]
    class_name = rule_schema["rule_types"][rule_type]["class"]
    rule_class = class_registry.get(class_name)
    if not rule_class:
        raise ValueError(f"No se encontró la clase para el tipo de regla: {rule_type}")
    return rule_class(rule_data)
