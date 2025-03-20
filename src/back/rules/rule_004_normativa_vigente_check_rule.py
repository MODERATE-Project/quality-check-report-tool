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
        # Crear resultado inicial común para incluir campos adicionales
        validation_result = {
            "status": "error",
            "rule_id": self.id,
            "message": "",
            "description": self.description,
            "details": {}
        }

        # Obtener el valor de 'NormativaVigente' desde el EPC
        normativa_value = epc.get_value_by_xpath(self.xpath)

        if normativa_value is None:
            validation_result["message"] = f"No se encontró valor para el XPath: {self.xpath}"
            return validation_result

        # Obtener el año de construcción
        ano_construccion = epc.get_value_by_xpath("//IdentificacionEdificio/AnoConstruccion")
        if ano_construccion is None:
            validation_result["message"] = "No se encontró el año de construcción ('AnoConstruccion') en el EPC."
            return validation_result

        try:
            ano_construccion = int(ano_construccion)
        except ValueError:
            validation_result["message"] = f"El valor de 'AnoConstruccion' no es un número válido: {ano_construccion}"
            validation_result["details"] = {"provided_ano_construccion": ano_construccion}
            return validation_result

        # Normalizar la normativa actual
        normativa_value_normalized = normativa_value.strip().lower()

        # Validar la normativa vigente
        for condition in self.conditions:
            range_ = condition.get("range", {})
            expected_value = condition.get("expected_value", "")

            min_year = range_.get("min")
            max_year = range_.get("max")

            # Convertir los valores esperados en una lista y normalizarlos
            expected_values = [v.strip().lower() for v in expected_value.split("/")]

            if (min_year is None or ano_construccion >= min_year) and (max_year is None or ano_construccion <= max_year):
                if normativa_value_normalized in expected_values:
                    validation_result["status"] = "success"
                    validation_result["message"] = (
                        f"La normativa '{normativa_value}' es válida para el año de construcción '{ano_construccion}'."
                    )
                    validation_result["details"] = {
                        "validated_normativa": normativa_value,
                        "validated_ano_construccion": ano_construccion,
                        "expected_normativa": expected_value
                    }
                    return validation_result
                else:
                    validation_result["message"] = (
                        f"La normativa aplicada no concuerda con la correspondiente al año de construcción de la edificación."
                    )
                    validation_result["details"] = {
                        "provided_normativa": normativa_value,
                        "validated_ano_construccion": ano_construccion,
                        "expected_normativa": expected_value
                    }
                    return validation_result

        # Si no se encontró ninguna condición aplicable
        validation_result["message"] = (
            f"No se encontró una normativa válida para el año de construcción '{ano_construccion}'."
        )
        validation_result["details"] = {"provided_ano_construccion": ano_construccion}
        return validation_result
