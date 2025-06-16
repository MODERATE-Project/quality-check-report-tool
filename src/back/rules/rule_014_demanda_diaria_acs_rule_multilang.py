from typing import Dict, Tuple, Optional, Any
from core.epc_dto import EpcDto
from .base_rule import BaseRule, register_rule_class
import logging

logger = logging.getLogger(__name__)

# Tabla fija de demanda esperada por número de dormitorios
DEMANDA_POR_DORMITORIOS = {
    "1": 42, "2": 84, "3": 112, "4": 140, "5": 168, "6": 196, "6+": 196
}

@register_rule_class
class DemandaDiariaACSRule(BaseRule):

    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        messages = self.parameters.get("messages", {}).get(key, {})
        return {lang: tpl.format(**kwargs) for lang, tpl in messages.items()}

    def _get_translated_details(self, key: str, **kwargs) -> dict:
        details_tpl = self.parameters.get("details", {}).get(key, {})
        return {
            lang: {k: v.format(**kwargs) for k, v in detail.items()}
            for lang, detail in details_tpl.items()
        }

    def get_question(self, epc: EpcDto) -> Optional[Tuple[str, Dict[str, Dict[str, Any]]]]:
        tipo = epc.get_value_by_xpath(self.parameters["xpath_tipo_edificio"])
        if tipo not in self.parameters.get("values", []):
            return None

        pregunta = self.parameters.get("questions", {}).get("numero_dormitorios", {})
        return (
            self.id,
            {
                f"{self.id}_0": {
                    "text": pregunta,
                    "type": "integer"
                }
            }
        )

    def validate(self, epc: EpcDto, questions={}) -> Dict:
        result = self._new_result()
        tipo = epc.get_value_by_xpath(self.parameters["xpath_tipo_edificio"])
        demanda_str = epc.get_value_by_xpath(self.parameters["DemandaDiariaACS"])

        if tipo not in self.parameters.get("values", []):
            result["status"] = "success"
            return result

        if not demanda_str:
            result["messages"] = self._get_translated_messages("missing_field")
            return result

        try:
            real = float(demanda_str)
        except ValueError:
            result["messages"] = self._get_translated_messages("not_numeric", value=demanda_str)
            return result

        if "0" not in questions:
            result["messages"] = self._get_translated_messages("missing_answer")
            return result

        try:
            dormitorios = int(questions["0"])
        except ValueError:
            result["messages"] = self._get_translated_messages("invalid_input")
            return result

        key = "6+" if dormitorios >= 6 else str(dormitorios)
        esperada = DEMANDA_POR_DORMITORIOS.get(key, 42.0)
        margen = 0.10

        if not (esperada * (1 - margen) <= real <= esperada * (1 + margen)):
            result["messages"] = self._get_translated_messages("invalid", real=real, expected=esperada)
            result["details"] = self._get_translated_details("invalid", real=real, expected=esperada)
            return result

        result["status"] = "success"
        result["messages"] = self._get_translated_messages("valid", real=real)
        result["details"] = self._get_translated_details("valid", real=real)
        return result
