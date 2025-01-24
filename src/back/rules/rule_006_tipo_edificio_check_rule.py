from .base_rule import BaseRule, register_rule_class
from typing import Dict


@register_rule_class
class TipoDeEdificioCheckRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")
        self.valid_values = self.parameters.get("valid_values", [])

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que el valor en el campo 'TipoDeEdificio' esté dentro de los valores permitidos.
        """
        # Obtener el valor desde el EPC
        tipo_de_edificio = epc.get_value_by_xpath(self.xpath)

        if tipo_de_edificio is None:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"No se encontró valor para el XPath: {self.xpath}"
            }

        # Validar si el valor está en los valores permitidos
        if tipo_de_edificio not in self.valid_values:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"El tipo de edificio '{tipo_de_edificio}' no es válido. Valores permitidos: {self.valid_values}."
            }

        # Si pasa todas las validaciones
        return {
            "status": "success",
            "rule_id": self.id,
            "message": f"El tipo de edificio '{tipo_de_edificio}' es válido."
        }
