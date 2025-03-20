import re
import unicodedata
from .base_rule import BaseRule, register_rule_class
from typing import Dict


def normalize_text(text: str) -> str:
    """
    Normaliza un texto eliminando acentos, espacios extra y caracteres especiales.
    """
    if not text:
        return ""
    
    # Convertir a ASCII eliminando acentos
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
    
    # Convertir a minúsculas
    text = text.lower().strip()
    
    # Remover espacios, saltos de línea y caracteres especiales no alfanuméricos (excepto letras, números y puntos)
    text = re.sub(r'[^a-z0-9.]', '', text)
    
    return text


def normalize_version(version: str) -> str:
    """
    Normaliza una versión eliminando abreviaturas como 'v.', 'ver.', 'ver', etc.
    """
    if not version:
        return ""

    # Convertir a minúsculas y eliminar espacios
    version = version.lower().strip()

    # Remover variantes de "versión"
    version = re.sub(r'\bv(er|er\.|\.|v|v\.)\s*', '', version)
    
    return version


@register_rule_class
class ProcedimientoVersionCheckRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters.get("xpath")
        self.valid_versions = self.parameters.get("valid_versions", {})

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que el procedimiento especificado en el EPC tiene una versión válida.
        """
        validation_result = {
            "status": "error",
            "rule_id": self.id,
            "message": "",
            "description": self.description,
            "details": {}
        }

        # Obtener el valor del procedimiento desde el EPC
        procedimiento_value = epc.get_value_by_xpath(self.xpath)

        if procedimiento_value is None:
            validation_result["message"] = f"No se encontró valor para el XPath: {self.xpath}"
            return validation_result

        # Normalizar el procedimiento recibido
        procedimiento_value_norm = normalize_text(procedimiento_value)

        # Buscar coincidencia con los procedimientos esperados
        procedimiento_name = None
        procedimiento_version = None

        for valid_procedimiento in self.valid_versions.keys():
            valid_procedimiento_norm = normalize_text(valid_procedimiento)

            if valid_procedimiento_norm in procedimiento_value_norm:
                procedimiento_name = valid_procedimiento
                remaining_text = procedimiento_value_norm.replace(valid_procedimiento_norm, "").strip()
                break

        if not procedimiento_name:
            validation_result["message"] = (
                f"El procedimiento '{procedimiento_value}' no está definido en las versiones válidas."
            )
            return validation_result

        # Extraer la versión de la parte restante
        match = re.search(r'(\d+(?:\.\d+)*[a-z]?)$', remaining_text)
        if match:
            procedimiento_version = match.group(1)

        if not procedimiento_version:
            validation_result["message"] = f"No se encontró una versión válida en '{procedimiento_value}'."
            validation_result["details"] = {"provided_procedure": procedimiento_name}
            return validation_result

        # Normalizar versiones para comparación
        procedimiento_version_norm = normalize_version(procedimiento_version)
        expected_version_norm = normalize_version(self.valid_versions[procedimiento_name])

        # Validar si la versión coincide
        if procedimiento_version_norm != expected_version_norm:
            validation_result["message"] = (
                f"La versión '{procedimiento_version}' del procedimiento '{procedimiento_name}' no es válida. "
                f"Se esperaba la versión '{self.valid_versions[procedimiento_name]}'."
            )
            validation_result["details"] = {
                "provided_procedure": procedimiento_name,
                "provided_version": procedimiento_version,
                "expected_version": self.valid_versions[procedimiento_name]
            }
            return validation_result

        # Si pasa todas las validaciones
        validation_result["status"] = "success"
        validation_result["message"] = (
            f"El procedimiento '{procedimiento_name}' con la versión '{procedimiento_version}' es válido."
        )
        validation_result["details"] = {
            "validated_procedure": procedimiento_name,
            "validated_version": procedimiento_version
        }
        return validation_result
