from .base_rule import BaseRule, register_rule_class
import pandas as pd
from typing import Dict


@register_rule_class
class FieldMatchingInXlsxRule(BaseRule):

    ZONA_CLIMATICA_FIELD_NAME = "Z.C. actualizada"
    MUNICIPIO_FIELD_NAME = "MUNICIPIO"

    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")
        self.dependent_field = self.parameters.get("dependent_field")
        self.valid_values_source = self.parameters.get("valid_values_source")

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que el valor en el campo especificado por 'xpath' coincide con un valor válido dependiente
        del valor en 'dependent_field' dentro del archivo Excel.
        """
        validation_result = {
            "status": "error",
            "rule_id": self.id,
            "message": "",
            "description": self.description,
        }

        # Leer los valores desde el documento EPC utilizando XPath
        value_to_validate = epc.get_value_by_xpath(self.xpath)
        dependent_value = epc.get_value_by_xpath(self.dependent_field)

        if value_to_validate is None:
            validation_result["message"] = f"No se encontró valor para el XPath: {self.xpath}"
            return validation_result

        if dependent_value is None:
            validation_result["message"] = f"No se encontró valor para el campo dependiente: {self.dependent_field}"
            return validation_result

        # Leer el archivo Excel
        try:
            excel_data = pd.read_excel(self.valid_values_source)
        except Exception as e:
            validation_result["message"] = f"No se pudo leer el archivo Excel '{self.valid_values_source}': {e}"
            return validation_result

        # Asegurar que las columnas requeridas existen
        if self.MUNICIPIO_FIELD_NAME not in excel_data.columns or self.ZONA_CLIMATICA_FIELD_NAME not in excel_data.columns:
            validation_result["message"] = "El archivo Excel no contiene las columnas 'MUNICIPIO' y 'ZONA_CLIMATICA'."
            return validation_result

        # Filtrar las zonas climáticas válidas para el municipio
        valid_values = excel_data[excel_data[self.MUNICIPIO_FIELD_NAME].str.strip().str.lower() == dependent_value.strip().lower()]

        if valid_values.empty:
            validation_result["message"] = f"No se encontraron valores válidos para el municipio '{dependent_value}'."
            return validation_result

        # Extraer las zonas climáticas válidas
        valid_zones = valid_values[self.ZONA_CLIMATICA_FIELD_NAME].dropna().astype(str).str.strip().str.lower().tolist()

        # Validar si el valor actual está en las zonas válidas
        if value_to_validate.strip().lower() not in valid_zones:
            validation_result["message"] = f"El valor '{value_to_validate}' no es válido para el municipio '{dependent_value}'."
            return validation_result

        # Si pasa todas las validaciones
        validation_result["status"] = "success"
        validation_result["message"] = f"El valor '{value_to_validate}' es válido para el municipio '{dependent_value}'."
        return validation_result
