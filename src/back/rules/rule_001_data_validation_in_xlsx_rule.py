from .base_rule import BaseRule, register_rule_class
import pandas as pd
from typing import Dict, Tuple
from unidecode import unidecode
from core.epc_dto import EpcDto

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
        Valida que el valor en el campo especificado por 'xpath' esté en la columna 'column_in_source' del Excel.
        """
        validation_result = {
            "status": "error",
            "rule_id": self.id,
            "message": "",
            "description": self.description,
            "details": {}
        }

        # Leer el valor desde el documento EPC utilizando XPath
        value_to_validate = epc.get_value_by_xpath(self.xpath)
        if value_to_validate is None:
            validation_result["message"] = f"No se encontró valor para el XPath: {self.xpath}"
            return validation_result

        # Leer el archivo Excel
        try:
            excel_data = pd.read_excel(self.valid_values_source)
        except Exception as e:
            validation_result["message"] = f"No se pudo leer el archivo Excel '{self.valid_values_source}': {e}"
            return validation_result

        # Asegurar que la columna "column_in_source" existe
        print(f"Columnas detectadas: {excel_data.columns.tolist()}")
        if self.column_in_source not in excel_data.columns:
            validation_result["message"] = f"La columna ('{self.column_in_source}') no está presente en el archivo Excel."
            return validation_result

        # Verificar si el valor está presente en la columna "column_in_source"
        valid_values = excel_data[self.column_in_source].astype(str).tolist()

        if self.allow_multiple_languages:
            # Convertir todo a minúsculas para permitir coincidencias más flexibles
            valid_values = [unidecode(val.lower()) for val in valid_values]
            value_to_validate = unidecode(value_to_validate.lower())

        if value_to_validate not in valid_values:
            validation_result["details"] = f"El valor '{value_to_validate}' no se encuentra en la columna '{self.column_in_source}'."
            validation_result["message"] = f"El nombre de la población ('{value_to_validate}' ) no figura en la listado de poblaciones de la Comunidad Valenciana que figura en Catastro."
            return validation_result

        # Si pasa todas las validaciones
        validation_result["status"] = "success"
        validation_result["message"] = f"El valor '{value_to_validate}' es válido."
        return validation_result
