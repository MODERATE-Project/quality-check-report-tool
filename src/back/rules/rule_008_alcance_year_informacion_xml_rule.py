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


    def validate(self, epc: "EpcDto", questions) -> Dict:
        result = {
            "rule_id":  self.id,
            "status":   "error",
            "message":  "",
            "description": self.description,
            "details":  {},
            "severity": self.severity
        }

        # 1) Datos brutos ---------------------------------------------------------
        alcance_value = epc.get_value_by_xpath(self.xpath)
        anno_raw      = epc.get_value_by_xpath(self.xpathAnno)
        if alcance_value is None or anno_raw is None:
            result["message"] = "Faltan datos de alcance o año."
            return result

        try:
            anno_construccion = int(anno_raw)
        except ValueError:
            result["message"] = f"Año no numérico: {anno_raw}"
            return result

        # 2) Recorremos las condiciones ------------------------------------------
        for idx, cond in enumerate(self.conditions):
            if alcance_value not in cond.get("values", []):
                continue                     # esta condición no aplica

            yr = cond.get("year_range", {})
            min_y = int(yr["min"]) if yr.get("min") is not None else None
            max_y = int(yr["max"]) if yr.get("max") is not None else None

            dentro = True
            if min_y is not None and anno_construccion < min_y:
                dentro = False
            if max_y is not None and anno_construccion > max_y:
                dentro = False

            # 2a) Compatible → success
            if dentro:
                result.update({
                    "status": "success",
                    "message": (f"El alcance '{alcance_value}' es compatible con "
                                f"el año {anno_construccion}."),
                    "details": {"validated_value": alcance_value,
                                "validated_ano_construccion": anno_construccion}
                })
                return result

            # 2b) Fuera de rango → comprobar respuesta del usuario
            if questions:
                if self.id in questions and isinstance(questions[self.id], dict):
                    answers = questions[self.id]   # formato A
                else:
                    answers = questions            # formato B
                user_resp = answers.get(str(idx))
            else:
                user_resp = None

            if user_resp is False:        # respondió "No"
                result.update({
                    "status": "error",
                    "message": ("El alcance indicado no es compatible con el año de "
                                "construcción de la edificación."),
                    "details": {"provided_value": alcance_value,
                                "provided_ano_construccion": anno_construccion,
                                "expected_condition": yr}
                })
                return result

            if user_resp is True:         # respondió "Sí"
                result.update({
                    "status": "success",
                    "message": "Se confirma que se trata de una actualización ya registrada.",
                    "details": {"validated_value": alcance_value,
                                "validated_ano_construccion": anno_construccion}
                })
                return result

            # Sin respuesta → error temporal
            result.update({
                "status": "error",
                "message": "Se requiere confirmación del usuario para validar este alcance.",
                "details": {"provided_value": alcance_value,
                            "provided_ano_construccion": anno_construccion}
            })
            return result

        # 3) El alcance no coincide con ninguna lista de valores ------------------
        result["message"] = "El valor de <AlcanceInformacionXML> no está en la lista permitida."
        result["details"] = {"provided_value": alcance_value}
        return result



    
    # def validate(self, epc: "EpcDto", questions) -> Dict:
    #     """
    #     Valida que el valor del campo 'AlcanceInformacionXML' sea uno de los permitidos y que el año de construcción
    #     cumpla con las condiciones de validación establecidas.
    #     """
    #     validation_result = {
    #         "rule_id": self.id,
    #         "status": "error",
    #         "message": "",
    #         "description": self.description,
    #         "details": {},
    #         "severity": self.severity
    #     }

    #     # Obtener el valor del alcance desde el EPC
    #     alcance_value = epc.get_value_by_xpath(self.xpath)
    #     # Obtener el año de construcción
    #     anno_construccion = epc.get_value_by_xpath(self.xpathAnno)

    #     if alcance_value is None:
    #         validation_result["message"] = f"No se encontró valor para el XPath: {self.xpath}"
    #         return validation_result

    #     if anno_construccion is None:
    #         validation_result["message"] = f"No se encontró el año de construcción en el XPath: {self.xpathAnno}"
    #         return validation_result

    #     try:
    #         anno_construccion = int(anno_construccion)
    #     except ValueError:
    #         validation_result["message"] = f"El valor de 'AnoConstruccion' no es un número válido: {anno_construccion}"
    #         validation_result["details"] = {"provided_ano_construccion": anno_construccion}
    #         return validation_result

    #     # Validar si el alcance está en la lista permitida y si cumple con el año correspondiente
    #     for condition in self.conditions:
    #         valid_values = condition.get("values", [])
    #         year_range = condition.get("year_range", {})

    #         # Si el alcance está dentro de los valores permitidos en la condición actual
    #         if alcance_value in valid_values:
    #             min_year = year_range.get("min")
    #             max_year = year_range.get("max")

    #             # Evaluar si el año de construcción está dentro del rango esperado
    #             if (min_year is None or anno_construccion >= min_year) and (max_year is None or anno_construccion <= max_year):
    #                 validation_result["status"] = "success"
    #                 validation_result["message"] = (
    #                     f"El alcance '{alcance_value}' es compatible con el año de construcción '{anno_construccion}'."
    #                 )
    #                 validation_result["details"] = {
    #                     "validated_value": alcance_value,
    #                     "validated_ano_construccion": anno_construccion
    #                 }
    #                 return validation_result
    #             else: 
    #                 # Manejar el caso de actualización de certificado
    #                 # hay que mirar la pregunta que se ha hecho al usuario y si la respuesta es "no" entonces se lanza el error
    #                 # Si la respuesta es "no", se lanza el error
    #                 user_response_key = self.id + "_" + str(self.conditions.index(condition))
    #                 if (questions is not None and self.id + "_" in questions):
    #                     user_response_key = self.id + "_"
    #                     user_response = questions.get(user_response_key, {}).get("response")
    #                     if user_response == "False":
    #                         validation_result["status"] = "error"
    #                         validation_result["message"] = (
    #                             "El alcance del certificado indicado no es compatible con el año de construcción de la edificación."
    #                         )
    #                         validation_result["details"] = {
    #                             "provided_value": alcance_value,
    #                             "provided_ano_construccion": anno_construccion,
    #                             "expected_condition": year_range
    #                         }
    #                         return validation_result
    #                 # Si la respuesta es "si", se devuelve un mensaje de éxito  

    #                 validation_result["status"] = "success"
    #                 validation_result["message"] = (    
    #                     f"El alcance '{alcance_value}' es compatible con el año de construcción '{anno_construccion}'."
    #                 )
    #                 validation_result["details"] = {    
    #                     "validated_value": alcance_value,
    #                     "validated_ano_construccion": anno_construccion
    #                 }
    #                 return validation_result

    #     # Si no se encontró una condición válida
    #     validation_result["message"] = (
    #         f"No concuerda el alcance con la lista de categorías admitidas:\n"
    #         f"- CertificacionExistente\n"
    #         f"- VerificacionExistente\n"
    #         f"- CertificacionVerificacionExistente\n"
    #         f"- CertificacionNuevo\n"
    #         f"- VerificacionNuevo\n"
    #         f"- CertificacionVerificacionNuevo"
    #     )
    #     validation_result["details"] = {
    #         "provided_value": alcance_value
    #     }
    #     return validation_result


    
