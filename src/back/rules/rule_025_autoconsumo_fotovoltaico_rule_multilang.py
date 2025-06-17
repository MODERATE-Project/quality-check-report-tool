from .base_rule import BaseRule, register_rule_class
from typing import Dict, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

@register_rule_class
class AutoconsumoFotovoltaicoRule(BaseRule):
    def get_question(self, epc) -> Optional[Tuple[str, Dict[str, Dict[str, Any]]]]:
        valor = epc.get_value_by_xpath(self.parameters["xpath_valor"])
        if valor is None or valor.strip() == "":
            return None

        textos = self.parameters.get("question_texts", {})
        return (
            self.id,
            {
                f"{self.id}_num_paneles": {
                    "text": textos.get("num_paneles", "Número de paneles?"),
                    "type": "integer",
                    "optional": True
                },
                f"{self.id}_potencia_w": {
                    "text": textos.get("potencia_panel", "Potencia por panel?"),
                    "type": "integer",
                    "optional": True
                }
            }
        )

    def validate(self, epc, questions: Optional[Dict] = None) -> Dict:
        result = self._new_result(status="success")
        p = self.parameters
        mensajes = p.get("messages", {})
        detalles = p.get("details", {})

        valor_str = epc.get_value_by_xpath(p["xpath_valor"])
        if valor_str is None or valor_str.strip() == "":
            result["status"] = "success"
            result["messages"] = mensajes.get("success", {})
            return result

        try:
            valor_real = float(valor_str)
        except ValueError:
            result["status"] = "error"
            result["messages"] = {"es": "Valor no numérico", "en": "Non-numeric value"}
            return result

        # Respuestas del usuario
        try:
            num_paneles = int(questions.get(f"{self.id}_num_paneles", 0))
            potencia = questions.get(f"{self.id}_potencia_w")
            potencia = int(potencia) if potencia else p["default_potencia_w"]
        except Exception as e:
            result["status"] = "error"
            result["messages"] = {"es": "Respuestas inválidas", "en": "Invalid user input"}
            return result

        max_kwh = (num_paneles * potencia / 1000) * p["horas_estimadas"] * p["factor_margen"]

        if valor_real > max_kwh:
            result["status"] = "suspected"
            result["messages"] = mensajes.get("suspected", {})
            result["details"] = {
                "es": {
                    "valor indicado": valor_real,
                    "máximo estimado": round(max_kwh, 2)
                },
                "en": {
                    "reported value": valor_real,
                    "estimated maximum": round(max_kwh, 2)
                }
            }
        else:
            result["status"] = "success"
            result["messages"] = mensajes.get("success", {})
            result["details"] = {
                "es": {
                    "valor indicado": valor_real,
                    "límite calculado": round(max_kwh, 2)
                },
                "en": {
                    "reported value": valor_real,
                    "calculated limit": round(max_kwh, 2)
                }
            }

        return result
