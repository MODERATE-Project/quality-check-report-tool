param (
    [string]$i18nPath = "./src/front/src/locales"
)

# Verificar si la carpeta de i18n existe
if (-Not (Test-Path -Path $i18nPath)) {
    Write-Host "La carpeta de i18n no existe en la ruta: $i18nPath"
    exit 1
}

# Solicitar el nombre del nuevo campo
$fieldName = Read-Host "Introduce el nombre del nuevo campo"

# Obtener todas las subcarpetas (locales) dentro de la carpeta de i18n
$localeFolders = Get-ChildItem -Path $i18nPath -Directory

foreach ($folder in $localeFolders) {
    # Ruta al archivo common.json dentro de la subcarpeta
    $commonFilePath = Join-Path -Path $folder.FullName -ChildPath "common.json"

    # Verificar si el archivo common.json existe
    if (-Not (Test-Path -Path $commonFilePath)) {
        Write-Host "El archivo common.json no existe en la carpeta: $folder.FullName"
        continue
    }

    # Leer el contenido del archivo JSON
    $content = Get-Content -Path $commonFilePath | ConvertFrom-Json

    # Obtener el idioma del archivo (nombre de la carpeta)
    $lang = $folder.BaseName

    # Solicitar la traducción para este idioma
    $translation = Read-Host "Introduce el texto para '$lang' ($fieldName)"

    # Añadir el nuevo campo
    $content | Add-Member -MemberType NoteProperty -Name $fieldName -Value $translation -Force

    # Guardar el archivo actualizado
    $content | ConvertTo-Json -Depth 10 | Set-Content -Path $commonFilePath -Encoding UTF8
    Write-Host "Actualizado: $commonFilePath"
}

Write-Host "Todos los archivos de i18n han sido actualizados"