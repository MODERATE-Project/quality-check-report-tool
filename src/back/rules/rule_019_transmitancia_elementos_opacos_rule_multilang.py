from .base_rule import BaseRule, register_rule_class
from typing import Dict, Any
from core.epc_dto import EpcDto

@register_rule_class
class TransmitanciaElementosOpacosRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_elementos = self.parameters.get("xpath_elementos")
        self.xpath_ano = self.parameters.get("xpath_ano")
        self.xpath_zona = self.parameters.get("xpath_zona")

        self.limites_tipo = self.parameters.get("limites_tipo", {})
        self.limites_zona_2007_2013 = self.parameters.get("limites_zona_2007_2013", {})

    def validate(self, epc: EpcDto, questions=None) -> Dict:
        result = self._new_result()
        sospechosos = []

        try:
            ano_construccion = int(epc.get_value_by_xpath(self.xpath_ano))
            zona_climatica = epc.get_value_by_xpath(self.xpath_zona)
        except Exception:
            result["messages"] = {
                "es": "No se puede determinar el año o la zona climática.",
                "en": "Construction year or climate zone could not be determined."
            }
            return result

        elementos = epc.get_nodes_by_xpath(self.xpath_elementos)
        if not elementos:
            result["messages"] = {
                "es": "No se encontraron elementos opacos a validar.",
                "en": "No opaque elements found for validation."
            }
            return result

        for idx, elem in enumerate(elementos):
            tipo = elem.findtext("Tipo")
            transmitancia_str = elem.findtext("Transmitancia")
            if tipo not in self.limites_tipo:
                continue

            try:
                transmitancia = float(transmitancia_str)
            except Exception:
                sospechosos.append({
                    "indice": idx + 1,
                    "tipo": tipo,
                    "valor": transmitancia_str,
                    "motivo": "no numérico"
                })
                continue

            if 2007 <= ano_construccion <= 2013:
                zona_letra = zona_climatica[0] if zona_climatica else ""
                limites_zona = self.limites_zona_2007_2013.get(tipo, {}).get(zona_letra)
                if not limites_zona:
                    sospechosos.append({
                        "indice": idx + 1,
                        "tipo": tipo,
                        "valor": transmitancia,
                        "motivo": f"zona climática '{zona_climatica}' no definida"
                    })
                    continue
                min_val, max_val = limites_zona
            else:
                limites = None
                for periodo in self.limites_tipo[tipo]:
                    if periodo["desde"] <= ano_construccion <= periodo["hasta"]:
                        limites = (periodo["min"], periodo["max"])
                        break
                if not limites:
                    sospechosos.append({
                        "indice": idx + 1,
                        "tipo": tipo,
                        "valor": transmitancia,
                        "motivo": f"no se encontró periodo para año {ano_construccion}"
                    })
                    continue
                min_val, max_val = limites

            if not (min_val <= transmitancia <= max_val):
                sospechosos.append({
                    "indice": idx + 1,
                    "tipo": tipo,
                    "valor": transmitancia,
                    "motivo": f"fuera de rango ({min_val} - {max_val})"
                })

        if sospechosos:
            result["messages"] = {
                "es": "Se han detectado valores de transmitancia fuera de los rangos permitidos.",
                "en": "Some transmittance values were found to be outside the permitted ranges."
            }
            result["details"] = {
                "es": {"valores_sospechosos": sospechosos},
                "en": {"suspect_values": sospechosos}
            }
            return result

        result["status"] = "success"
        result["messages"] = {
            "es": "Todos los valores de transmitancia son correctos.",
            "en": "All transmittance values are within permitted ranges."
        }
        return result
