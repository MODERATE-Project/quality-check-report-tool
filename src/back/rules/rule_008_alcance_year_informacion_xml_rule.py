from .base_rule import BaseRule, register_rule_class
from typing import Dict, List, Any, Tuple


@register_rule_class
class AlcanceYearInformacionXMLRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")  # XPath para obtener el valor del alcance
        self.xpathAnno = self.parameters.get("xpath_anno", "").strip()  # XPath para obtener el año de construcción
        self.conditions = self.parameters.get("conditions", [])  # Condiciones establecidas en la regla
        self.has_question = "true"


    def get_question(self, epc) -> Tuple[str, Dict[str, str]]:
        """
        Obtiene la pregunta asociada a la regla.
        """


        # Obtener el valor del alcance desde el EPC
        alcance_value = epc.get_value_by_xpath(self.xpath)
        # Obtener el año de construcción
        anno_construccion = epc.get_value_by_xpath(self.xpathAnno)

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
                    return None
                else: #AQUIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII ES DONDE HAY QUE MIRAR LO DE LA PREGUNTA!!!!!!!!!!!!!
                    print ("get_question ", self.id, " la preunta es: ¿Se trata de una actualización de un certificado de eficiencia energética ya registrado?")
                    return {
                                "text": "¿Se trata de una actualización de un certificado de eficiencia energética ya registrado?",
                                "type": "number"
                            }

        print ("get_question ", self.id," no hay pregunta")
        return None



    
    def validate(self, epc: "EpcDto") -> Dict:
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
                else: #AQUIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII ES DONDE HAY QUE MIRAR LO DE LA PREGUNTA!!!!!!!!!!!!!
                    # Manejar el caso de actualización de certificado
                    prompt_on_error = condition.get("prompt_on_error")
                    if prompt_on_error:
                        validation_result["message"] = prompt_on_error
                        validation_result["details"] = {
                            "provided_value": alcance_value,
                            "provided_ano_construccion": anno_construccion,
                            "expected_condition": year_range
                        }
                        return validation_result

                    validation_result["message"] = (
                        "El alcance del certificado indicado no es compatible con el año de construcción de la edificación."
                    )
                    validation_result["details"] = {
                        "provided_value": alcance_value,
                        "provided_ano_construccion": anno_construccion,
                        "expected_condition": year_range
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
