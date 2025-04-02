import os
from .base_rule import BaseRule, register_rule_class
from typing import Dict

# Tabla de demanda de ACS en función del número de dormitorios (en litros/día)
DEMANDA_POR_DORMITORIOS = {
    1: 42,   # 1,5 personas * 28 L/día
    2: 84,   # 3 personas * 28 L/día
    3: 112,  # 4 personas * 28 L/día
    4: 140,  # 5 personas * 28 L/día
    5: 168,  # 6 personas * 28 L/día
    6: 196,  # 7 personas * 28 L/día
    "6+": 196 # Más de 6 dormitorios, mismo valor que 6
}

# Factores de descentralización según el CTE
FACTOR_DESCENTRALIZACION = {
    3: 1.00,
    10: 0.95,
    20: 0.90,
    50: 0.85,
    75: 0.80,
    100: 0.75,
    101: 0.70
}

@register_rule_class
class DemandaDiariaACSRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_tipo_edificio = self.parameters.get("xpath_tipo_edificio")

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Genera todas las posibles demandas diarias de ACS según el número de dormitorios
        y, si el tipo de edificio es BloqueDeViviendaCompleto, aplica los factores de descentralización.
        """
        validation_result = {
            "rule_id": self.id,
            "status": "error", #aquí tenia info, porque esta regla necesita interacción con el usuario
            "message": "",
            "description": self.description,
            "details": {}
        }

        # Obtener el tipo de edificio
        tipo_edificio = epc.get_value_by_xpath(self.xpath_tipo_edificio)

        # Si el tipo de edificio no es válido, mostrar el error
        if tipo_edificio not in self.parameters["values"]:
            validation_result["message"] = f"Tipo de edificio no válido: {tipo_edificio}."
            validation_result["details"] = {"provided_value": tipo_edificio}
            return validation_result

        # Calcular la demanda en función de los dormitorios
        demanda_por_dormitorios = {d: f"{v} L/día" for d, v in DEMANDA_POR_DORMITORIOS.items()}

        # Si el tipo de edificio es "BloqueDeViviendaCompleto", calcular factor de descentralización
        if tipo_edificio == "BloqueDeViviendaCompleto":
            demanda_por_viviendas = {}
            for num_viviendas in sorted(FACTOR_DESCENTRALIZACION.keys()):
                factor = FACTOR_DESCENTRALIZACION[num_viviendas]
                demanda_vivienda = {
                    d: f"{v * factor:.2f} L/día (Factor {factor})"
                    for d, v in DEMANDA_POR_DORMITORIOS.items()
                }
                demanda_por_viviendas[num_viviendas] = demanda_vivienda

            validation_result["message"] = "Demanda ACS estimada para BloqueDeViviendaCompleto con factores de descentralización."
            validation_result["details"] = {
                "tipo_edificio": tipo_edificio,
                "demanda_por_viviendas": demanda_por_viviendas
            }
            return validation_result

        # Si no es BloqueDeViviendaCompleto, solo devolver los valores por dormitorios
        validation_result["message"] = "Demanda ACS estimada según el número de dormitorios."
        validation_result["details"] = {
            "tipo_edificio": tipo_edificio,
            "demanda_por_dormitorios": demanda_por_dormitorios
        }
        return validation_result
