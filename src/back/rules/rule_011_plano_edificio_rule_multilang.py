from .base_rule import BaseRule, register_rule_class
from typing import Dict

@register_rule_class
class PlanoEdificioRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_plano = self.parameters.get("xpath_plano")  # XPath para obtener el plano

    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        messages = self.parameters.get("messages", {}).get(key, {})
        return {lang: tpl.format(**kwargs) for lang, tpl in messages.items()}

    def _get_translated_details(self, key: str, **kwargs) -> dict:
        details = self.parameters.get("details", {}).get(key, {})
        return {
            lang: {k: v.format(**kwargs) for k, v in detail.items()}
            for lang, detail in details.items()
        }

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que el plano del edificio esté presente y no vacío en el XML.
        """
        validation_result = self._new_result()  # por defecto status="error"

        # Obtener el valor del plano desde el XML
        plano_value = epc.get_value_by_xpath(self.xpath_plano)

        if plano_value is None or plano_value.strip() == "":
            validation_result["messages"] = self._get_translated_messages("missing")
            validation_result["details"] = self._get_translated_details("missing", value="None" if plano_value is None else "vacía")
            return validation_result

        # Si el plano está presente
        validation_result["status"] = "success"
        validation_result["messages"] = self._get_translated_messages("valid")
        validation_result["details"] = self._get_translated_details("valid", value="Plano Adjunto")
        return validation_result
