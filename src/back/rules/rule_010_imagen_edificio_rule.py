from .base_rule import BaseRule, register_rule_class
from typing import Dict

@register_rule_class
class ImagenEdificioRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_imagen = self.parameters.get("xpath_imagen")  # XPath para obtener la imagen

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que la imagen del edificio esté presente y no vacía en el XML.
        """
        validation_result = self._new_result()  # por defecto status="error"

        # Obtener el valor de la imagen desde el XML
        imagen_value = epc.get_value_by_xpath(self.xpath_imagen)

        if imagen_value is None or imagen_value.strip() == "":
            validation_result["message"] = "Debe adjuntarse imagen del edificio."
            validation_result["details"] = {"provided_value": imagen_value if imagen_value is not None else "None"}
            return validation_result

        # Si la imagen está presente
        validation_result["status"] = "success"
        validation_result["message"] = "La imagen del edificio está correctamente adjunta."
        validation_result["details"] = "validated_value: imagen adjunta"
        return validation_result
