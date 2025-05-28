from .base_rule import BaseRule, register_rule_class
from xml.etree.ElementTree import Element
from typing import Dict
from core.epc_dto import EpcDto

@register_rule_class
class PuentesTermicosCERMARule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_procedimiento = self.parameters.get("xpath_procedimiento")
        self.xpath_puentes = self.parameters.get("xpath_puentes")

    def validate(self, epc: EpcDto) -> Dict:
        result = self._new_result()

        # 1. Verificar si el procedimiento contiene 'CERMA'
        procedimiento = epc.get_value_by_xpath(self.xpath_procedimiento)
        if not procedimiento or "cerma" not in procedimiento.lower():
            result["status"] = "success"
            result["messages"] = self._get_translated_messages("not_applicable")
            return result

        # 2. Obtener los nodos <Puentes_Termicos>
        nodo = epc.get_nodes_by_xpath(self.xpath_puentes)

        if nodo is None or len(nodo) == 0:
            result["status"] = "error"
            result["messages"] = self._get_translated_messages("missing")
            return result

        # 3. Todo está correcto
        result["status"] = "success"
        result["messages"] = self._get_translated_messages("ok")
        return result
