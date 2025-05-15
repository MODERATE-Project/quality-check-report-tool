#!/bin/bash

# Ruta base de los locales
I18N_PATH="./src/front/src/locales"

# Verificar si la carpeta de i18n existe
if [ ! -d "$I18N_PATH" ]; then
  echo "La carpeta de i18n no existe en la ruta: $I18N_PATH"
  exit 1
fi

# Solicitar el nombre del nuevo campo
read -p "Introduce el nombre del nuevo campo: " FIELD_NAME

# Crear un diccionario para almacenar las traducciones
declare -A TRANSLATIONS

# Paso 1: Recopilar las traducciones para cada idioma
for FOLDER in "$I18N_PATH"/*; do
  if [ -d "$FOLDER" ]; then
    # Obtener el idioma (nombre de la carpeta)
    LANG=$(basename "$FOLDER")

    # Solicitar la traducción para este idioma
    read -p "Introduce el texto para '$LANG' ($FIELD_NAME): " TRANSLATION

    # Guardar la traducción en el diccionario
    TRANSLATIONS["$LANG"]="$TRANSLATION"
  fi
done

# Paso 2: Escribir las traducciones en los archivos
for FOLDER in "$I18N_PATH"/*; do
  if [ -d "$FOLDER" ]; then
    # Ruta al archivo common.json dentro de la subcarpeta
    COMMON_FILE="$FOLDER/common.json"

    # Verificar si el archivo common.json existe
    if [ ! -f "$COMMON_FILE" ]; then
      echo "El archivo common.json no existe en la carpeta: $FOLDER"
      continue
    fi

    # Leer el contenido del archivo JSON
    CONTENT=$(cat "$COMMON_FILE")

    # Añadir el nuevo campo con la traducción correspondiente
    LANG=$(basename "$FOLDER")
    TRANSLATION=${TRANSLATIONS["$LANG"]}
    UPDATED_CONTENT=$(echo "$CONTENT" | jq --arg key "$FIELD_NAME" --arg value "$TRANSLATION" '. + {($key): $value}')

    # Guardar el archivo actualizado
    echo "$UPDATED_CONTENT" > "$COMMON_FILE"
    echo "Actualizado: $COMMON_FILE"
  fi
done

echo "¡Todos los archivos de i18n han sido actualizados!"