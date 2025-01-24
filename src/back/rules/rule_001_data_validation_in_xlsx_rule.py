from .base_rule import BaseRule, register_rule_class
import pandas as pd
from typing import Dict

@register_rule_class
class DataValidationInXlsxRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")
        self.column_in_source = self.parameters.get("column_in_source")
        self.valid_values_source = self.parameters.get("valid_values_source")
        self.allow_multiple_languages = self.parameters.get("allow_multiple_languages", False)

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que el valor en el campo especificado por 'xpath' esté en la columna 'municipio' del Excel.
        """
        # Leer el valor desde el documento EPC utilizando XPath
        value_to_validate = epc.get_value_by_xpath(self.xpath)
        if value_to_validate is None:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"No se encontró valor para el XPath: {self.xpath}"
            }

        # Leer el archivo Excel
        try:
            excel_data = pd.read_excel(self.valid_values_source)
        except Exception as e:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"No se pudo leer el archivo Excel '{self.valid_values_source}': {e}"
            }

        # Asegurar que la columna "MUNICIPIO" existe
        print(f"Columnas detectadas: {excel_data.columns.tolist()}")
        if self.column_in_source not in excel_data.columns:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": "La columna ('{self.column_in_source}') no está presente en el archivo Excel."
            }

        # Verificar si el valor está presente en la columna "MUNICIPIO"
        valid_values = excel_data[self.column_in_source].astype(str).tolist()
        #print("que hay en la columna municipio?: ",valid_values)
        if self.allow_multiple_languages:
            # Convertir todo a minúsculas para permitir coincidencias más flexibles
            valid_values = [val.lower() for val in valid_values]
            value_to_validate = value_to_validate.lower()

        if value_to_validate not in valid_values:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"El valor '{value_to_validate}' no se encuentra en la columna '{self.column_in_source}'."
            }

        # Si pasa todas las validaciones
        return {
            "status": "success",
            "rule_id": self.id,
            "message": f"El valor '{value_to_validate}' es válido."
        }
