import json
import inspect
import os, logging
from os import getenv, listdir, path
from typing import Dict, List, Type
from rules import base_rule
from rules.base_rule import class_registry, register_rule_class, BaseRule
from config import RULES_JASON_PATH, RULES_BASE_PATH, RULES_CACHE_PATH, RULES_CLASS_PATH

import importlib
import pkgutil
import sys

logger = logging.getLogger(__name__)


class RulesFactory:
    _instance = None
    _initialized = False
    _registered_rules = class_registry

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.common_rules: List[base_rule.BaseRule] = []
            self.models: Dict[str, List[base_rule.BaseRule]] = {}
            self.RULES_CLASS_PATH = RULES_CLASS_PATH
            self.RULES_CACHE_JSON = RULES_CACHE_PATH
            self._initialized = True  # Evitamos inicializar más de una vez
            logger.info("Registrando")
            self._register_rule_classes()



    # def _register_rule_classes(self):
    #     """
    #     Importa dinámicamente todos los módulos del paquete 'rules' para registrar las clases.
    #     """
    #     import importlib
    #     import pkgutil

    #     # Nombre del paquete lógico (usado para importaciones)
    #     if self.RULES_CLASS_PATH[0] == "/":
    #         package_name = self.RULES_CLASS_PATH[1:].replace("/", ".")
    #     else:
    #         package_name = self.RULES_CLASS_PATH.replace("/", ".")

    #     # Eliminar 'src.' del package_name si está presente
    #     if package_name.startswith("src."):
    #         package_name = package_name[4:]

    #     logger.debug(f"package_name: {package_name}")

    #     # Ruta física al directorio del paquete
    #     package_path = self.RULES_CLASS_PATH
    #     logger.debug(f"Package_path en register_rule_classes: {package_path}")

    #     for _, module_name, _ in pkgutil.iter_modules([package_path]):
    #         module_full_name = f"{package_name}.{module_name}"
    #         logger.debug(f"importando módulo: {module_full_name}")
    #         print ("importando módulo: ", module_full_name)
    #         importlib.import_module(module_full_name)

    #     # Verifica que las clases estén registradas
    #     logger.info("clases registradas en class_registry:")
    #     for name, cls in class_registry.items():
    #         logger.debug(f"- {name}: {cls}")


    # def _register_rule_classes(self):
    #     """
    #     Importa dinámicamente todos los módulos del paquete 'rules' para registrar las clases.
    #     """
    #     package_path = self.RULES_CLASS_PATH  # Ruta absoluta al directorio de reglas

    #     if not os.path.exists(package_path):
    #         raise FileNotFoundError(f"No se encontró la ruta del paquete de reglas: {package_path}")

    #     # Asegurar que la ruta esté en sys.path
    #     if package_path not in sys.path:
    #         sys.path.append(package_path)

    #     # Convertir la ruta en un nombre de paquete Python
    #     package_name = os.path.relpath(package_path, start=os.getcwd()).replace(os.sep, ".")

    #     # Si el paquete está dentro de 'src', ajustarlo
    #     if package_name.startswith("src."):
    #         package_name = package_name[4:]

    #     logger.debug(f"package_name: {package_name}")
    #     logger.debug(f"Package_path en register_rule_classes: {package_path}")

    #     # Importar dinámicamente los módulos dentro de rules/
    #     for _, module_name, _ in pkgutil.iter_modules([package_path]):
    #         module_full_name = f"{package_name}.{module_name}"
    #         logger.debug(f"Importando módulo: {module_full_name}")

    #         try:
    #             importlib.import_module(module_full_name)
    #         except ModuleNotFoundError as e:
    #             logger.error(f"Error al importar {module_full_name}: {e}")
    #             continue

    #     # Verificar que las clases estén registradas
    #     logger.info("Clases registradas en class_registry:")
    #     for name, cls in class_registry.items():
    #         logger.debug(f"- {name}: {cls}")



    def _register_rule_classes(self):
        """
        Importa dinámicamente todos los módulos del paquete 'rules' para registrar las clases.
        """
        package_path = self.RULES_CLASS_PATH  # Ruta absoluta al directorio de reglas

        if not os.path.exists(package_path):
            raise FileNotFoundError(f"No se encontró la ruta del paquete de reglas: {package_path}")

        # Asegurar que la ruta está en sys.path para permitir importaciones
        if package_path not in sys.path:
            sys.path.append(os.path.dirname(package_path))  # Añadir la carpeta "src" sin incluir "rules"

        # Obtener el nombre del paquete sin incluir "src"
        base_dir = os.path.dirname(self.RULES_CLASS_PATH)  # Obtiene la ruta de "src"
        package_name = os.path.relpath(package_path, start=base_dir).replace(os.sep, ".")

        logger.debug(f"package_name: {package_name}")
        logger.debug(f"Package_path en register_rule_classes: {package_path}")

        # Importar dinámicamente los módulos dentro de rules/
        for _, module_name, _ in pkgutil.iter_modules([package_path]):
            module_full_name = f"{package_name}.{module_name}"
            logger.debug(f"Importando módulo: {module_full_name}")

            try:
                importlib.import_module(module_full_name)
            except ModuleNotFoundError as e:
                logger.error(f"Error al importar {module_full_name}: {e}")
                continue

        # Verificar que las clases estén registradas
        logger.info("Clases registradas en class_registry:")
        for name, cls in class_registry.items():
            logger.debug(f"- {name}: {cls}")
                            

    # def load_rules(self) -> None:
    #     """Carga reglas comunes y específicas de modelos desde el archivo ensamblado."""
    #     with open(self.RULES_PATH, 'r', encoding='utf-8') as file:
    #         data = json.load(file)

    #         # Cargar common_rules
    #         self.common_rules = [
    #             self._create_rule(rule_data, data["rule_types"]) for rule_data in data.get("common_rules", [])
    #         ]

    #         # Cargar model_rules
    #         self.models = {}
    #         for rule_data in data.get("model_rules", []):
    #             model_name = rule_data.get("model", "default_model")
    #             if model_name not in self.models:
    #                 self.models[model_name] = []
    #             self.models[model_name].append(self._create_rule(rule_data, data["rule_types"]))


    def load_rules(self) -> None:
        """
        Carga reglas comunes y específicas de modelos desde un archivo JSON.
        """
        self.common_rules = []
        self.models = {}

        # Leer el archivo JSON completo
        with open(self.RULES_CACHE_JSON, 'r', encoding='utf-8') as file:
            data = json.load(file)
            rules = data.get("rules", {})

            # Cargar common_rules
            for rule_data in rules.get("common_rules", []):
                self.common_rules.append(self._create_rule(rule_data))

            # Cargar model_rules
            for rule_data in rules.get("model_rules", []):
                model_name = rule_data.get("model", "default_model")
                if model_name not in self.models:
                    self.models[model_name] = []
                self.models[model_name].append(self._create_rule(rule_data))


    def _create_rule(self, rule_data: Dict) -> base_rule.BaseRule:
        """
        Crea una instancia de regla basada en el campo 'class' del JSON.
        """
        rule_class_name = rule_data.get("class")
        rule_class = self._registered_rules.get(rule_class_name)

        if not rule_class:
            raise ValueError(f"Clase de regla desconocida: {rule_class_name}")
        
        # Crear una instancia de la clase pasando los datos del JSON
        return rule_class(rule_data)


    # def _create_rule(self, rule_data: Dict) -> base_rule.BaseRule:
    #     """
    #     Crea una instancia de regla basada en el tipo dinámicamente.
    #     """
    #     rule_type = rule_data.get("type")
    #     rule_class = self._registered_rules.get(rule_type)
    #     if not rule_class:
    #         raise ValueError(f"Tipo de regla desconocido: {rule_type}")
    #     return rule_class(rule_data)

    def get_rules_for_model(self, x: int) -> List[base_rule.BaseRule]:
        """
        Obtiene las reglas específicas para un modelo según su ID.
        """
        model_name = self.determine_model(x)
        return self.models.get(model_name, [])

    def determine_model(self, x: int) -> str:
        """
        Determina el nombre del modelo basado en el identificador.
        """
        # TODO implementar la lógica para determinar el modelo
        return "model1"


    def apply_rules(self, epc: "EpcDto", questions) -> Dict:
        """
        Aplica las reglas cargadas al documento EPC.

        Args:
            epc (EpcDto): Objeto que representa el documento a validar.

        Returns:
            Dict: Resultados de las validaciones organizados por regla.
        """
        validation_results = {
            "common_rules": [],
            "model_rules": {}
        }

        # Aplicar reglas comunes
        for rule in self.common_rules:
            result = rule.validate(epc, questions[rule.id])
            validation_results["common_rules"].append({
                "rule_id": rule.id,
                "status": result.get("status"),
                "message": result.get("message", ""),
                "description": result.get("description"),
                "details": result.get("details", {}),  # Información adicional si está disponible
                "severity": result.get("severity")
            })

        # Aplicar reglas específicas de modelos
        for model_name, rules in self.models.items():
            model_results = []
            for rule in rules:
                result = rule.validate(epc,questions[rule.id])
                model_results.append({
                    "rule_id": rule.id,
                    "status": result.get("status"),
                    "message": result.get("message", ""),
                    "description": result.get("description"),
                    "details": result.get("details", {}),  # Información adicional si está disponible
                    "severity": result.get("severity")
                })
            validation_results["model_rules"][model_name] = model_results

        return validation_results
    



    #comprobar todas las reglas y aquellas que tengan campo question, se añaden a la lista de preguntas
    def get_questions(self, epc) -> Dict[str,Dict[str, str]]:
        """
        Obtiene las preguntas que deben hacerse al usuario basadas en las reglas cargadas.

        Args:
            epc (EpcDto): Objeto que representa el documento a validar.

        Returns:
            List[str]: Lista de preguntas a realizar al usuario.
        """
        questions = {}
    
        for rule in self.common_rules:
            logger.debug(f"Comprobando regla común: {rule.id}")

            auxiliame = rule.get_question(epc)
            logger.debug(f"Pregunta obtenida: {auxiliame}")

            if auxiliame is not None:
                rule_id, preguntas = auxiliame

                for pregunta_id, contenido in preguntas.items():
                    questions.setdefault(pregunta_id, {})
                    questions[pregunta_id]["text"] = contenido["text"]
                    questions[pregunta_id]["type"] = contenido["type"]



        # Comprobar reglas específicas de modelos
        for model_name, rules in self.models.items():
            logger.debug(f"Comprobando regla común: {rule.id}")

            # Llamar a la función get_question de la regla
            auxiliame = rule.get_question(epc)
            logger.debug(f"Pregunta obtenida: {auxiliame}")

            if auxiliame is not None:
                rule_id, preguntas = auxiliame

                for pregunta_id, contenido in preguntas.items():
                    questions.setdefault(pregunta_id, {})
                    questions[pregunta_id]["text"] = contenido["text"]
                    questions[pregunta_id]["type"] = contenido["type"]


        # Al final, si 'questions' está vacío, devolvemos None
        if not questions:
            return None
        
        return questions
