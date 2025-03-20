from .base_rule import BaseRule, register_rule_class
from typing import Dict
from datetime import datetime, timedelta

@register_rule_class
class FechaEmisionCertificadoRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_fecha = self.parameters.get("xpath_fecha")  # XPath para obtener la fecha
        self.max_days_difference = self.parameters.get("max_days_difference", 30)  # Límite en días

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que la fecha de emisión del certificado no sea superior a 30 días antes de la fecha actual.
        """
        validation_result = {
            "rule_id": self.id,
            "status": "error",
            "message": "",
            "description": self.description,
            "details": {}
        }

        # Obtener la fecha de emisión desde el XML
        fecha_emision_str = epc.get_value_by_xpath(self.xpath_fecha)

        if fecha_emision_str is None:
            validation_result["message"] = f"No se encontró la fecha de emisión en el XPath: {self.xpath_fecha}"
            return validation_result

        try:
            fecha_emision = datetime.strptime(fecha_emision_str, "%d/%m/%Y")  # Formato esperado: DD/MM/YYYY
        except ValueError:
            validation_result["message"] = f"Formato de fecha inválido: {fecha_emision_str}. Se esperaba DD/MM/YYYY."
            validation_result["details"] = {"provided_fecha": fecha_emision_str}
            return validation_result

        # Calcular la fecha límite permitida (máximo 30 días atrás)
        fecha_actual = datetime.today()
        fecha_limite = fecha_actual - timedelta(days=self.max_days_difference)

        if fecha_emision < fecha_limite:
            validation_result["message"] = (
                "La fecha de registro del certificado no puede superar los 30 días posteriores a su emisión."
            )
            validation_result["details"] = {
                "provided_fecha": fecha_emision.strftime("%d/%m/%Y"),
                "fecha_actual": fecha_actual.strftime("%d/%m/%Y"),
                "fecha_limite": fecha_limite.strftime("%d/%m/%Y")
            }
            return validation_result

        # Si pasa la validación
        validation_result["status"] = "success"
        validation_result["message"] = "La fecha de emisión del certificado es válida."
        validation_result["details"] = {
            "validated_fecha": fecha_emision.strftime("%d/%m/%Y")
        }
        return validation_result
