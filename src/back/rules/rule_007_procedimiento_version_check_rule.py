from .base_rule import BaseRule, register_rule_class
from typing import Dict


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
        # Obtener el valor del procedimiento desde el EPC
        procedimiento_value = epc.get_value_by_xpath(self.xpath)

        if procedimiento_value is None:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"No se encontró valor para el XPath: {self.xpath}"
            }

        # Normalizar el valor del procedimiento
        procedimiento_value = procedimiento_value.strip()

        # Buscar el nombre del procedimiento en el valor del EPC
        procedimiento_name = None
        procedimiento_version = None

        for valid_procedimiento in self.valid_versions.keys():
            if procedimiento_value.lower().startswith(valid_procedimiento.lower()):
                procedimiento_name = valid_procedimiento
                remaining_text = procedimiento_value[len(valid_procedimiento):].strip()
                break

        if not procedimiento_name:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"El procedimiento '{procedimiento_value}' no está definido en las versiones válidas."
            }

        # Extraer la versión de la parte restante
        parts = remaining_text.split()
        if parts:
            procedimiento_version = parts[0]

        # Normalizar versiones para comparación
        def normalize_version(version: str) -> str:
            return version.lower().replace("v.", "").replace("v", "").strip()

        procedimiento_version_normalized = normalize_version(procedimiento_version)
        expected_version_normalized = normalize_version(self.valid_versions[procedimiento_name])

        # Validar si la versión coincide
        if procedimiento_version_normalized != expected_version_normalized:
            return {
                "status": "error",
                "rule_id": self.id,
                "message": f"La versión '{procedimiento_version}' del procedimiento '{procedimiento_name}' no es válida. "
                           f"Se esperaba la versión '{self.valid_versions[procedimiento_name]}'."
            }

        # Si pasa todas las validaciones
        return {
            "status": "success",
            "rule_id": self.id,
            "message": f"El procedimiento '{procedimiento_name}' con la versión '{procedimiento_version}' es válido."
        }
