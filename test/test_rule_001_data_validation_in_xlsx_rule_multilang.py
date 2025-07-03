import json
import sys, os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/back'))
sys.path.insert(0, path)

from rules.rule_001_data_validation_in_xlsx_rule_multilang import DataValidationInXlsxRule
from core.epc_dto import EpcDto

# Rutas a los directorios y archivos
DATA_DIR = os.path.join(path,"data")
CACHE_JSON_PATH = os.path.join(path,os.path.join("core","rules_cache.json"))
EPC_FILE_PATH = "D:\\Proyectos\\2024\\MODERATE\\Ficheros\\02_XMLs\\Example_Dwelling.xml" #os.path.join(DATA_DIR, "1 Bloque de viviendas.xml")
EXCEL_FILE_PATH = os.path.join(DATA_DIR, "Listado Poblaciones Zonificación Climática Comunidad Valenciana.xlsx")

# Cargar el archivo EPC
with open(EPC_FILE_PATH, "r", encoding="utf-8") as epc_file:
    epc_content = epc_file.read()

# Crear una instancia de EpcDto
epc = EpcDto(epc_content)

# Cargar las reglas desde el JSON de caché
with open(CACHE_JSON_PATH, "r", encoding="utf-8") as cache_file:
    cache_data = json.load(cache_file)

# Buscar la regla de tipo 'DataValidationInXlsxRule'
rule_data = next(
    (rule for rule in cache_data["rules"]["common_rules"] if rule["class"] == "DataValidationInXlsxRule"),
    None
)

if not rule_data:
    raise ValueError("No se encontró una regla de tipo 'DataValidationInXlsxRule' en el JSON de caché.")

# Ajustar la ruta del archivo Excel en los parámetros de la regla
rule_data["parameters"]["valid_values_source"] = EXCEL_FILE_PATH

# Instanciar la regla
rule = DataValidationInXlsxRule(rule_data)

# Validar el documento EPC
result = rule.validate(epc)

# Imprimir el resultado de manera legible
if isinstance(result, dict):  # Verificar que el resultado es un diccionario
    for key, value in result.items():
        if isinstance(value, dict):  # Si hay diccionarios anidados, imprimirlos también
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  - {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")
else:
    print(result)  # En caso de que la salida no sea un diccionario

# Mostrar los mensajes traducidos si existen
if "messages" in result:
    print("\nMensajes por idioma:")
    for lang, msg in result["messages"].items():
        print(f"  [{lang}]: {msg}")
