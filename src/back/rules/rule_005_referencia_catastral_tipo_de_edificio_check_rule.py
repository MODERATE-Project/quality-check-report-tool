from .base_rule import BaseRule, register_rule_class
from typing import Dict


@register_rule_class
class ReferenciaCatastralTipoDeEdificioRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")
        self.dependent_field = self.parameters.get("dependent_field")
        self.lengths = self.parameters.get("lengths", {})

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que la longitud de 'ReferenciaCatastral' coincida con los valores permitidos para el tipo de edificio.
        """
        validation_result = self._new_result()  # por defecto status="error"

        # Obtener los valores desde el EPC
        referencia_catastral = epc.get_value_by_xpath(self.xpath)
        tipo_de_edificio = epc.get_value_by_xpath(self.dependent_field)

        if referencia_catastral is None:
            validation_result["message"] = f"No se encontró valor para el XPath: {self.xpath}"
            return validation_result

        if tipo_de_edificio is None:
            validation_result["message"] = f"No se encontró valor para el campo dependiente: {self.dependent_field}"
            return validation_result

        # Verificar si el tipo de edificio tiene longitudes definidas
        valid_lengths = self.lengths.get(tipo_de_edificio)
        if valid_lengths is None:
            validation_result["message"] = f"No se encontraron longitudes válidas para el tipo de edificio '{tipo_de_edificio}'."
            return validation_result

        # Validar la longitud de la referencia catastral
        if len(referencia_catastral) not in valid_lengths:
            validation_result["details"] = (
                f"La longitud de la referencia catastral '{len(referencia_catastral)}' no es válida para el tipo de edificio '{tipo_de_edificio}'. "
                f"Longitudes permitidas: {valid_lengths}."
            )
            validation_result["message"] = (
                f"No concuerda el número de dígitos de la referencia catastral con el Tipo de Edificio considerado, en este caso '{tipo_de_edificio}'."
            )
            return validation_result

        # Si pasa todas las validaciones
        validation_result["status"] = "success"
        validation_result["message"] = (
            f"La referencia catastral '{referencia_catastral}' es válida para el tipo de edificio '{tipo_de_edificio}'."
        )
        return validation_result
