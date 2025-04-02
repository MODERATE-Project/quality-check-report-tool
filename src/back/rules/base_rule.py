from typing import Dict, Type, Any, Tuple
from core.epc_dto import EpcDto

# Diccionario para registrar dinámicamente las clases de reglas
class_registry = {}

def register_rule_class(cls: Type):
    """
    Decorador para registrar dinámicamente clases de reglas basadas en BaseRule.
    """
    class_registry[cls.__name__] = cls
    return cls


@register_rule_class
class BaseRule:
    def __init__(self, rule_data: Dict):
        self.id = rule_data.get("id")
        self.type = rule_data.get("type")
        self.parameters = rule_data.get("parameters", {})
        self.description = rule_data.get("description")
        self.name = rule_data.get("name")
        self.severity = rule_data.get("severity")
        self.need_question = "false"

    def validate(self, epc: "EpcDto") -> Dict:
        raise NotImplementedError("Debe implementarse en subclases.")
    
    def get_question(self,epc) -> Tuple[str, Dict[str , str]]:
         return None