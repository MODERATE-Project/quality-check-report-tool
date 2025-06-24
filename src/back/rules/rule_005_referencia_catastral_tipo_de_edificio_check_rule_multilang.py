from .base_rule import BaseRule, register_rule_class
from typing import Dict


@register_rule_class
class ReferenciaCatastralTipoDeEdificioRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")
        self.dependent_field = self.parameters.get("dependent_field")
        self.lengths = self.parameters.get("lengths", {})

    
    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        messages = self.parameters.get("messages", {}).get(key, {})
        return {
            lang: tpl.format(**kwargs) if tpl else ""
            for lang, tpl in messages.items()
        }

    def _get_translated_details(self, key: str, **kwargs) -> dict:
        details_template = self.parameters.get("details", {}).get(key, {})
        return {
            lang: {
                k: v.format(**kwargs) if isinstance(v, str) else v
                for k, v in detail.items()
            }
            for lang, detail in details_template.items()
        }

    def validate(self, epc: "EpcDto") -> Dict:

        """
        Valida que la longitud de 'ReferenciaCatastral' coincida con los valores permitidos para el tipo de edificio.
        """
        validation_result = self._new_result()  # por defecto status="error"

        # Obtener los valores desde el EPC
        referencia_catastral = epc.get_value_by_xpath(self.xpath)
        tipo_de_edificio = epc.get_value_by_xpath(self.dependent_field)

        if referencia_catastral is None:
            validation_result["messages"] = self._get_translated_messages("missing_value", xpath=self.xpath)
            return validation_result

        if tipo_de_edificio is None:
            validation_result["messages"] = self._get_translated_messages("missing_dependent", field=self.dependent_field)
            return validation_result

        # Verificar si el tipo de edificio tiene longitudes definidas
        valid_lengths = self.lengths.get(tipo_de_edificio)
        if valid_lengths is None:
            validation_result["messages"] = self._get_translated_messages("no_lengths", tipo=tipo_de_edificio)
            return validation_result

        # Validar la longitud de la referencia catastral
        if len(referencia_catastral) not in valid_lengths:
            validation_result["details"] = self._get_translated_details("invalid_length", tipo=tipo_de_edificio, longitud=len(referencia_catastral), permitidas=", ".join(map(str, valid_lengths)))
            validation_result["messages"] = self._get_translated_messages("invalid_length", tipo=tipo_de_edificio)
            return validation_result

        # Si pasa todas las validaciones
        validation_result["status"] = "success"
        validation_result["messages"] = self._get_translated_messages("valid", tipo=tipo_de_edificio, referencia=referencia_catastral)
        return validation_result
