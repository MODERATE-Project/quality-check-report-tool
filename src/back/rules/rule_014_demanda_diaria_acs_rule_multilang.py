from typing import Dict, Tuple, Optional, Any
from core.epc_dto import EpcDto
from .base_rule import BaseRule, register_rule_class
import logging

logger = logging.getLogger(__name__)

DEMANDA_POR_DORMITORIOS = {
    "1": 42, "2": 84, "3": 112, "4": 140, "5": 168, "6": 196, "6+": 196
}

FACTOR_DESCENTRALIZACION = {
    "3": 1.00, "10": 0.95, "20": 0.90, "50": 0.85, "75": 0.80, "100": 0.75, "101": 0.70
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
        building_type = epc.get_value_by_xpath(self.parameters["xpath_tipo_edificio"])
        valid_types = self.parameters.get("values", [])

        if building_type not in valid_types:
            return None

        question = (
            "¿Cuántas viviendas hay en el bloque?" if building_type == "BloqueDeViviendaCompleto"
            else "¿Cuántos dormitorios tiene la vivienda?"
        )

        return (self.id, {
            f"{self.id}_0": {
                "text": question,
                "type": "integer"
            }
        })

    def validate(self, epc: EpcDto, questions) -> Dict:
        result = self._new_result()
        building_type = epc.get_value_by_xpath(self.parameters["xpath_tipo_edificio"])
        demanda_acs_str = epc.get_value_by_xpath(self.parameters["DemandaDiariaACS"])

        if not demanda_acs_str:
            result["messages"] = self._get_translated_messages("missing_field")
            return result

        try:
            demanda_acs_real = float(demanda_acs_str)
        except ValueError:
            result["messages"] = self._get_translated_messages("not_numeric", value=demanda_acs_str)
            return result

        if "0" not in questions:
            result["messages"] = self._get_translated_messages("missing_answer")
            return result

        try:
            user_value = int(questions["0"])
        except ValueError:
            result["messages"] = self._get_translated_messages("invalid_input")
            return result

        if building_type == "BloqueDeViviendaCompleto":
            base = 42.0
            demanda_base = base * user_value
            factor = self._obtener_factor_descentralizacion(user_value)
            demanda_esperada = demanda_base * factor
        else:
            key = "6+" if user_value >= 6 else str(user_value)
            demanda_esperada = DEMANDA_POR_DORMITORIOS.get(key, 42.0)

        margen = 0.10
        if not (demanda_esperada * (1 - margen) <= demanda_acs_real <= demanda_esperada * (1 + margen)):
            result["messages"] = self._get_translated_messages(
                "invalid", real=demanda_acs_real, expected=demanda_esperada
            )
            result["details"] = self._get_translated_details(
                "invalid", real=demanda_acs_real, expected=demanda_esperada
            )
            return result

        result["status"] = "success"
        result["messages"] = self._get_translated_messages("valid", real=demanda_acs_real)
        result["details"] = self._get_translated_details("valid", real=demanda_acs_real)
        return result

    def _obtener_factor_descentralizacion(self, num_viviendas: int) -> float:
        thresholds = sorted(int(k) for k in FACTOR_DESCENTRALIZACION.keys())
        for th in thresholds:
            if num_viviendas <= th:
                return FACTOR_DESCENTRALIZACION[str(th)]
        return FACTOR_DESCENTRALIZACION["101"]
