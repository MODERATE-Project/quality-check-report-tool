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
        self.dias_limite = int(self.parameters.get("dias_limite", 90))

    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        mensajes = self.parameters.get("messages", {}).get(key, {})
        return {lang: tpl.format(**kwargs) for lang, tpl in mensajes.items()}

    def _get_translated_details(self, key: str, **kwargs) -> dict:
        detalles = self.parameters.get("details", {}).get(key, {})
        return {
            lang: {k: v.format(**kwargs) for k, v in detalle.items()}
            for lang, detalle in detalles.items()
        }

    def validate(self, epc: "EpcDto") -> Dict:
        result = self._new_result(status="success")

        fecha_visita_str = epc.get_value_by_xpath(self.xpath_fecha_visita)
        fecha_certificado_str = epc.get_value_by_xpath(self.xpath_fecha_certificado)
        datos_visita = epc.get_value_by_xpath(self.xpath_datos_visita)

        if not fecha_visita_str or not fecha_certificado_str:
            result["status"] = "error"
            result["messages"] = self._get_translated_messages("missing_dates")
            result["details"] = self._get_translated_details("missing_dates")
            return result

        result["details"] = {
            "FechaVisita": fecha_visita_str,
            "FechaCertificado": fecha_certificado_str,
            "DatosVisita": datos_visita
        }

        try:
            fecha_visita = datetime.datetime.strptime(fecha_visita_str, "%d/%m/%Y").date()
            fecha_certificado = datetime.datetime.strptime(fecha_certificado_str, "%d/%m/%Y").date()
        except ValueError:
            result["status"] = "error"
            result["messages"] = self._get_translated_messages("invalid_date_format")
            result["details"] = self._get_translated_details("invalid_date_format")
            return result

        diferencia_dias = (fecha_certificado - fecha_visita).days
        if diferencia_dias > self.dias_limite:
            result["status"] = "error"
            result["messages"] = self._get_translated_messages("too_old", dias=diferencia_dias)
            result["details"] = self._get_translated_details("too_old", dias=diferencia_dias)
            return result

        if not datos_visita or not datos_visita.strip():
            result["status"] = "error"
            result["messages"] = self._get_translated_messages("empty_data")
            result["details"] = self._get_translated_details("empty_data")
            return result

        result["messages"] = self._get_translated_messages("valid")
        result["details"] = self._get_translated_details("valid")
        return result
