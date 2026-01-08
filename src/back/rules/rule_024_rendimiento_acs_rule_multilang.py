from .base_rule import BaseRule, register_rule_class
from typing import Dict
import logging

logger = logging.getLogger(__name__)

@register_rule_class
class RendimientoACSRule(BaseRule):
    def validate(self, epc, questions=None) -> Dict:
        result = self._new_result()
        p = self.parameters
        mensajes = p.get("messages", {})
        detalles = p.get("details", {})

        nodos = epc.get_nodes_by_xpath(p["xpath_generadores"])
        if not nodos:
            result["messages"] = mensajes.get("missing_data", {})
            return result

        errores_nominales = []
        errores_estacionales = []
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
                            errores_nominales.append((idx + 1, val_nom, vector_text))
                except ValueError:
                    errores_nominales.append((idx + 1, r_nominal.text, vector_text))
            
            # RENDIMIENTO ESTACIONAL (si está configurado)
            if "rendimiento_estacional_tag" in p and "limites_estacional" in p:
                r_estacional = gen.find(p.get("rendimiento_estacional_tag"))
                if r_estacional is not None and r_estacional.text != p["valor_excluido"]:
                    try:
                        val_est = float(r_estacional.text)
                        if vector_text in p["limites_estacional"]:
                            lim_inf, lim_sup = p["limites_estacional"][vector_text]
                            if not (lim_inf <= val_est <= lim_sup):
                                errores_estacionales.append((idx + 1, val_est, vector_text))
                    except ValueError:
                        errores_estacionales.append((idx + 1, r_estacional.text, vector_text))

        if errores_nominales:
            result.update({
                "status": "error",
                "messages": mensajes.get("error_nominal", {}),
                "details": {
                    "es": {
                        "generadores con error": errores_nominales,
                        "límites nominales usados": p["limites_nominal"]
                    },
                    "en": {
                        "generators with error": errores_nominales,
                        "nominal limits used": p["limites_nominal"]
                    }
                }
            })
            return result

        if errores_estacionales:
            result.update({
                "status": "error",
                "messages": mensajes.get("error_estacional", {}),
                "details": {
                    "es": {
                        "generadores con error": errores_estacionales,
                        "límites estacionales usados": p.get("limites_estacional", {})
                    },
                    "en": {
                        "generators with error": errores_estacionales,
                        "seasonal limits used": p.get("limites_estacional", {})
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
