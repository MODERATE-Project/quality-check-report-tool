from .base_rule import BaseRule, register_rule_class
from typing import Dict

@register_rule_class
class ImagenEdificioRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_imagen = self.parameters.get("xpath_imagen")  # XPath para obtener la imagen

    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        messages = self.parameters.get("messages", {}).get(key, {})
        return {lang: tpl.format(**kwargs) for lang, tpl in messages.items()}

    def _get_translated_details(self, key: str, **kwargs) -> dict:
        template = self.parameters.get("details", {}).get(key, {})
        return {
            lang: {k: v.format(**kwargs) for k, v in detail.items()}
            for lang, detail in template.items()
        }

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que la imagen del edificio esté presente y no vacía en el XML.
        """
        validation_result = self._new_result()  # por defecto status="error"

        # Obtener el valor de la imagen desde el XML
        imagen_value = epc.get_value_by_xpath(self.xpath_imagen)

        if imagen_value is None or imagen_value.strip() == "":
            validation_result["messages"] = self._get_translated_messages("missing")
            validation_result["message"] = validation_result["messages"].get("es", "")
            validation_result["details"] = self._get_translated_details("missing", value="None" if imagen_value is None else "vacía")
            return validation_result

        # Si la imagen está presente
        validation_result["status"] = "success"
        validation_result["messages"] = self._get_translated_messages("valid")
        validation_result["message"] = validation_result["messages"].get("es", "")
        validation_result["details"] = self._get_translated_details("valid", value="imagen adjunta")
        return validation_result
