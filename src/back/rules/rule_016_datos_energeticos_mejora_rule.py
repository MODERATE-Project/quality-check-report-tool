import os
import re
from .base_rule import BaseRule, register_rule_class
from typing import Dict

@register_rule_class
class DatosEnergeticosMejoraRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_medidas_mejora = self.parameters.get("xpath_medidas_mejora")

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Verifica que en <MedidasDeMejora> haya al menos una <Medida>
        y que ninguna medida tenga los tres campos (<Nombre>, <Descripcion>, <CosteEstimado>) vacíos.
        """
        validation_result = {
            "rule_id": self.id,
            "status": "success",
            "message": "Las medidas de mejora están correctamente definidas.",
            "description": self.description,
            "details": {}
        }

        # Obtener todos los nodos <Medida> dentro de <MedidasDeMejora>
        medidas = epc.get_nodes_by_xpath(self.xpath_medidas_mejora)
        if not medidas:
            validation_result["status"] = "error"
            validation_result["message"] = "Debe indicarse al menos una medida de mejora."
            return validation_result  # Si no hay medidas de mejora, la validación falla

        for index, medida in enumerate(medidas, start=1):
            nombre = medida.find("Nombre")
            descripcion = medida.find("Descripcion")
            coste_estimado = medida.find("CosteEstimado")

            nombre_valido = nombre is not None and nombre.text and nombre.text.strip()
            descripcion_valido = descripcion is not None and descripcion.text and descripcion.text.strip()
            coste_estimado_valido = coste_estimado is not None and coste_estimado.text and coste_estimado.text.strip()

            # Si los tres campos están vacíos, marcamos como error
            if not nombre_valido and not descripcion_valido and not coste_estimado_valido:
                validation_result["status"] = "error"
                validation_result["message"] = "Al menos una medida tiene todos sus valores vacíos."
                validation_result["details"] = {f"Medida {index}": "Todos los campos (Nombre, Descripción, CosteEstimado) están vacíos."}
                return validation_result

        # Si todo está correcto:
        validation_result["status"] = "success"
        validation_result["message"] = "Las medidas de mejora están correctamente definidas."
        return validation_result
