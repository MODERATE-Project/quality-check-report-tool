from .base_rule import BaseRule, register_rule_class
from typing import Dict
import logging

logger = logging.getLogger(__name__)

@register_rule_class
class RendimientosGeneradoresRefrigeracionRule(BaseRule):
    def validate(self, epc, questions=None) -> Dict:
        result = self._new_result()
        p = self.parameters
        mensajes = p.get("messages", {})
        detalles = p.get("details", {})

        nodos = epc.get_nodes_by_xpath(p["xpath_generadores"])
        if not nodos:
            result["messages"] = mensajes.get("missing_data", {})
            return result

        nominal_errors = []
        estacional_errors = []
        resumen_generadores = []

        for idx, gen in enumerate(nodos):
            vector = gen.find(p["vector_tag"])
            if vector is None or not vector.text:
                continue

            vector_text = vector.text.strip()
            resumen_generadores.append(vector_text)

            # RENDIMIENTO NOMINAL
            r_nominal = gen.find(p["rendimiento_nominal_tag"])
            if r_nominal is not None and r_nominal.text != p["valor_excluido"]:
                try:
                    val_nom = float(r_nominal.text)
                    if vector_text in p["limites_nominal"]:
                        lim_inf, lim_sup = p["limites_nominal"][vector_text]
                        if not (lim_inf <= val_nom <= lim_sup):
                            nominal_errors.append((idx + 1, val_nom, vector_text))
                except ValueError:
                    nominal_errors.append((idx + 1, r_nominal.text, vector_text))

            # RENDIMIENTO ESTACIONAL
            r_estacional = gen.find(p["rendimiento_estacional_tag"])
            if r_estacional is not None and r_estacional.text != p["valor_excluido"]:
                try:
                    val_est = float(r_estacional.text)
                    if vector_text in p["limites_estacional"]:
                        lim_inf, lim_sup = p["limites_estacional"][vector_text]
                        if not (lim_inf <= val_est <= lim_sup):
                            estacional_errors.append((idx + 1, val_est, vector_text))
                except ValueError:
                    estacional_errors.append((idx + 1, r_estacional.text, vector_text))

        if nominal_errors:
            result.update({
                "status": "error",
                "messages": mensajes.get("error_nominal", {}),
                "details": {
                    "es": {
                        "generadores con error": nominal_errors,
                        "límites nominales usados": p["limites_nominal"]
                    },
                    "en": {
                        "generators with error": nominal_errors,
                        "nominal limits used": p["limites_nominal"]
                    }
                }
            })
            return result

        if estacional_errors:
            result.update({
                "status": "error",
                "messages": mensajes.get("error_estacional", {}),
                "details": {
                    "es": {
                        "generadores con error": estacional_errors,
                        "límites estacionales usados": p["limites_estacional"]
                    },
                    "en": {
                        "generators with error": estacional_errors,
                        "seasonal limits used": p["limites_estacional"]
                    }
                }
            })
            return result

        result.update({
            "status": "success",
            "messages": mensajes.get("success", {}),
            "details": {
                "es": {
                    "generadores validados": resumen_generadores
                },
                "en": {
                    "validated generators": resumen_generadores
                }
            }
        })
        return result
