from .base_rule import BaseRule, register_rule_class
from typing import Dict

@register_rule_class
class PlanoEdificioRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_plano = self.parameters.get("xpath_plano")  # XPath para obtener el plano

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que el plano del edificio esté presente y no vacío en el XML.
        """
        validation_result = {
            "rule_id": self.id,
            "status": "error",
            "message": "",
            "description": self.description,
            "details": {}
        }

        # Obtener el valor del plano desde el XML
        plano_value = epc.get_value_by_xpath(self.xpath_plano)

        if plano_value is None or plano_value.strip() == "":
            validation_result["message"] = "Debe adjuntarse plano del edificio."
            validation_result["details"] = {"provided_value": plano_value if plano_value is not None else "None"}
            return validation_result

        # Si el plano está presente
        validation_result["status"] = "success"
        validation_result["message"] = "El plano del edificio está correctamente adjunto."
        validation_result["details"] = {"validated_value": "Plano Adjunto"}
        return validation_result
