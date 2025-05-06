from typing import Dict
from .base_rule import BaseRule, register_rule_class

@register_rule_class
class DatosEnergeticosMejoraRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_medidas_mejora = self.parameters.get("xpath_medidas_mejora")

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
        Verifica que en <MedidasDeMejora> haya al menos una <Medida>
        y que ninguna tenga todos sus campos clave vacíos.
        """
        result = self._new_result()

        medidas = epc.get_nodes_by_xpath(self.xpath_medidas_mejora)
        if not medidas:
            result["messages"] = self._get_translated_messages("missing")
            result["message"] = result["messages"].get("es", "")
            result["details"] = self._get_translated_details("missing")
            return result

        for idx, medida in enumerate(medidas, start=1):
            nombre = medida.find("Nombre")
            descripcion = medida.find("Descripcion")
            coste = medida.find("CosteEstimado")

            nombre_ok = nombre is not None and nombre.text and nombre.text.strip()
            descripcion_ok = descripcion is not None and descripcion.text and descripcion.text.strip()
            coste_ok = coste is not None and coste.text and coste.text.strip()

            if not nombre_ok and not descripcion_ok and not coste_ok:
                result["messages"] = self._get_translated_messages("all_empty", idx=idx)
                result["message"] = result["messages"].get("es", "")
                result["details"] = self._get_translated_details("all_empty", idx=idx)
                return result

        result["status"] = "success"
        result["messages"] = self._get_translated_messages("valid")
        result["message"] = result["messages"].get("es", "")
        result["details"] = self._get_translated_details("valid")
        return result
