import re
from .base_rule import BaseRule, register_rule_class
from typing import Dict

# Regla que comprueba si un campo cumple con una expresión regular

@register_rule_class
class FieldCheckByRegExRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")
        self.regex = self.parameters.get("regex")
        
    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        messages = self.parameters.get("messages", {}).get(key, {})
        return {
            lang: tpl.format(**kwargs) if tpl else ""
            for lang, tpl in messages.items()
        }


    def validate(self, epc: "EpcDto") -> Dict:
        validation_result = self._new_result()

        value_to_validate = epc.get_value_by_xpath(self.xpath)

        if value_to_validate is None:
            validation_result["messages"] = self._get_translated_messages("missing_value", xpath=self.xpath)
            validation_result["message"] = validation_result["messages"].get("es", "")
            return validation_result

        if not re.match(self.regex, value_to_validate):
            validation_result["messages"] = self._get_translated_messages("invalid_format", value=value_to_validate)
            validation_result["message"] = validation_result["messages"].get("es", "")
            return validation_result

        validation_result["status"] = "success"
        validation_result["messages"] = self._get_translated_messages("valid", value=value_to_validate)
        validation_result["message"] = validation_result["messages"].get("es", "")
        return validation_result


