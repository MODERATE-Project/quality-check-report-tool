import os
import logging
from pathlib import Path

# Rutas base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTADOS = Path("/src")

# Rutas comunes
RULES_CLASS_PATH = os.path.join(BASE_DIR, "rules")  # Ruta al directorio de reglas
RULES_BASE_PATH = os.path.join(BASE_DIR, "core", "rules_base.json")  # Archivo base de reglas
RULES_JASON_PATH= os.path.join(BASE_DIR, "rules_json")  # Archivo base de reglas
RULES_CACHE_PATH = os.path.join(BASE_DIR, "core", "rules_cache.json")  # Archivo de caché de reglas

# Otros parámetros globales pueden agregarse aquí
LOG_LEVEL = logging.DEBUG  # Nivel de logging global
