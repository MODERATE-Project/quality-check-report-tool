import re
from .base_rule import BaseRule, register_rule_class
from typing import Dict

#Regla que comprueba si un campo cumple con una expresión regular

@register_rule_class
class FieldCheckByRegExRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")
        self.regex = self.parameters.get("regex")

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que el valor en el campo especificado por 'xpath' cumple con el formato descrito por la expresión regular.
        """
        # Obtener el valor del campo especificado por XPath
        value_to_validate = epc.get_value_by_xpath(self.xpath)

        if value_to_validate is None:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"No se encontró valor para el XPath: {self.xpath}"
            }

        # Validar el valor utilizando la expresión regular
        if not re.match(self.regex, value_to_validate):
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"El valor '{value_to_validate}' no cumple con el formato."
            }

        # Si pasa la validación
        return {
            "status": "success",
            "rule_id": self.id,
            "message": f"El valor '{value_to_validate}' es válido."
        }
