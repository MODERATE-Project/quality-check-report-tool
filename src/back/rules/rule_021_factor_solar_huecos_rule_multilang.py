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
        factorSolar_field = params["field"]

        anno_raw = epc.get_value_by_xpath(params["xpath_anno"])
        valores_f = epc.get_nodes_by_xpath(params["xpath_factores"])

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
        for idx, e in enumerate(valores_f):
            tipo = e.findtext("Tipo")
            nombre = e.findtext("Nombre")
            try:
                u_val = float(e.findtext(factorSolar_field))
                info = {"nombre": nombre, "tipo": tipo, "valor": u_val}
                if not (intervalo["min_u"] <= u_val <= intervalo["max_u"]):
                    errores.append(info)
            except:
                errores.append({
                    "nombre": nombre,
                    "tipo": tipo,
                    "valor": e.findtext(factorSolar_field)
                })

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
