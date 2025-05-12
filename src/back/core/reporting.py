import os
import json
import csv
import shutil
import logging
from datetime import datetime
from pathlib import Path
from config import BASE_DIR, RESULTADOS
from core.epc_dto import EpcDto


RESULTS_DIR = Path(__file__).resolve().parent.parent / Path("resultados")
EXTERNAL_RESUMEN_PATH = RESULTS_DIR / "resumen_errores.csv"
INTERNAL_RESUMEN_DIR = RESULTS_DIR / Path("internal")
INTERNAL_RESUMEN_PATH = INTERNAL_RESUMEN_DIR / "resumen_errores.internal"
REFERENCIA_CATASTRAL_XPATH = "//IdentificacionEdificio/ReferenciaCatastral"

logger = logging.getLogger(__name__)


def _get_referencia_catastral(epc: EpcDto) -> str:
    ref = epc.get_value_by_xpath(REFERENCIA_CATASTRAL_XPATH)
    if not ref:
        raise ValueError("No se pudo obtener la referencia catastral del XML.")
    return ref.strip().replace(" ", "_").replace("/", "_")

def _load_resumen_csv() -> dict:
    resumen = {}
    if not INTERNAL_RESUMEN_PATH.exists() or INTERNAL_RESUMEN_PATH.stat().st_size == 0:
        return resumen

    with open(INTERNAL_RESUMEN_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=';')
        if reader.fieldnames is None or "rule_id" not in reader.fieldnames:
            logger.warning("El CSV interno no tiene cabecera válida.")
            return resumen

        for row in reader:
            rule_id = row["rule_id"]
            resumen[rule_id] = {
                "name": row.get("rule_name", ""),
                "errores": int(row.get("error_count", 0)),
                "referencias": row.get("referencias_con_errores", "").split("|") if row.get("referencias_con_errores") else []
            }

    return resumen

def _save_resumen_csv(resumen: dict):
    INTERNAL_RESUMEN_DIR.mkdir(parents=True, exist_ok=True)

    # Guardar CSV interno de trabajo
    with open(INTERNAL_RESUMEN_PATH, "w", newline='', encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["rule_id", "rule_name", "error_count", "referencias_con_errores"])
        for rule_id, data in resumen.items():
            writer.writerow([
                rule_id,
                data["name"],
                data["errores"],
                "|".join(data["referencias"])
            ])

    # Copiar CSV externo para consulta con Excel
    shutil.copy(INTERNAL_RESUMEN_PATH, EXTERNAL_RESUMEN_PATH)

def guardar_resultado(resultado: dict, epc: EpcDto):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    INTERNAL_RESUMEN_DIR.mkdir(parents=True, exist_ok=True)

    try:
        referencia = _get_referencia_catastral(epc)
    except ValueError as e:
        logger.error(f"Error al obtener la referencia catastral: {e}")
        return
    # ya no usamos fecha para el nombre del archivo. Queremos que sea siempre el mismo y ante nuevas versiones se sobrescriba
    #fecha_tag = datetime.now().strftime("%Y%m%d")
    filename = f"{referencia}.json" #_{fecha_tag}.json"
    file_path = RESULTS_DIR / filename

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    resumen = _load_resumen_csv()

    # Recorremos todas las secciones de reglas
    for section in resultado:
        reglas = resultado.get(section, [])
        if not isinstance(reglas, list):
            continue

        for item in reglas:
            if item.get("status") != "error":
                continue

            rule_id = item.get("rule_id")
            rule_name = item.get("name", rule_id)
            if not rule_id:
                continue

            if rule_id not in resumen:
                resumen[rule_id] = {
                    "name": rule_name,
                    "errores": 0,
                    "referencias": []
                }

            resumen[rule_id]["errores"] += 1
            if referencia not in resumen[rule_id]["referencias"]:
                resumen[rule_id]["referencias"].append(referencia)

    _save_resumen_csv(resumen)