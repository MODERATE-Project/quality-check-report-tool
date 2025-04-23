import base64
import re
from io import BytesIO
from PIL import Image
from typing import Dict
from .base_rule import BaseRule, register_rule_class

@register_rule_class
class ImagenBase64EdificioRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_plano = self.parameters.get("xpath_plano")
        self.valid_extensions = self.parameters.get("valid_extensions", [".jpg", ".jpeg", ".png"])
        self.max_width = self.parameters.get("max_width", 800)
        self.max_height = self.parameters.get("max_height", 600)

    def validate(self, epc: "EpcDto") -> Dict:
        validation_result = self._new_result()  # por defecto status="error"

        plano_value = epc.get_value_by_xpath(self.xpath_plano)

        if not plano_value or plano_value.strip() == "":
            validation_result["message"] = "Debe adjuntarse un plano del edificio en formato Base64."
            validation_result["details"] = {"provided_value": plano_value if plano_value is not None else "None"}
            return validation_result

        image_info = self._validar_imagen(plano_value)

        if not image_info["es_valida"]:
            validation_result["message"] = image_info["error"]
            validation_result["details"] = image_info["detalles"]
            return validation_result

        validation_result["status"] = "success"
        validation_result["message"] = "El plano del edificio es válido y está correctamente adjunto en formato Base64, con extensión y dimensiones correctas."
        validation_result["details"] = image_info["detalles"]
        return validation_result

    def _validar_imagen(self, base64_string: str) -> Dict:
        base64_pattern = r"^data:image\/(png|jpeg|jpg);base64,(.+)$"
        match = re.match(base64_pattern, base64_string)

        formato_detectado = None
        if match:
            formato_detectado = match.group(1)
            base64_data = match.group(2)
        else:
            base64_data = base64_string

        try:
            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data))
            image.verify()

            # Volver a abrir para comprobar dimensiones
            image = Image.open(BytesIO(image_data))
            width, height = image.size

            if width > self.max_width or height > self.max_height:
                return {
                    "es_valida": False,
                    "error": f"Las dimensiones de la imagen exceden el máximo permitido ({self.max_width}x{self.max_height}).",
                    "detalles": {"ancho": width, "alto": height}
                }

            extension_valida = False
            if formato_detectado:
                extension_valida = f".{formato_detectado}" in self.valid_extensions

            if not extension_valida:
                return {
                    "es_valida": False,
                    "error": f"La extensión de la imagen no es válida. Se permiten: {', '.join(self.valid_extensions)}.",
                    "detalles": {"formato_detectado": formato_detectado or "desconocido"}
                }

            return {
                "es_valida": True,
                "detalles": {"ancho": width, "alto": height, "formato": formato_detectado or "desconocido"}
            }

        except Exception as e:
            return {
                "es_valida": False,
                "error": "La imagen proporcionada no es válida o está dañada.",
                "detalles": {"error": str(e)}
            }
