
import os
from .base_rule import BaseRule, register_rule_class
from typing import Dict

@register_rule_class
class PuentesTermicosRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_puentes_termicos = self.parameters.get("xpath_puentes_termicos")

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Verifica que la categoría 'PuentesTermicos' no esté vacía y que ninguna longitud sea 0.
        """
        validation_result = {
            "rule_id": self.id,
            "status": "error",
            "message": "La definición del edificio debe incluir puentes térmicos.",
            "description": self.description,
            "details": {}
        }

        # Obtener todos los nodos PuenteTermico
        puentes_termicos = epc.get_nodes_by_xpath(self.xpath_puentes_termicos)

        if not puentes_termicos:
            return validation_result  # Si no hay puentes térmicos, ya está mal

        # Revisar cada PuenteTermico y su Longitud
        for index, puente in enumerate(puentes_termicos, start=1):
            longitud_element = puente.find("Longitud")
            
            if longitud_element is None or not longitud_element.text.strip():
                validation_result["details"][f"PuenteTermico_{index}"] = "Error: Longitud no especificada"
                return validation_result
            
            try:
                longitud_valor = float(longitud_element.text.strip())
                if longitud_valor == 0:
                    validation_result["details"][f"PuenteTermico_{index}"] = "Error: Longitud no puede ser 0"
                    return validation_result
            except ValueError:
                validation_result["details"][f"PuenteTermico_{index}"] = f"Error: Valor inválido ({longitud_element.text})"
                return validation_result

        # Si todo está correcto:
        validation_result["status"] = "success"
        validation_result["message"] = "Los puentes térmicos están correctamente definidos."
        return validation_result
