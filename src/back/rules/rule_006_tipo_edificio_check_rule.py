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
        validation_result = {
            "status": "error",
            "rule_id": self.id,
            "message": "",
            "description": self.description,
            "details": "",
        }

        # Obtener el valor desde el EPC
        tipo_de_edificio = epc.get_value_by_xpath(self.xpath)

        if tipo_de_edificio is None:
            validation_result["message"] = f"No se encontró valor para el XPath: {self.xpath}"
            return validation_result

        # Validar si el valor está en los valores permitidos
        if tipo_de_edificio not in self.valid_values:
            validation_result["details"] = (
                f"El tipo de edificio '{tipo_de_edificio}' no es válido. "
                f"Valores permitidos: {', '.join(self.valid_values)}."
            )
            validation_result["message"] = f"No concuerda el tipo de edificio indicado con la lista de categorías admitidas:\n -ViviendaUnifamiliar \n -BloqueDeViviendaCompleto \n -ViviendaIndividualEnBloque \n -EdificioUsoTerciario \n -LocalUsoTerciario"
            return validation_result

        # Si pasa todas las validaciones
        validation_result["status"] = "success"
        validation_result["message"] = f"El tipo de edificio '{tipo_de_edificio}' es válido."
        return validation_result
