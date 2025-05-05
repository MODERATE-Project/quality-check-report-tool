from .base_rule import BaseRule, register_rule_class
import pandas as pd
from typing import Dict
from unidecode import unidecode


@register_rule_class
class FieldMatchingInXlsxRule(BaseRule):

    ZONA_CLIMATICA_FIELD_NAME = "Z.C. actualizada"
    MUNICIPIO_FIELD_NAME = "MUNICIPIO"

    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")                 # zona climática a validar
        self.dependent_field = self.parameters.get("dependent_field")  # municipio
        self.valid_values_source = self.parameters.get("valid_values_source")

    # --------------------------------------------------------------------- #
    #  Utilidades
    # --------------------------------------------------------------------- #

    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        messages = self.parameters.get("messages", {}).get(key, {})
        return {
            lang: tpl.format(**kwargs) if tpl else ""
            for lang, tpl in messages.items()
        }

    def _normalize(self,text: str) -> str:
        """minúsculas, sin tildes, sin espacios extremos"""
        return unidecode(text.strip().lower())


    def _split_and_normalize(self, cell: str):
        """Divide por '/', normaliza cada fragmento"""
        return [self._normalize(p) for p in str(cell).split("/")]

    # --------------------------------------------------------------------- #
    #  Validación principal
    # --------------------------------------------------------------------- #
    def validate(self, epc: "EpcDto") -> Dict:
        res = self._new_result()  # por defecto status="error"

        zona_xml_raw = epc.get_value_by_xpath(self.xpath)
        municipio_raw = epc.get_value_by_xpath(self.dependent_field)

        if zona_xml_raw is None:
            res["messages"] = self._get_translated_messages("missing_value", field=self.xpath)
            res["message"] = res["messages"].get("es", "")
            return res
        if municipio_raw is None:
            res["messages"] = self._get_translated_messages("missing_dependent", field=self.dependent_field)
            res["message"] = res["messages"].get("es", "")
            return res

        zona_xml = self._normalize(zona_xml_raw)
        municipio_xml = self._normalize(municipio_raw)

        try:
            df = pd.read_excel(self.valid_values_source)
        except Exception as e:
            res["messages"] = self._get_translated_messages("excel_error", filename=self.valid_values_source, error=str(e))
            res["message"] = res["messages"].get("es", "")
            return res

        for col in (self.MUNICIPIO_FIELD_NAME, self.ZONA_CLIMATICA_FIELD_NAME):
            if col not in df.columns:
                res["messages"] = self._get_translated_messages("column_missing", column=col)
                res["message"] = res["messages"].get("es", "")
                return res

        zonas_validas = set()
        for _, row in df.iterrows():
            municipios_en_fila = self._split_and_normalize(row[self.MUNICIPIO_FIELD_NAME])
            if municipio_xml in municipios_en_fila:
                zonas_en_fila = self._split_and_normalize(row[self.ZONA_CLIMATICA_FIELD_NAME])
                zonas_validas.update(zonas_en_fila)

        if not zonas_validas:
            res["messages"] = self._get_translated_messages("no_zones_found", municipio=municipio_raw)
            res["message"] = res["messages"].get("es", "")
            return res

        if zona_xml not in zonas_validas:
            res["status"] = "error"
            res["details"] = {
                "reason": "invalid_zone",
                "input": zona_xml_raw,
                "expected": list(zonas_validas)
            }
            res["messages"] = self._get_translated_messages("zone_mismatch", zona=zona_xml_raw, municipio=municipio_raw, zonas=", ".join(sorted(zonas_validas)))
            res["message"] = res["messages"].get("es", "")
            return res

        res["status"] = "success"
        res["messages"] = self._get_translated_messages("valid", zona=zona_xml_raw, municipio=municipio_raw)
        res["message"] = res["messages"].get("es", "")
        return res
 