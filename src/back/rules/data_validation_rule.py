from .base_rule import BaseRule, register_rule_class
from typing import Dict

@register_rule_class
class DataValidationRule(BaseRule):
    def validate(self, epc: "EpcDto") -> Dict:
        # Lógica de validación específica para 'data_validation'
        xpath = self.parameters.get("xpath")
        max_days_difference = self.parameters.get("max_days_difference")
        reference_xpath = self.parameters.get("reference_xpath")
        # Implementación específica aquí...
        return {"status": "success", "rule_id": self.id}
