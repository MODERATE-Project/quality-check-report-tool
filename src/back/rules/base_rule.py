from typing import Dict, Any, Tuple, Type
from core.epc_dto import EpcDto

# ───────────────────────── registro dinámico ──────────────────────────
class_registry: Dict[str, Type] = {}

def register_rule_class(cls: Type):
    """Decorador para registrar automáticamente las subclases de BaseRule."""
    class_registry[cls.__name__] = cls
    return cls


@register_rule_class
class BaseRule:
    """Clase base de la que heredan todas las reglas de validación."""

    def __init__(self, rule_data: Dict):
        self.id: str = rule_data.get("id")
        self.type: str = rule_data.get("type")
        self.parameters: Dict = rule_data.get("parameters", {})
        self.description: str = rule_data.get("description")
        self.name: str = rule_data.get("name")
        self.severity: str = rule_data.get("severity")  # "Error", "Warning", etc.

    # ───────────────────────── helpers comunes ─────────────────────────
    def _new_result(self, status: str = "error") -> Dict[str, Any]:
        """Devuelve un diccionario estándar para el resultado de la regla."""
        return {
            "rule_id":     self.id,
            "status":      status,      # "error" o "success"
            "messages":     {},
            "description": self.description,
            "details":     {},
            "severity":    self.severity,
            "name"  :     self.name,
            "type":       self.type
        }

    # ───────────────────────── interfaces a implementar ─────────────────
    def validate(self, epc: "EpcDto", questions=None) -> Dict:
        """Cada subclase debe implementar su lógica de validación."""
        raise NotImplementedError

    def get_question(self, epc: "EpcDto") -> Tuple[str, Dict[str, Dict[str, str]]]:
        """Por defecto no hay preguntas para el usuario."""
        return None

    def _get_translated_message(self, key: str, lang: str = "es", **kwargs) -> str:
        try:
            template = self.parameters.get("messages", {}).get(key, {}).get(lang)
            return template.format(**kwargs) if template else ""
        except Exception:
            return ""
