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
    @staticmethod
    def _normalize(text: str) -> str:
        """minúsculas, sin tildes, sin espacios extremos"""
        return unidecode(text.strip().lower())

    @staticmethod
    def _split_and_normalize(cell: str):
        """Divide por '/', normaliza cada fragmento"""
        return [FieldMatchingInXlsxRule._normalize(p) for p in str(cell).split("/")]

    # --------------------------------------------------------------------- #
    #  Validación principal
    # --------------------------------------------------------------------- #
    def validate(self, epc: "EpcDto") -> Dict:
        res = {
            "rule_id":     self.id,
            "status":      "error",
            "message":     "",
            "description": self.description,
            "details":     {}
        }

        # 1) Valores leídos del XML --------------------------------------------------
        zona_xml_raw = epc.get_value_by_xpath(self.xpath)
        municipio_raw = epc.get_value_by_xpath(self.dependent_field)

        if zona_xml_raw is None:
            res["message"] = f"No se encontró valor para el XPath: {self.xpath}"
            return res
        if municipio_raw is None:
            res["message"] = f"No se encontró valor para el campo dependiente: {self.dependent_field}"
            return res

        zona_xml      = self._normalize(zona_xml_raw)
        municipio_xml = self._normalize(municipio_raw)

        # 2) Cargamos el Excel -------------------------------------------------------
        try:
            df = pd.read_excel(self.valid_values_source)
        except Exception as e:
            res["message"] = f"No se pudo leer el archivo Excel '{self.valid_values_source}': {e}"
            return res

        for col in (self.MUNICIPIO_FIELD_NAME, self.ZONA_CLIMATICA_FIELD_NAME):
            if col not in df.columns:
                res["message"] = f"El Excel no contiene la columna '{col}'."
                return res

        # 3) Recorremos filas, buscando las que contengan nuestro municipio ----------
        zonas_validas = set()

        for _, row in df.iterrows():
            municipios_en_fila = self._split_and_normalize(row[self.MUNICIPIO_FIELD_NAME])
            if municipio_xml in municipios_en_fila:
                # añadimos todas las zonas (también pueden venir separadas por '/')
                zonas_en_fila = self._split_and_normalize(row[self.ZONA_CLIMATICA_FIELD_NAME])
                zonas_validas.update(zonas_en_fila)

        # 4) Si no encontramos ninguna zona para ese municipio -----------------------
        if not zonas_validas:
            res["message"] = f"No se encontraron valores válidos para el municipio '{municipio_raw}'."
            return res

        # 5) Comprobamos si la zona del XML está entre las válidas -------------------
        if zona_xml not in zonas_validas:
            res.update({
                "details": (f"El valor '{zona_xml_raw}' no es válido para el municipio "
                            f"'{municipio_raw}'. Zonas admitidas: {', '.join(sorted(zonas_validas))}."),
                "message": (f"Dada la localidad ('{municipio_raw}'), "
                            f"la zona climática del XML ('{zona_xml_raw}') no concuerda ni con el CTE "
                            f"ni con la actualización de 2022.")
            })
            return res

        # 6) Todo correcto -----------------------------------------------------------
        res.update({
            "status":  "success",
            "message": f"El valor '{zona_xml_raw}' es válido para el municipio '{municipio_raw}'."
        })
        return res
