from .base_rule import BaseRule, register_rule_class
from typing import Dict, List


@register_rule_class
class AlcanceYearInformacionXMLRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")
        self.conditions = self.parameters.get("conditions", [])

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida el alcance de la información en combinación con el año de construcción.
        """
        # Obtener el valor de alcance desde el EPC
        alcance_value = epc.get_value_by_xpath(self.xpath)
        if alcance_value is None:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"No se encontró valor para el XPath: {self.xpath}"
            }

        # Obtener el año de construcción desde el EPC
        ano_xpath = "//IdentificacionEdificio/AnoConstruccion"
        ano_construccion = epc.get_value_by_xpath(ano_xpath)
        if ano_construccion is None:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"No se encontró el valor del año de construcción para el XPath: {ano_xpath}"
            }

        # Convertir el año de construcción a entero
        try:
            ano_construccion = int(ano_construccion)
        except ValueError:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"El valor '{ano_construccion}' no es un año válido."
            }

        # Validar las condiciones
        for condition in self.conditions:
            if alcance_value in condition["values"]:
                year_range = condition.get("year_range", {})
                min_year = year_range.get("min", float('-inf'))
                max_year = year_range.get("max", float('inf'))

                if not (min_year <= ano_construccion <= max_year):
                    prompt = condition.get("prompt_on_error")
                    if prompt:
                        return {
                            "status": "warning",
                            "rule_id": self.id,
                            "message": f"{prompt} Alcance: '{alcance_value}', Año de construcción: '{ano_construccion}'."
                        }
                    else:
                        return {
                            "status": "error",
                            "rule_id": self.id,
                            "message": f"El valor de alcance '{alcance_value}' no es válido para el año de construcción '{ano_construccion}'."
                        }

        # Si pasa todas las validaciones
        return {
            "status": "success",
            "rule_id": self.id,
            "message": f"El alcance '{alcance_value}' y el año '{ano_construccion}' son válidos."
        }
