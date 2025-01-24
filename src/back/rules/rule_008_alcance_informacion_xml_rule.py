from .base_rule import BaseRule, register_rule_class
from typing import Dict


@register_rule_class
class AlcanceInformacionXMLRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")
        self.valid_values = self.parameters.get("valid_values", [])

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que el valor del campo especificado esté en la lista de valores permitidos.
        """
        # Obtener el valor del campo desde el EPC
        alcance_value = epc.get_value_by_xpath(self.xpath)

        if alcance_value is None:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"No se encontró valor para el XPath: {self.xpath}"
            }

        # Validar si el valor está dentro de los valores permitidos
        if alcance_value not in self.valid_values:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"El valor '{alcance_value}' no es válido para el campo '{self.xpath}'. "
                           f"Valores válidos: {', '.join(self.valid_values)}."
            }

        # Si pasa la validación
        return {
            "status": "success",
            "rule_id": self.id,
            "message": f"El valor '{alcance_value}' es válido para el campo '{self.xpath}'."
        }
