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

    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        messages = self.parameters.get("messages", {}).get(key, {})
        return {lang: tpl.format(**kwargs) for lang, tpl in messages.items()}

    def _get_translated_details(self, key: str, **kwargs) -> dict:
        details = self.parameters.get("details", {}).get(key, {})
        return {
            lang: {k: v.format(**kwargs) for k, v in detail.items()}
            for lang, detail in details.items()
        }

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
        result = self._new_result()  # por defecto status="error"

        # Validaciones básicas de existencia y tipo
        if alcance_value is None or anno_raw is None:
            result["messages"] = self._get_translated_messages("missing_fields")
            result["message"] = result["messages"].get("es", "")
            return result
        try:
            anno_construccion = int(anno_raw)
        except ValueError:
            result["messages"] = self._get_translated_messages("invalid_year", year=anno_raw)
            result["message"] = result["messages"].get("es", "")
            return result

        # ────────────────────────────────────────────────────────────────
        #  CASO 1: no se pasa 'questions'  →  versión corta
        # ────────────────────────────────────────────────────────────────
        if questions is None:
            result.update({
                "status":  "success",
                "messages": self._get_translated_messages("valid", alcance=alcance_value, ano=anno_construccion),
                "message": self._get_translated_messages("valid", alcance=alcance_value, ano=anno_construccion).get("es", ""),
                "details": self._get_translated_details("valid", alcance=alcance_value, ano=anno_construccion)
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
                    "messages": self._get_translated_messages("valid", alcance=alcance_value, ano=anno_construccion),
                    "message": self._get_translated_messages("valid", alcance=alcance_value, ano=anno_construccion).get("es", ""),
                    "details": self._get_translated_details("valid", alcance=alcance_value, ano=anno_construccion)
                })
                return result

            # --- fuera de rango → consultar respuesta ---
            answers = (questions.get(self.id) if self.id in questions else questions)
            user_resp = answers.get(str(idx)) if isinstance(answers, dict) else None

            if user_resp is True:          # usuario confirmó actualización (sí)
                result.update({
                    "status":  "success",
                    "messages": self._get_translated_messages("confirmed"),
                    "message": self._get_translated_messages("confirmed").get("es", ""),
                    "details": self._get_translated_details("confirmed")
                })
                return result

            if user_resp is False:         # usuario dijo que NO
                result.update({
                    "status":  "error",
                    "messages": self._get_translated_messages("incompatible", alcance=alcance_value),
                    "message": self._get_translated_messages("incompatible", alcance=alcance_value).get("es", ""),
                    "details": self._get_translated_details("incompatible", alcance=alcance_value, ano=anno_construccion, expected=yr)
                })
                return result

            # Aún no hay respuesta
            result.update({
                "messages": self._get_translated_messages("needs_confirmation"),
                "message": self._get_translated_messages("needs_confirmation").get("es", ""),
                "details": self._get_translated_details("needs_confirmation", alcance=alcance_value, ano=anno_construccion)
            })
            return result

        # El alcance no aparece en ninguna lista de valores
        result["messages"] = self._get_translated_messages("not_in_list", alcance=alcance_value)
        result["message"] = result["messages"].get("es", "")
        result["details"] = self._get_translated_details("not_in_list", alcance=alcance_value)
        return result
