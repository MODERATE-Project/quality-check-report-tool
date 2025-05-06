import os
from typing import Dict
from .base_rule import BaseRule, register_rule_class

@register_rule_class
class PuentesTermicosRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_puentes_termicos = self.parameters.get("xpath_puentes_termicos")

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
        """
        Verifica que la categoría 'PuentesTermicos' no esté vacía
        y que ninguna longitud sea 0 o no válida.
        """
        validation_result = self._new_result()  # por defecto status="error"

        # Obtener todos los nodos PuenteTermico
        puentes_termicos = epc.get_nodes_by_xpath(self.xpath_puentes_termicos)

        if not puentes_termicos:
            validation_result["messages"] = self._get_translated_messages("missing")
            validation_result["message"] = validation_result["messages"].get("es", "")
            validation_result["details"] = self._get_translated_details("missing")
            return validation_result

        # Revisar cada PuenteTermico y su Longitud
        for index, puente in enumerate(puentes_termicos, start=1):
            longitud_element = puente.find("Longitud")
            if longitud_element is None or not longitud_element.text.strip():
                validation_result["messages"] = self._get_translated_messages("missing_length", idx=index)
                validation_result["message"] = validation_result["messages"].get("es", "")
                validation_result["details"] = self._get_translated_details("missing_length", idx=index)
                return validation_result

            try:
                longitud_valor = float(longitud_element.text.strip())
                if longitud_valor == 0:
                    validation_result["messages"] = self._get_translated_messages("zero_length", idx=index)
                    validation_result["message"] = validation_result["messages"].get("es", "")
                    validation_result["details"] = self._get_translated_details("zero_length", idx=index)
                    return validation_result
            except ValueError:
                valor = longitud_element.text.strip()
                validation_result["messages"] = self._get_translated_messages("invalid_value", idx=index, valor=valor)
                validation_result["message"] = validation_result["messages"].get("es", "")
                validation_result["details"] = self._get_translated_details("invalid_value", idx=index, valor=valor)
                return validation_result

        # Si todo está correcto:
        validation_result["status"] = "success"
        validation_result["messages"] = self._get_translated_messages("valid")
        validation_result["message"] = validation_result["messages"].get("es", "")
        validation_result["details"] = self._get_translated_details("valid")
        return validation_result
