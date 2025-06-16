from .base_rule import BaseRule, register_rule_class
from typing import Dict
import logging

logger = logging.getLogger(__name__)

@register_rule_class
class FactorSolarHuecosRule(BaseRule):
    def validate(self, epc, questions=None) -> Dict:
        result = self._new_result()
        params = self.parameters
        mensajes = params.get("messages", {})
        detalles = params.get("details", {})
        intervalos = params.get("intervalos", [])

        anno_raw = epc.get_value_by_xpath(params["xpath_anno"])
        valores_f = epc.get_values_by_xpath(params["xpath_factores"])

        try:
            anno = int(anno_raw)
        except (TypeError, ValueError):
            result["messages"] = mensajes.get("invalid_anno", {})
            return result

        if not valores_f:
            result["messages"] = mensajes.get("missing_factores", {})
            return result

        intervalo = next((
            r for r in intervalos
            if (r["min_year"] is None or anno >= r["min_year"]) and
               (r["max_year"] is None or anno <= r["max_year"])
        ), None)

        if not intervalo:
            result["messages"] = mensajes.get("no_interval", {})
            return result

        errores = []
        for idx, val in enumerate(valores_f):
            try:
                f_val = float(val)
                if not (intervalo["min_f"] <= f_val <= intervalo["max_f"]):
                    errores.append((idx + 1, f_val))
            except ValueError:
                errores.append((idx + 1, val))

        if errores:
            result.update({
                "status": "error",
                "messages": mensajes.get("error_values", {}),
                "details": {
                    "es": {
                        "año de construcción": anno,
                        "valores fuera de rango": errores,
                        "límites permitidos": intervalo
                    },
                    "en": {
                        "construction year": anno,
                        "out-of-range values": errores,
                        "allowed limits": intervalo
                    }
                }
            })
        else:
            result.update({
                "status": "success",
                "messages": mensajes.get("success", {}),
                "details": {
                    "es": {
                        "año de construcción": anno,
                        "valores validados": valores_f
                    },
                    "en": {
                        "construction year": anno,
                        "validated values": valores_f
                    }
                }
            })

        return result
