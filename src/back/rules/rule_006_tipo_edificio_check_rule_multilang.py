from .base_rule import BaseRule, register_rule_class
from typing import Dict


@register_rule_class
class TipoDeEdificioCheckRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")
        self.valid_values = self.parameters.get("valid_values", [])


    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        messages = self.parameters.get("messages", {}).get(key, {})
        return {
            lang: tpl.format(**kwargs) if tpl else ""
            for lang, tpl in messages.items()
        }

    def _get_translated_details(self, key: str, **kwargs) -> dict:
        details_template = self.parameters.get("details", {}).get(key, {})
        return {
            lang: {
                k: v.format(**kwargs) if isinstance(v, str) else v
                for k, v in detail.items()
            }
            for lang, detail in details_template.items()
        }

    def validate(self, epc: "EpcDto") -> Dict:

        """
        Valida que el valor en el campo 'TipoDeEdificio' esté dentro de los valores permitidos.
        """
        validation_result = self._new_result()  # por defecto status="error"

        # Obtener el valor desde el EPC
        tipo_de_edificio = epc.get_value_by_xpath(self.xpath)

        if tipo_de_edificio is None:
            validation_result["messages"] = self._get_translated_messages("missing_value", xpath=self.xpath)
            validation_result["message"] = validation_result["messages"].get("es", "")
            return validation_result

        # Validar si el valor está en los valores permitidos
        if tipo_de_edificio not in self.valid_values:
            validation_result["details"] = self._get_translated_details("invalid", tipo=tipo_de_edificio, validos=", ".join(self.valid_values))
            validation_result["messages"] = self._get_translated_messages("invalid", tipo=tipo_de_edificio)
            validation_result["message"] = validation_result["messages"].get("es", "")
            return validation_result

        # Si pasa todas las validaciones
        validation_result["status"] = "success"
        validation_result["messages"] = self._get_translated_messages("valid", tipo=tipo_de_edificio)
        validation_result["message"] = validation_result["messages"].get("es", "")
        return validation_result
