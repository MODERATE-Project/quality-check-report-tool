from .base_rule import BaseRule, register_rule_class
import pandas as pd
from typing import Dict, Tuple
from unidecode import unidecode
from core.epc_dto import EpcDto

@register_rule_class
class DataValidationInXlsxRule(BaseRule):
    def __init__(self, rule_data: Dict):

        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")
        self.column_in_source = self.parameters.get("column_in_source")
        self.valid_values_source = self.parameters.get("valid_values_source")
        self.allow_multiple_languages = self.parameters.get("allow_multiple_languages", False)

    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        messages = self.parameters.get("messages", {}).get(key, {})
        return {
            lang: tpl.format(**kwargs) if tpl else ""
            for lang, tpl in messages.items()
        }


    def validate(self, epc: "EpcDto") -> Dict:
        validation_result = self._new_result()  # por defecto status="error"
        value_to_validate = epc.get_value_by_xpath(self.xpath)
        if value_to_validate is None:
            validation_result["messages"] = self._get_translated_messages("missing_value", xpath=self.xpath)
            return validation_result

        normalized_value_to_validate = unidecode(value_to_validate.lower().strip())

        try:
            excel_data = pd.read_excel(self.valid_values_source)
        except Exception as e:
            validation_result["messages"] = self._get_translated_messages("excel_error", filename=self.valid_values_source, error=str(e))
            return validation_result

        if self.column_in_source not in excel_data.columns:
            validation_result["messages"] = self._get_translated_messages("column_missing", column=self.column_in_source)
            return validation_result

        valid_values = excel_data[self.column_in_source].astype(str).tolist()
        valor_encontrado = False
        for val in valid_values:
            posibles_valores = [unidecode(x.lower().strip()) for x in val.split("/")]
            if normalized_value_to_validate in posibles_valores:
                valor_encontrado = True
                break

        if not valor_encontrado:
            validation_result["status"] = "error"
            validation_result["details"] = {
                "reason": "value_not_found",
                "input": value_to_validate,
                "column": self.column_in_source
            }
            validation_result["messages"] = self._get_translated_messages("not_found", value=value_to_validate)
            return validation_result

        validation_result["status"] = "success"
        validation_result["messages"] = self._get_translated_messages("valid", value=value_to_validate)
        return validation_result
