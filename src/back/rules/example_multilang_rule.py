from .base_rule import BaseRule, register_rule_class
from typing import Dict

@register_rule_class
class ExampleMultilangRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")

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
        result = self._new_result()
        value = epc.get_value_by_xpath(self.xpath)

        if value is None:
            result["messages"] = self._get_translated_messages("missing_value", xpath=self.xpath)
            return result

        if value != "EXPECTED":
            result["status"] = "error"
            result["messages"] = self._get_translated_messages("invalid", value=value)
            result["details"] = self._get_translated_details("invalid", value=value, expected="EXPECTED")
            return result

        result["status"] = "success"
        result["messages"] = self._get_translated_messages("valid", value=value)
        result["details"] = self._get_translated_details("valid", value=value)
        return result