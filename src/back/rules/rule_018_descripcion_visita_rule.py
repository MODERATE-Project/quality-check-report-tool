from .base_rule import BaseRule, register_rule_class
from core.epc_dto import EpcDto
from typing import Dict

@register_rule_class
class DescripcionVisitaRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")

    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        mensajes = self.parameters.get("messages", {}).get(key, {})
        return {lang: tpl.format(**kwargs) for lang, tpl in mensajes.items()}

    def _get_translated_details(self, key: str, **kwargs) -> dict:
        detalles = self.parameters.get("details", {}).get(key, {})
        return {
            lang: {k: v.format(**kwargs) for k, v in detalle.items()}
            for lang, detalle in detalles.items()
        }

    def validate(self, epc: EpcDto) -> Dict:
        result = self._new_result()
        valor = epc.get_value_by_xpath(self.xpath)

        if not valor or not valor.strip():
            result["status"] = "error"
            result["messages"] = self._get_translated_messages("empty")
            result["message"] = result["messages"].get("es", "")
            result["details"] = self._get_translated_details("empty")
            return result

        result["status"] = "success"
        result["messages"] = self._get_translated_messages("valid")
        result["message"] = result["messages"].get("es", "")
        result["details"] = self._get_translated_details("valid")
        return result
