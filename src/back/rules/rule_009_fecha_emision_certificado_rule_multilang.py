from .base_rule import BaseRule, register_rule_class
from typing import Dict
from datetime import datetime, timedelta


@register_rule_class
class FechaEmisionCertificadoRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_fecha = self.parameters.get("xpath_fecha")
        self.max_days_difference = self.parameters.get("max_days_difference", 30)

    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        messages = self.parameters.get("messages", {}).get(key, {})
        return {lang: tpl.format(**kwargs) for lang, tpl in messages.items()}

    def _get_translated_details(self, key: str, **kwargs) -> dict:
        template = self.parameters.get("details", {}).get(key, {})
        return {
            lang: {k: v.format(**kwargs) for k, v in detail.items()}
            for lang, detail in template.items()
        }

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que la fecha de emisión del certificado no sea superior
        a N días antes de la fecha actual.
        """
        validation_result = self._new_result()

        fecha_emision_str = epc.get_value_by_xpath(self.xpath_fecha)
        if fecha_emision_str is None:
            validation_result["messages"] = self._get_translated_messages("missing", xpath=self.xpath_fecha)
            return validation_result

        try:
            fecha_emision = datetime.strptime(fecha_emision_str, "%d/%m/%Y")
        except ValueError:
            validation_result["messages"] = self._get_translated_messages("invalid_format", value=fecha_emision_str)
            validation_result["details"] = self._get_translated_details("invalid_format", value=fecha_emision_str)
            return validation_result

        fecha_actual = datetime.today()
        fecha_limite = fecha_actual - timedelta(days=self.max_days_difference)

        if fecha_emision < fecha_limite:
            validation_result["messages"] = self._get_translated_messages("too_old", fecha=fecha_emision.strftime("%d/%m/%Y"), dias=self.max_days_difference)
            validation_result["details"] = self._get_translated_details(
                "too_old",
                fecha=fecha_emision.strftime("%d/%m/%Y"),
                hoy=fecha_actual.strftime("%d/%m/%Y"),
                limite=fecha_limite.strftime("%d/%m/%Y")
            )
            return validation_result

        validation_result["status"] = "success"
        validation_result["messages"] = self._get_translated_messages("valid", fecha=fecha_emision.strftime("%d/%m/%Y"))
        validation_result["details"] = self._get_translated_details("valid", fecha=fecha_emision.strftime("%d/%m/%Y"))
        return validation_result
