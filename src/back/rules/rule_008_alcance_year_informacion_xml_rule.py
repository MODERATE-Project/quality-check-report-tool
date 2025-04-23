from .base_rule import BaseRule, register_rule_class
from typing import Dict, List, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

@register_rule_class
class AlcanceYearInformacionXMLRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")  # XPath para obtener el valor del alcance
        self.xpathAnno = self.parameters.get("xpath_anno", "").strip()  # XPath para obtener el año de construcción
        self.conditions = self.parameters.get("conditions", [])  # Condiciones establecidas en la regla




    def get_question(self, epc) -> Optional[Tuple[str, Dict[str, Dict[str, str]]]]:
        """
        Devuelve la pregunta (si procede) para la regla.

        Si no hace falta preguntar nada, devuelve None.
        """

        logger.debug("get_question  de la regla %s", self.id)

        # ── 1. Datos de entrada ────────────────────────────────────────────────────
        alcance_value = epc.get_value_by_xpath(self.xpath)
        logger.debug("alcance_value: %s", alcance_value)

        try:
            anno_raw = epc.get_value_by_xpath(self.xpathAnno)
            anno_construccion = int(anno_raw)
        except (TypeError, ValueError):
            logger.warning("Año de construcción no válido: %s", anno_raw)
            return None                       # sin año no podemos validar

        # ── 2. Recorremos las condiciones de la regla ─────────────────────────────
        for idx, cond in enumerate(self.conditions):
            logger.debug("condition (%d): %s", idx, cond)

            if alcance_value not in cond.get("values", []):
                continue                      # esta condición no aplica a este alcance

            yr = cond.get("year_range", {})
            min_ok = yr.get("min")           # puede ser None
            max_ok = yr.get("max")

            dentro_del_rango = True
            if min_ok is not None and anno_construccion < int(min_ok):
                dentro_del_rango = False
            if max_ok is not None and anno_construccion > int(max_ok):
                dentro_del_rango = False

            # 2a. Todo encaja ➜ no hay pregunta
            if dentro_del_rango:
                return None

            # 2b. Fuera de rango ➜ construimos la pregunta
            prompt = cond.get("prompt_on_error") or "La información no concuerda, ¿confirmar?"
            question_key = f"{self.id}_{idx}"

            logger.debug("get_question %s la pregunta es: %s", self.id, prompt)

            return (
                self.id,
                {
                    question_key: {
                        "text": prompt,
                        "type": "boolean"
                    }
                }
            )

        # ── 3. No se encontró ninguna condición relevante ─────────────────────────
        logger.debug("get_question %s: no hay pregunta", self.id)
        return None

    # … imports y class AlcanceYearInformacionXMLRule …

    # ──────────────────────────────────────────────────────────────────────
    def validate(self, epc: "EpcDto", questions: Dict = None) -> Dict:
        """
        • Si no llegan 'questions'  →  asumimos que get_question() no vio conflicto,
          y devolvemos success inmediato (versión corta original).
        • Si llegan 'questions'     →  aplicamos la lógica completa
          (rango + respuesta del usuario).
        """
        alcance_value = epc.get_value_by_xpath(self.xpath)
        anno_raw      = epc.get_value_by_xpath(self.xpathAnno)

        # Resultado base
        result = {
            "rule_id":     self.id,
            "status":      "error",
            "message":     "",
            "description": self.description,
            "details":     {},
            "severity":    self.severity
        }

        # Validaciones básicas de existencia y tipo
        if alcance_value is None or anno_raw is None:
            result["message"] = "Faltan datos de alcance o año."
            return result
        try:
            anno_construccion = int(anno_raw)
        except ValueError:
            result["message"] = f"Año no numérico: {anno_raw}"
            return result

        # ────────────────────────────────────────────────────────────────
        #  CASO 1: no se pasa 'questions'  →  versión corta
        # ────────────────────────────────────────────────────────────────
        if questions is None:
            result.update({
                "status":  "success",
                "message": (f"El alcance '{alcance_value}' es compatible con "
                            f"el año {anno_construccion}."),
                "details": {"validated_value": alcance_value,
                            "validated_ano_construccion": anno_construccion}
            })
            return result

        # ────────────────────────────────────────────────────────────────
        #  CASO 2: se reciben respuestas de usuario  →  versión larga
        # ────────────────────────────────────────────────────────────────
        for idx, cond in enumerate(self.conditions):
            if alcance_value not in cond.get("values", []):
                continue

            yr = cond.get("year_range", {})
            min_y = yr.get("min")
            max_y = yr.get("max")

            dentro = ((min_y is None or anno_construccion >= min_y) and
                      (max_y is None or anno_construccion <= max_y))

            if dentro:                      # success directo
                result.update({
                    "status": "success",
                    "message": (f"El alcance '{alcance_value}' es compatible con "
                                f"el año {anno_construccion}."),
                    "details": {"validated_value": alcance_value,
                                "validated_ano_construccion": anno_construccion}
                })
                return result

            # --- fuera de rango → consultar respuesta ---
            answers = (questions.get(self.id) if self.id in questions else questions)
            user_resp = answers.get(str(idx)) if isinstance(answers, dict) else None

            if user_resp is True:          # usuario confirmó actualización (sí)
                result.update({
                    "status":  "success",
                    "message": "Se confirma que se trata de una actualización ya registrada.",
                    "details": {"validated_value": alcance_value,
                                "validated_ano_construccion": anno_construccion}
                })
                return result

            if user_resp is False:         # usuario dijo que NO
                result.update({
                    "status":  "error",
                    "message": ("El alcance indicado no es compatible con el año de "
                                "construcción de la edificación."),
                    "details": {"provided_value": alcance_value,
                                "provided_ano_construccion": anno_construccion,
                                "expected_condition": yr}
                })
                return result

            # Aún no hay respuesta
            result.update({
                "message": "Se requiere confirmación del usuario para validar este alcance.",
                "details": {"provided_value": alcance_value,
                            "provided_ano_construccion": anno_construccion}
            })
            return result

        # El alcance no aparece en ninguna lista de valores
        result["message"] = "El valor de <AlcanceInformacionXML> no está en la lista permitida."
        result["details"] = {"provided_value": alcance_value}
        return result
