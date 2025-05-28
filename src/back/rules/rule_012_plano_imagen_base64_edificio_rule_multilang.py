import base64
import re
import unicodedata
from io import BytesIO
from typing import Dict, List, Tuple

from PIL import Image
from .base_rule import BaseRule, register_rule_class


# ───────────────────────── utilidades ─────────────────────────
def _normalize_ext(ext: str) -> str:
    if not ext:
        return ""
    ext = unicodedata.normalize("NFKD", ext).lower().strip()
    if not ext.startswith("."):
        ext = "." + ext
    return ext


def _decode_base64_image(b64_str: str) -> Tuple[bool, Dict]:
    """
    Intenta decodificar una cadena Base64 que representa una imagen.
    Soporta tanto cadenas con encabezado MIME (data:image/png;base64,...) como sin él.

    Returns:
        - (True, {"image": PIL.Image, "ext": str}) si la imagen es válida
        - (False, {"message": str, "details": dict}) si la imagen es inválida o está dañada
    """
    mime_ext = ""
    
    # Intentamos extraer el MIME si está presente
    m = re.match(r"^data:image/([a-z0-9.+-]+);base64,(.+)$", b64_str, re.I)
    if m:
        mime_ext = _normalize_ext(m.group(1).split("+")[0])
        b64_data = m.group(2)
    else:
        b64_data = b64_str

    # Eliminar espacios, saltos de línea y tabulaciones
    b64_clean = re.sub(r"\s+", "", b64_data)

    try:
        # Decodificamos la cadena base64
        img_bytes = base64.b64decode(b64_clean, validate=True)

        # Verificamos que es una imagen válida
        with BytesIO(img_bytes) as bio:
            img = Image.open(bio)
            img.verify()  # Verifica estructura sin cargarla completamente

        # Reabrimos la imagen para trabajar con ella
        img = Image.open(BytesIO(img_bytes))
    except Exception as e:
        return False, {
            "message": "La imagen no es válida o está dañada.",
            "details": {
                "error": str(e),
                "sample": b64_str[:40] + "..."  # muestra para depuración
            }
        }

    # Determinar extensión
    ext = mime_ext or _normalize_ext(img.format.lower() if img.format else "")
    return True, {"image": img, "ext": ext}



# ───────────────────────── regla ──────────────────────────────
@register_rule_class
class PlanoImagenBase64EdificioRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath_plano: str = self.parameters["xpath_plano"]
        self.valid_exts: List[str] = [_normalize_ext(e) for e in self.parameters.get("valid_extensions", [])]
        self.max_w: int = int(self.parameters.get("max_width", 800))
        self.max_h: int = int(self.parameters.get("max_height", 600))

    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        messages = self.parameters.get("messages", {}).get(key, {})
        return {lang: tpl.format(**kwargs) for lang, tpl in messages.items()}

    def _get_translated_details(self, key: str, **kwargs) -> dict:
        template = self.parameters.get("details", {}).get(key, {})
        return {
            lang: {k: v.format(**kwargs) for k, v in detail.items()}
            for lang, detail in template.items()
        }

    def validate(self, epc: "EpcDto") -> Dict:
        result = self._new_result()

        plano_raw = epc.get_value_by_xpath(self.xpath_plano)
        if not plano_raw or plano_raw.strip() == "":
            result["messages"] = self._get_translated_messages("missing")
            result["details"] = self._get_translated_details("missing")
            return result

        ok, info = _decode_base64_image(plano_raw)
        if not ok:
            result["messages"] = self._get_translated_messages("invalid_base64")
            result["details"] = self._get_translated_details("invalid_base64", muestra=plano_raw[:40] + "...")
            return result

        img: Image.Image = info["image"]
        ext: str = info["ext"]

        if ext not in self.valid_exts:
            result["messages"] = self._get_translated_messages("invalid_ext", ext=ext, valids=", ".join(self.valid_exts))
            result["details"] = self._get_translated_details("invalid_ext", ext=ext)
            return result

        if img.width > self.max_w or img.height > self.max_h:
            result["messages"] = self._get_translated_messages("too_big", w=img.width, h=img.height, max_w=self.max_w, max_h=self.max_h)
            result["details"] = self._get_translated_details("too_big", w=img.width, h=img.height, max_w=self.max_w, max_h=self.max_h, ext=ext)
            return result

        result["status"] = "success"
        result["messages"] = self._get_translated_messages("valid")
        result["details"] = self._get_translated_details("valid", w=img.width, h=img.height, ext=ext)
        return result
