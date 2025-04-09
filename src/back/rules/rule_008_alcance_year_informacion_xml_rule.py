from .base_rule import BaseRule, register_rule_class
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

@register_rule_class
class AlcanceYearInformacionXMLRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")  # XPath para obtener el valor del alcance
        self.xpathAnno = self.parameters.get("xpath_anno", "").strip()  # XPath para obtener el año de construcción
        self.conditions = self.parameters.get("conditions", [])  # Condiciones establecidas en la regla


    def get_question(self, epc) -> Tuple[str, Dict[str, str]]:
        """
        Obtiene la pregunta asociada a la regla.
        """
        logger.debug("get_question  de la regla 008")

        # Obtener el valor del alcance desde el EPC
        alcance_value = epc.get_value_by_xpath(self.xpath)
        logger.debug("alcance_value: %s", alcance_value)
        # Obtener el año de construcción
        anno_construccion = int(epc.get_value_by_xpath(self.xpathAnno))
        logger.debug("(self.xpathAnno): %s", self.xpathAnno)

        # Validar si el alcance está en la lista permitida y si cumple con el año correspondiente
        for i, condition in enumerate(self.conditions):
            logger.debug("condition: %s", condition)
            valid_values = condition.get("values", [])
            year_range = condition.get("year_range", {})

            # Si el alcance está dentro de los valores permitidos en la condición actual
            if alcance_value in valid_values:
                min_year_str = year_range.get("min")
                min_year = int(min_year_str) if min_year_str is not None else None

                max_year_str = year_range.get("max")
                max_year = int(max_year_str) if max_year_str is not None else None
                
                # Evaluar si el año de construcción está dentro del rango esperado
                if (min_year is None or anno_construccion >= min_year) and (max_year is None or anno_construccion <= max_year):
                    return None
                else: #AQUIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII ES DONDE HAY QUE MIRAR LO DE LA PREGUNTA!!!!!!!!!!!!!
                    logger.debug(f"get_question {self.id} la pregunta es: ¿Se trata de una actualización de un certificado de eficiencia energética ya registrado?")
                    return self.id, {self.id + "_" + str(i): {
                                         "text": "¿Se trata de una actualización de un certificado de eficiencia energética ya registrado?",
                                         "type": "boolean"
                                    }}

        print ("get_question ", self.id," no hay pregunta")
        return None



    
    def validate(self, epc: "EpcDto", questions) -> Dict:
        """
        Valida que el valor del campo 'AlcanceInformacionXML' sea uno de los permitidos y que el año de construcción
        cumpla con las condiciones de validación establecidas.
        """
        validation_result = {
            "rule_id": self.id,
            "status": "error",
            "message": "",
            "description": self.description,
            "details": {},
            "severity": self.severity
        }

        # Obtener el valor del alcance desde el EPC
        alcance_value = epc.get_value_by_xpath(self.xpath)
        # Obtener el año de construcción
        anno_construccion = epc.get_value_by_xpath(self.xpathAnno)

        if alcance_value is None:
            validation_result["message"] = f"No se encontró valor para el XPath: {self.xpath}"
            return validation_result

        if anno_construccion is None:
            validation_result["message"] = f"No se encontró el año de construcción en el XPath: {self.xpathAnno}"
            return validation_result

        try:
            anno_construccion = int(anno_construccion)
        except ValueError:
            validation_result["message"] = f"El valor de 'AnoConstruccion' no es un número válido: {anno_construccion}"
            validation_result["details"] = {"provided_ano_construccion": anno_construccion}
            return validation_result

        # Validar si el alcance está en la lista permitida y si cumple con el año correspondiente
        for condition in self.conditions:
            valid_values = condition.get("values", [])
            year_range = condition.get("year_range", {})

            # Si el alcance está dentro de los valores permitidos en la condición actual
            if alcance_value in valid_values:
                min_year = year_range.get("min")
                max_year = year_range.get("max")

                # Evaluar si el año de construcción está dentro del rango esperado
                if (min_year is None or anno_construccion >= min_year) and (max_year is None or anno_construccion <= max_year):
                    validation_result["status"] = "success"
                    validation_result["message"] = (
                        f"El alcance '{alcance_value}' es compatible con el año de construcción '{anno_construccion}'."
                    )
                    validation_result["details"] = {
                        "validated_value": alcance_value,
                        "validated_ano_construccion": anno_construccion
                    }
                    return validation_result
                else: 
                    # Manejar el caso de actualización de certificado
                    # hay que mirar la pregunta que se ha hecho al usuario y si la respuesta es "no" entonces se lanza el error
                    # Si la respuesta es "no", se lanza el error
                    user_response_key = self.id + "_" + str(self.conditions.index(condition))
                    if (questions is not None and self.id + "_" in questions):
                        user_response_key = self.id + "_"
                        user_response = questions.get(user_response_key, {}).get("response")
                        if user_response == "False":
                            validation_result["status"] = "error"
                            validation_result["message"] = (
                                "El alcance del certificado indicado no es compatible con el año de construcción de la edificación."
                            )
                            validation_result["details"] = {
                                "provided_value": alcance_value,
                                "provided_ano_construccion": anno_construccion,
                                "expected_condition": year_range
                            }
                            return validation_result
                    # Si la respuesta es "si", se devuelve un mensaje de éxito  

                    validation_result["status"] = "success"
                    validation_result["message"] = (    
                        f"El alcance '{alcance_value}' es compatible con el año de construcción '{anno_construccion}'."
                    )
                    validation_result["details"] = {    
                        "validated_value": alcance_value,
                        "validated_ano_construccion": anno_construccion
                    }
                    return validation_result

        # Si no se encontró una condición válida
        validation_result["message"] = (
            f"No concuerda el alcance con la lista de categorías admitidas:\n"
            f"- CertificacionExistente\n"
            f"- VerificacionExistente\n"
            f"- CertificacionVerificacionExistente\n"
            f"- CertificacionNuevo\n"
            f"- VerificacionNuevo\n"
            f"- CertificacionVerificacionNuevo"
        )
        validation_result["details"] = {
            "provided_value": alcance_value
        }
        return validation_result
