import base64
import re
from io import BytesIO
from PIL import Image
from typing import Dict
from .base_rule import BaseRule, register_rule_class

@register_rule_class
class PlanoImagenBase64EdificioRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_plano = self.parameters.get("xpath_plano")  # XPath para obtener el plano

    def validate(self, epc: "EpcDto") -> Dict:
        """
        Valida que el campo <Plano> en <DatosGeneralesyGeometria> contenga una imagen en formato Base64 válida.
        """
        validation_result = {
            "rule_id": self.id,
            "status": "error",
            "message": "",
            "description": self.description,
            "details": {}
        }

        # Obtener el valor del plano desde el XML/JSON
        plano_value = epc.get_value_by_xpath(self.xpath_plano)

        if not plano_value or plano_value.strip() == "":
            validation_result["message"] = "Debe adjuntarse un plano del edificio en formato Base64."
            validation_result["details"] = {"provided_value": plano_value if plano_value is not None else "None"}
            return validation_result

        # Verificar si el contenido es una imagen en Base64
        if not self._es_imagen_base64(plano_value):
            validation_result["message"] = "El plano no es una imagen válida en formato Base64."
            validation_result["details"] = {"provided_value": plano_value[:30] + "..."}  # Mostrar solo los primeros caracteres para seguridad
            return validation_result

        # Si la validación es exitosa
        validation_result["status"] = "success"
        validation_result["message"] = "El plano del edificio es válido y está correctamente adjunto en formato Base64."
        validation_result["details"] = {"validated_value": "Imagen de plano válida en Base64"}
        return validation_result

    def _es_imagen_base64(self, base64_string: str) -> bool:
        """
        Verifica si una cadena es una imagen válida en formato Base64.
        """
        # Expresión regular para detectar Base64 de imágenes (con o sin prefijo data:image/)
        base64_pattern = r"^data:image\/(png|jpeg|jpg|gif|bmp);base64,(.+)$"
        match = re.match(base64_pattern, base64_string)

        if match:
            base64_data = match.group(2)  # Extraer solo los datos Base64
        else:
            base64_data = base64_string  # Si no tiene prefijo, asumir que es Base64 crudo

        try:
            # Intentar decodificar la imagen
            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data))
            image.verify()  # Verifica si la imagen es válida
            return True
        except Exception:
            return False
