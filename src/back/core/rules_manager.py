from os import getenv
import json
class RuleManager:
    _instance = None
    _initialized = False

    RULES_PATH = ''

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # Atributos internos
            self.common_rules = []
            self.models = {}
            self.RULES_PATH = getenv('RULES_PATH', 'core/rules_repository.json')
            self._initialized = True  # Evitamos inicializar más de una vez

    def load_rules(self) -> None:
        """Carga reglas comunes y específicas de modelos desde un archivo JSON."""
        with open(self.RULES_PATH, 'r') as file:
            data = json.load(file)
            self.common_rules = data.get("common_rules", [])
            self.models = data.get("models", {})
    
    def get_rules_for_model(self, x: int) -> dict:
        """
        Obtiene las reglas específicas para un modelo según su ID.
        """
        model_name = self.determine_model(x)
        return self.models.get(model_name, {})
    
    def determine_model(self, x: int) -> str:
        """
        Determina el nombre del modelo basado en el identificador.
        """
        # TODO implementar la lógica para determinar el modelo
        pass