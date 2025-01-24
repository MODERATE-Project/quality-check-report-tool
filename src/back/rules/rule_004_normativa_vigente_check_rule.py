from .base_rule import BaseRule, register_rule_class
from typing import Dict


@register_rule_class
class NormativaVigenteCheckRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")
        self.conditions = self.parameters.get("conditions", [])

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que el valor en el campo 'xpath' coincide con la normativa esperada según el año de construcción.
        """
        # Obtener el valor de 'NormativaVigente' desde el EPC
        normativa_value = epc.get_value_by_xpath(self.xpath)

        if normativa_value is None:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"No se encontró valor para el XPath: {self.xpath}"
            }

        # Obtener el año de construcción
        ano_construccion = epc.get_value_by_xpath("//IdentificacionEdificio/AnoConstruccion")
        if ano_construccion is None:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": "No se encontró el año de construcción ('AnoConstruccion') en el EPC."
            }

        try:
            ano_construccion = int(ano_construccion)
        except ValueError:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"El valor de 'AnoConstruccion' no es un número válido: {ano_construccion}"
            }

        # Validar la normativa vigente
        for condition in self.conditions:
            range_ = condition.get("range", {})
            expected_value = condition.get("expected_value")

            min_year = range_.get("min")
            max_year = range_.get("max")

            if (min_year is None or ano_construccion >= min_year) and (max_year is None or ano_construccion <= max_year):
                if normativa_value.strip().lower() in expected_value.strip().lower():
                    return {
                        "status": "success",
                        "rule_id": self.id,
                        "message": f"La normativa '{normativa_value}' es válida para el año de construcción '{ano_construccion}'."
                    }
                else:
                    return {
                        "status": "error",
                        "rule_id": self.id,
                        "message": f"La normativa '{normativa_value}' no coincide con la esperada '{expected_value}' para el año de construcción '{ano_construccion}'."
                    }

        # Si no se encontró ninguna condición aplicable
        return {
            "status": "error",
            "rule_id": self.id,
            "message": f"No se encontró una normativa válida para el año de construcción '{ano_construccion}'."
        }
