from .base_rule import BaseRule, register_rule_class
from typing import Dict, Optional, Tuple

@register_rule_class
class AlcanceYearInformacionXMLRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")
        self.xpathAnno = self.parameters.get("xpath_anno", "").strip()
        self.conditions = self.parameters.get("conditions", [])
        self.messages = self.parameters.get("messages", {})
        self.details = self.parameters.get("details", {})

    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        msgs = self.messages.get(key, {})
        return {lang: tpl.format(**kwargs) for lang, tpl in msgs.items()}

    def _get_translated_details(self, key: str, **kwargs) -> dict:
        dets = self.details.get(key, {})
        return {
            lang: {k: v.format(**kwargs) for k, v in d.items()}
            for lang, d in dets.items()
        }

    def get_question(self, epc) -> Optional[Tuple[str, Dict[str, Dict[str, str]]]]:
        alcance_value = epc.get_value_by_xpath(self.xpath)
        try:
            anno_construccion = int(epc.get_value_by_xpath(self.xpathAnno))
        except (TypeError, ValueError):
            return None

        for idx, cond in enumerate(self.conditions):
            # Aplicamos solo si el valor pertenece a esta condición
            if alcance_value not in cond.get("values", []):
                continue

            yr = cond.get("year_range", {})
            min_y = yr.get("min")
            max_y = yr.get("max")

            dentro = ((min_y is None or anno_construccion >= min_y) and
                    (max_y is None or anno_construccion <= max_y))

            if dentro:
                return None  # Todo correcto

            # Si está fuera del rango, generamos la pregunta
            return (
                self.id,
                {
                    str(idx): {
                        "text": cond.get("prompt_on_error", "¿Confirmas que es una actualización?"),
                        "type": "boolean"
                    }
                }
            )

        # Ninguna condición aplicable
        return None


    def validate(self, epc, questions: Dict = None) -> Dict:
        alcance_value = epc.get_value_by_xpath(self.xpath)
        anno_raw = epc.get_value_by_xpath(self.xpathAnno)
        result = self._new_result()

        if alcance_value is None or anno_raw is None:
            result["status"] = "error"
            result["messages"] = self._get_translated_messages("missing_data")
            result["message"] = result["messages"].get("es", "")
            return result

        try:
            anno_construccion = int(anno_raw)
        except ValueError:
            result["status"] = "error"
            result["messages"] = self._get_translated_messages("invalid_year", raw=anno_raw)
            result["message"] = result["messages"].get("es", "")
            return result

        for idx, cond in enumerate(self.conditions):
            # Evaluamos la condición correspondiente al valor de alcance
            if alcance_value not in cond.get("values", []):
                continue

            yr = cond.get("year_range", {})
            min_y = yr.get("min")
            max_y = yr.get("max")

            dentro = ((min_y is None or anno_construccion >= min_y) and
                    (max_y is None or anno_construccion <= max_y))

            if dentro:
                result["status"] = "success"
                result["messages"] = self._get_translated_messages("valid", value=alcance_value, year=anno_construccion)
                result["message"] = result["messages"].get("es", "")
                result["details"] = self._get_translated_details("valid", value=alcance_value, year=anno_construccion)
                return result

            # Comprobar si hay respuesta del usuario
            answers = questions.get(self.id, questions) if questions else {}
            user_resp = answers.get(str(idx)) if isinstance(answers, dict) else None

            if user_resp is True:
                result["status"] = "success"
                result["messages"] = self._get_translated_messages("confirmed")
                result["message"] = result["messages"].get("es", "")
                result["details"] = self._get_translated_details("confirmed", value=alcance_value, year=anno_construccion)
                return result

            if user_resp is False:
                result["status"] = "error"
                result["messages"] = self._get_translated_messages("incompatible", value=alcance_value, year=anno_construccion)
                result["message"] = result["messages"].get("es", "")
                result["details"] = self._get_translated_details("incompatible", value=alcance_value, year=anno_construccion)
                return result

            result["status"] = "pending"
            result["messages"] = self._get_translated_messages("pending")
            result["message"] = result["messages"].get("es", "")
            result["details"] = self._get_translated_details("pending", value=alcance_value, year=anno_construccion)
            return result

        # Si ninguna condición cubre este valor → error por valor no permitido
        result["status"] = "error"
        result["messages"] = self._get_translated_messages("invalid_value", value=alcance_value)
        result["message"] = result["messages"].get("es", "")
        result["details"] = self._get_translated_details("invalid_value", value=alcance_value)
        return result

