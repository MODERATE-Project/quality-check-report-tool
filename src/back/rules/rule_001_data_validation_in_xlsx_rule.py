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


        # Para ignorar tildes y mayúsculas en el valor a validar
        normalized_value_to_validate = unidecode(value_to_validate.lower().strip())

        # Leer el archivo Excel
        try:
            excel_data = pd.read_excel(self.valid_values_source)
        except Exception as e:
            validation_result["message"] = f"No se pudo leer el archivo Excel '{self.valid_values_source}': {e}"
            return validation_result

        # Asegurar que la columna "column_in_source" existe
        print(f"Columnas detectadas: {excel_data.columns.tolist()}")
        if self.column_in_source not in excel_data.columns:
            validation_result["message"] = (
                f"La columna ('{self.column_in_source}') no está presente en el archivo Excel."
            )
            return validation_result

        # Lista con todos los valores de la columna (convertidos a str)
        valid_values = excel_data[self.column_in_source].astype(str).tolist()

        # Para cada elemento de la columna, separamos por '/', normalizamos (lower, unidecode) y
        # verificamos si 'normalized_value_to_validate' está presente en alguno de los "sinónimos".
        valor_encontrado = False
        for val in valid_values:
            # Si la columna contiene varios valores separados por '/', los separamos en una lista
            posibles_valores = [unidecode(x.lower().strip()) for x in val.split("/")]
            if normalized_value_to_validate in posibles_valores:
                valor_encontrado = True
                break

        if not valor_encontrado:
            validation_result["details"] = (
                f"El valor '{value_to_validate}' no se encuentra en la columna "
                f"'{self.column_in_source}' (teniendo en cuenta variaciones por idioma)."
            )
            validation_result["message"] = (
                f"El nombre de la población ('{value_to_validate}') no figura en la lista "
                f"de poblaciones válidas para la Comunidad Valenciana."
            )
            return validation_result

        # Si pasa todas las validaciones
        validation_result["status"] = "success"
        validation_result["message"] = f"El valor '{value_to_validate}' es válido."
        return validation_result