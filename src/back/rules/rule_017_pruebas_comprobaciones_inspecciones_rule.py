import datetime
from .base_rule import BaseRule, register_rule_class
from typing import Dict

@register_rule_class
class PruebasComprobacionesInspeccionesRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_fecha_visita = self.parameters.get("xpath_fecha_visita")
        self.xpath_fecha_certificado = self.parameters.get("xpath_fecha_certificado")
        self.xpath_datos_visita = self.parameters.get("xpath_datos_visita")
        self.dias_limite = 90  # Número máximo de días permitidos

    def validate(self, epc: "EpcDto") -> Dict:
        validation_result = self._new_result()  # por defecto status="error"

        # Obtener la fecha de visita y la fecha del certificado
        fecha_visita_str = epc.get_value_by_xpath(self.xpath_fecha_visita)
        fecha_certificado_str = epc.get_value_by_xpath(self.xpath_fecha_certificado)
        datos_visita = epc.get_value_by_xpath(self.xpath_datos_visita)

        # Verificar que los valores existen
        if not fecha_visita_str or not fecha_certificado_str:
            validation_result["status"] = "error"
            validation_result["message"] = "No se encontró la fecha de visita o la fecha del certificado."
            return validation_result

        try:
            fecha_visita = datetime.datetime.strptime(fecha_visita_str, "%d/%m/%Y").date()
            fecha_certificado = datetime.datetime.strptime(fecha_certificado_str, "%d/%m/%Y").date()
        except ValueError:
            validation_result["status"] = "error"
            validation_result["message"] = "Formato de fecha incorrecto en la visita o certificado."
            validation_result["details"]["FechaVisita"] = fecha_visita_str
            validation_result["details"]["FechaCertificado"] = fecha_certificado_str
            return validation_result

        # Verificar si la fecha de visita está dentro del rango permitido
        diferencia_dias = (fecha_certificado - fecha_visita).days
        if diferencia_dias > self.dias_limite:
            validation_result["status"] = "error"
            validation_result["message"] = "La visita debe ser máximo 90 días previa a la emisión del certificado."
            validation_result["details"]["FechaVisita"] = fecha_visita_str
            validation_result["details"]["FechaCertificado"] = fecha_certificado_str

        # Verificar que el campo de datos de la visita no esté vacío
        if not datos_visita or not datos_visita.strip():
            validation_result["status"] = "error"
            validation_result["message"] = "Debe figurar una descripción de la visita realizada."
            validation_result["details"]["DatosVisita"] = "DatosVisita Vacío"

        return validation_result
