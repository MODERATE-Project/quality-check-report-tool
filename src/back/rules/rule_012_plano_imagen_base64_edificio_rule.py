# plano_imagen_base64_edificio_rule.py
import base64
import re
import unicodedata
from io import BytesIO
from typing import Dict, List, Tuple

from PIL import Image
from .base_rule import BaseRule, register_rule_class


# ───────────────────────── utilidades ─────────────────────────
def _normalize_ext(ext: str) -> str:
    """
    Normaliza una extensión: '.JPG' → '.jpg', 'jpeg' → '.jpeg'.
    Añade el punto inicial si falta.
    """
    if not ext:
        return ""
    ext = unicodedata.normalize("NFKD", ext).lower().strip()
    if not ext.startswith("."):
        ext = "." + ext
    return ext


def _decode_base64_image(b64_str: str) -> Tuple[bool, Dict]:
    """
    Intenta decodificar una cadena Base64 que represente una imagen.

    Retorna:
        (True,  {'image': PIL.Image, 'ext': '.png'}) si es válida
        (False, {'message': str, 'details': {...}})  si no lo es
    """
    # data:image/png;base64,.....
    m = re.match(r"^data:image/([a-z0-9.+-]+);base64,(.+)$", b64_str, re.I)
    mime_ext = None
    b64_data = b64_str
    if m:
        mime_ext = _normalize_ext(m.group(1).split("+")[0])  # 'jpeg' -> '.jpeg'
        b64_data = m.group(2)

    try:
        img_bytes = base64.b64decode(b64_data, validate=True)
        img = Image.open(BytesIO(img_bytes))
        img.verify()                     # comprueba integridad
        img = Image.open(BytesIO(img_bytes))  # re-abrir para acceder a size/format
    except Exception:
        return False, {
            "message": "El plano no es una imagen válida en formato Base64.",
            "details": {"provided_value": b64_str[:40] + "..."}
        }

    ext = mime_ext or _normalize_ext(img.format.lower() if img.format else "")
    return True, {"image": img, "ext": ext}


# ───────────────────────── regla ──────────────────────────────
@register_rule_class
class PlanoImagenBase64EdificioRule(BaseRule):
    """
    Comprueba que el campo <Plano> contenga una imagen Base64:
      • extensión entre las permitidas
      • tamaño (ancho/alto) <= límites configurados
    """

    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)

        self.xpath_plano: str = self.parameters["xpath_plano"]
        self.valid_exts: List[str] = [
            _normalize_ext(e) for e in self.parameters.get("valid_extensions", [])
        ]

        # límites máximos (defecto 800×600 si no se indican)
        self.max_w: int = int(self.parameters.get("max_width", 800))
        self.max_h: int = int(self.parameters.get("max_height", 600))

    # ------------------------------------------------------------------
    def validate(self, epc: "EpcDto") -> Dict:
        result = self._new_result()  # por defecto status="error"

        plano_raw = epc.get_value_by_xpath(self.xpath_plano)
        if not plano_raw or plano_raw.strip() == "":
            result["message"] = "Debe adjuntarse un plano del edificio en formato Base64."
            return result

        ok, info = _decode_base64_image(plano_raw)
        if not ok:
            result.update(info)
            return result     # info ya contiene message / details

        img: Image.Image = info["image"]
        ext: str = info["ext"]

        if ext not in self.valid_exts:
            result.update({
                "message": (f"La extensión '{ext}' no es válida. "
                            f"Las permitidas son: {', '.join(self.valid_exts)}."),
                "details": {"provided_extension": ext}
            })
            return result

        if img.width > self.max_w or img.height > self.max_h:
            result.update({
                "message": (f"El plano supera el tamaño máximo permitido "
                            f"({self.max_w}×{self.max_h} px). "
                            f"Se ha proporcionado una imagen de {img.width}×{img.height} px."),
                "details": {"width": img.width, "height": img.height,
                            "limit_width": self.max_w, "limit_height": self.max_h,
                            "extension": ext}
            })
            return result

        # —— Todo correcto ——
        result.update({
            "status":  "success",
            "message": "El plano del edificio es válido y está correctamente adjunto en formato Base64.",
            "details": {"width": img.width, "height": img.height, "extension": ext}
        })
        return result
