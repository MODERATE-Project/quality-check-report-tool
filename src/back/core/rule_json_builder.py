import os, logging
import json
import hashlib
from typing import Dict, List
from config import RULES_JASON_PATH, RULES_BASE_PATH, RULES_CACHE_PATH

logger = logging.getLogger(__name__)


class RuleJsonBuilder:
    def __init__(self, rule_directory: str = "rules_json", base_file: str = "rules_base.json", cache_file: str = "rules_cache.json"):
        """
        Inicializa el RuleBuilder.

        :param rule_directory: Directorio donde están los JSONs individuales de reglas.
        :param base_file: Archivo JSON que contiene la base de las reglas.
        :param cache_file: Archivo cacheado con las reglas ensambladas.
        """
        self.rule_directory = RULES_JASON_PATH
        self.base_file = RULES_BASE_PATH
        self.cache_file = RULES_CACHE_PATH


    def _calculate_directory_hash(self) -> str:
        """
        Calcula un hash único basado en el contenido de los archivos del directorio de reglas y la base.
        """
        hash_md5 = hashlib.md5()

        # Incluir el contenido de la base de reglas
        with open(self.base_file, 'rb') as f:
            while chunk := f.read(4096):
                hash_md5.update(chunk)

        # Incluir el contenido de las reglas individuales (excluyendo el archivo de caché)
        for file in sorted(os.listdir(self.rule_directory)):
            if file.endswith(".json") and file != os.path.basename(self.cache_file):
                with open(os.path.join(self.rule_directory, file), 'rb') as f:
                    while chunk := f.read(4096):
                        hash_md5.update(chunk)

        return hash_md5.hexdigest()

    def _load_cache(self) -> Dict:
        """
        Carga el archivo de caché si existe.
        """
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_cache(self, cache_data: Dict):
        """
        Guarda el archivo cacheado con las reglas ensambladas.
        """
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=4, ensure_ascii=False)

    def build_rules(self) -> Dict:
        """
        Construye el fichero de reglas ensambladas si hay cambios en las reglas individuales.
        """
        current_hash = self._calculate_directory_hash()
        cache_data = self._load_cache()

        # Si no hay cambios, devuelve el caché existente
        if cache_data.get("hash") == current_hash:
            logger.info("No hay cambios en las reglas. Usando caché.")
            return cache_data["rules"]

        # Leer y ensamblar reglas
        logger.info("Cambios detectados en las reglas. Reconstruyendo.")
        rules = self._assemble_rules()

        # Guardar en caché
        self._save_cache({"hash": current_hash, "rules": rules})
        return rules

    # def _assemble_rules(self) -> Dict:
    #     """
    #     Ensambla todas las reglas individuales con la base de reglas en un único diccionario.
    #     """
    #     # Leer la base de reglas
    #     with open(self.base_file, 'r', encoding='utf-8') as f:
    #         base_rules = json.load(f)

    #     # Diccionario para ensamblar reglas
    #     assembled_rules = {"rule_types": base_rules["rule_types"], "common_rules": [], "model_rules": []}

    #     # Leer reglas individuales
    #     for file in os.listdir(self.rule_directory):
    #         if file.endswith(".json"):
    #             logger.debug(f"Json a cargar: {file}")
    #             rule_path = os.path.join(self.rule_directory, file)
    #             with open(rule_path, 'r', encoding='utf-8') as f:
    #                 rule_data = json.load(f)

    #                 # Clasificar según categoría
    #                 category = rule_data.get("category")
    #                 if category == "common_rules":
    #                     assembled_rules["common_rules"].append(rule_data)
    #                 elif category == "model_rules":
    #                     assembled_rules["model_rules"].append(rule_data)
    #                 else:
    #                     raise ValueError(f"Categoría desconocida en el archivo {file}: {category}")

    #     return assembled_rules

    def _assemble_rules(self) -> Dict:
        """
        Ensambla todas las reglas individuales con la base de reglas en un único diccionario.
        """
        # Leer la base de reglas
        with open(self.base_file, 'r', encoding='utf-8') as f:
            base_rules = json.load(f)

        # Diccionario para ensamblar reglas
        assembled_rules = {"rule_types": base_rules["rule_types"], "common_rules": [], "model_rules": []}

        # Conjuntos para evitar duplicados
        common_rule_ids = set()
        model_rule_ids = set()

        # Leer reglas individuales
        for file in os.listdir(self.rule_directory):
            if file.endswith(".json"):
                logger.debug(f"Json a cargar: {file}")
                rule_path = os.path.join(self.rule_directory, file)
                with open(rule_path, 'r', encoding='utf-8') as f:
                    rule_data = json.load(f)

                    # Clasificar según categoría
                    category = rule_data.get("category")
                    rule_id = rule_data.get("id")

                    if category == "common_rules":
                        if rule_id not in common_rule_ids:
                            assembled_rules["common_rules"].append(rule_data)
                            common_rule_ids.add(rule_id)
                    elif category == "model_rules":
                        if rule_id not in model_rule_ids:
                            assembled_rules["model_rules"].append(rule_data)
                            model_rule_ids.add(rule_id)
                    else:
                        raise ValueError(f"Categoría desconocida en el archivo {file}: {category}")

        return assembled_rules


