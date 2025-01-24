from .base_rule import BaseRule, register_rule_class
from typing import Dict

@register_rule_class
class FieldMatchingRule(BaseRule):
    def validate(self, epc: "EpcDto") -> Dict:
        # Implementación específica
        return {"status": "success", "rule_id": self.id}

        
