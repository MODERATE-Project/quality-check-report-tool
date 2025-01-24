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
        # Obtener los valores desde el EPC
        referencia_catastral = epc.get_value_by_xpath(self.xpath)
        tipo_de_edificio = epc.get_value_by_xpath(self.dependent_field)

        if referencia_catastral is None:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"No se encontró valor para el XPath: {self.xpath}"
            }

        if tipo_de_edificio is None:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"No se encontró valor para el campo dependiente: {self.dependent_field}"
            }

        # Verificar si el tipo de edificio tiene longitudes definidas
        valid_lengths = self.lengths.get(tipo_de_edificio)
        if valid_lengths is None:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"No se encontraron longitudes válidas para el tipo de edificio '{tipo_de_edificio}'."
            }

        # Validar la longitud de la referencia catastral
        if len(referencia_catastral) not in valid_lengths:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"La longitud de la referencia catastral '{len(referencia_catastral)}' no es válida para el tipo de edificio '{tipo_de_edificio}'. "
                           f"Longitudes permitidas: {valid_lengths}."
            }

        # Si pasa todas las validaciones
        return {
            "status": "success",
            "rule_id": self.id,
            "message": f"La referencia catastral '{referencia_catastral}' es válida para el tipo de edificio '{tipo_de_edificio}'."
        }
