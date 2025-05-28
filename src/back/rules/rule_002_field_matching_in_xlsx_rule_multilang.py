from .base_rule import BaseRule, register_rule_class
import pandas as pd
from typing import Dict
from unidecode import unidecode

@register_rule_class
class FieldMatchingInXlsxRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)

        # XPath para extraer el valor a validar (zona climática) y el campo dependiente (municipio)
        self.xpath = self.parameters.get("xpath")
        self.dependent_field = self.parameters.get("dependent_field")

        # Ruta al archivo Excel con los valores válidos
        self.valid_values_source = self.parameters.get("valid_values_source")

        # Nombre de las columnas en el Excel
        self.column_filter = self.parameters.get("column_filter")  # Ej. "MUNICIPIO"
        self.column_match_actualizada = self.parameters.get("column_match_actualizada")  # Ej. "Z.C. actualizada"
        self.column_match_cte = self.parameters.get("column_match_cte")  # Ej. "Z.C. CTE"

    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        """
        Devuelve los mensajes en todos los idiomas para una clave dada,
        interpolando los valores necesarios.
        """
        messages = self.parameters.get("messages", {}).get(key, {})
        return {
            lang: tpl.format(**kwargs) if tpl else ""
            for lang, tpl in messages.items()
        }

    def _normalize(self, text: str) -> str:
        """
        Devuelve el texto en minúsculas, sin tildes ni espacios.
        """
        return unidecode(text.strip().lower())

    def _split_and_normalize(self, cell: str):
        """
        Dado un valor de celda, lo separa por "/" y normaliza cada parte.
        """
        return [self._normalize(p) for p in str(cell).split("/")]

    def validate(self, epc: "EpcDto") -> Dict:
        res = self._new_result()

        # Obtener valores del XML
        zona_xml_raw = epc.get_value_by_xpath(self.xpath)
        municipio_raw = epc.get_value_by_xpath(self.dependent_field)

        # Validar existencia de ambos campos
        if zona_xml_raw is None:
            res["messages"] = self._get_translated_messages("missing_value", field=self.xpath)
            return res
        if municipio_raw is None:
            res["messages"] = self._get_translated_messages("missing_dependent", field=self.dependent_field)
            return res

        # Normalizar para comparación
        zona_xml = self._normalize(zona_xml_raw)
        municipio_xml = self._normalize(municipio_raw)

        # Leer el Excel
        try:
            df = pd.read_excel(self.valid_values_source)
        except Exception as e:
            res["messages"] = self._get_translated_messages("excel_error", filename=self.valid_values_source, error=str(e))
            return res

        # Comprobar que las columnas necesarias existen
        for col in (self.column_filter, self.column_match_actualizada, self.column_match_cte):
            if col not in df.columns:
                res["messages"] = self._get_translated_messages("column_missing", column=col)
                return res

        # Recopilar todas las zonas válidas asociadas al municipio
        zonas_validas = set()
        for _, row in df.iterrows():
            municipios = self._split_and_normalize(row[self.column_filter])
            if municipio_xml in municipios:
                zonas_validas.update(self._split_and_normalize(row[self.column_match_actualizada]))
                zonas_validas.update(self._split_and_normalize(row[self.column_match_cte]))

        # Si no se encontraron zonas válidas para el municipio
        if not zonas_validas:
            res["messages"] = self._get_translated_messages("no_zones_found", municipio=municipio_raw)
            return res

        # Comprobar si la zona del XML está entre las válidas
        if zona_xml not in zonas_validas:
            res["status"] = "error"
            res["details"] = {
                "reason": "invalid_zone",
                "input": zona_xml_raw,
                "expected": sorted(list(zonas_validas))
            }
            res["messages"] = self._get_translated_messages(
                "zone_mismatch",
                zona=zona_xml_raw,
                municipio=municipio_raw,
                zonas=", ".join(sorted(zonas_validas))
            )
            return res

        # Si todo es correcto
        res["status"] = "success"
        res["messages"] = self._get_translated_messages("valid", zona=zona_xml_raw, municipio=municipio_raw)
        return res
