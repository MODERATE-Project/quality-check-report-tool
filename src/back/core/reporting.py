import os
import json
from datetime import datetime
from pathlib import Path
from config import BASE_DIR
import logging

RESULTS_DIR = Path(__file__).resolve().parent.parent / Path("resultados")
RESUMEN_PATH = RESULTS_DIR / "resumen_errores.json"

logger = logging.getLogger(__name__)

def _load_resumen():
    if RESUMEN_PATH.exists():
        with open(RESUMEN_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"contador_registros": 0, "reglas": {}}

def _save_resumen(data):
    with open(RESUMEN_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def guardar_resultado(resultado: dict):
    now = datetime.now()
    resumen = _load_resumen()
    resumen["contador_registros"] += 1
    current_id = resumen["contador_registros"]

    logger.debug("Guardando resultado con ID: %s", current_id)
    logger.debug("Resultado: %s", resultado)
    # Crear estructura de directorios año/mes/día
    dir_path = RESULTS_DIR / now.strftime("%Y") / now.strftime("%m") / now.strftime("%d")
    logger.debug("Directorio de resultados: %s", dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    logger.debug("Directorio creado: %s", dir_path)
    # Guardar el resultado con nombre identificador_timestamp.json
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    filename = f"{current_id:03d}_{timestamp}.json"
    logger.debug("Nombre del archivo: %s", filename)
    file_path = dir_path / filename
    logger.debug("Ruta del archivo: %s", file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    logger
    # Actualizar resumen por regla
    for item in resultado.get("errors", []):
        rule_id = item.get("id")
        rule_name = item.get("name", rule_id)
        if not rule_id:
            continue

        if rule_id not in resumen["reglas"]:
            resumen["reglas"][rule_id] = {
                "name": rule_name,
                "errores": 0,
                "ids": []
            }
        resumen["reglas"][rule_id]["errores"] += 1
        resumen["reglas"][rule_id]["ids"].append(current_id)
    logger.debug("Resumen actualizado: %s", resumen)
    # Guardar el resumen actualizado
    _save_resumen(resumen)
