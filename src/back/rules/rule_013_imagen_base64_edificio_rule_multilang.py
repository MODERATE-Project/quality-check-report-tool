import base64
import re
import unicodedata
from io import BytesIO
from typing import Dict, List, Tuple

from PIL import Image
from .base_rule import BaseRule, register_rule_class


def _normalize_ext(ext: str) -> str:
    if not ext:
        return ""
    ext = unicodedata.normalize("NFKD", ext).lower().strip()
    if not ext.startswith("."):
        ext = "." + ext
    return ext


def _decode_base64_image(b64_str: str) -> Tuple[bool, Dict]:
    m = re.match(r"^data:image/([a-z0-9.+-]+);base64,(.+)$", b64_str, re.I)
    mime_ext = None
    b64_data = b64_str
    if m:
        mime_ext = _normalize_ext(m.group(1).split("+")[0])
        b64_data = m.group(2)

    try:
        img_bytes = base64.b64decode(b64_data, validate=True)
        img = Image.open(BytesIO(img_bytes))
        img.verify()
        img = Image.open(BytesIO(img_bytes))
    except Exception:
        return False, {
            "message": "La imagen no es válida o está dañada.",
            "details": {"sample": b64_str[:40] + "..."}
        }

    ext = mime_ext or _normalize_ext(img.format.lower() if img.format else "")
    return True, {"image": img, "ext": ext}


@register_rule_class
class ImagenBase64EdificioRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters["xpath_plano"]
        self.valid_exts = [_normalize_ext(e) for e in self.parameters.get("valid_extensions", [])]
        self.max_w = int(self.parameters.get("max_width", 800))
        self.max_h = int(self.parameters.get("max_height", 600))

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
        raw_value = epc.get_value_by_xpath(self.xpath)

        if not raw_value or raw_value.strip() == "":
            result["messages"] = self._get_translated_messages("missing")
            result["message"] = result["messages"].get("es", "")
            result["details"] = self._get_translated_details("missing", value="vacía")
            return result

        ok, info = _decode_base64_image(raw_value)
        if not ok:
            result["messages"] = self._get_translated_messages("invalid_data")
            result["message"] = result["messages"].get("es", "")
            result["details"] = self._get_translated_details("invalid_data", muestra=raw_value[:40] + "...")
            return result

        img: Image.Image = info["image"]
        ext: str = info["ext"]

        if ext not in self.valid_exts:
            result["messages"] = self._get_translated_messages("invalid_ext", formato=ext, validos=", ".join(self.valid_exts))
            result["message"] = result["messages"].get("es", "")
            result["details"] = self._get_translated_details("invalid_ext", formato=ext)
            return result

        if img.width > self.max_w or img.height > self.max_h:
            result["messages"] = self._get_translated_messages("too_big", ancho=img.width, alto=img.height, max_w=self.max_w, max_h=self.max_h)
            result["message"] = result["messages"].get("es", "")
            result["details"] = self._get_translated_details("too_big", ancho=img.width, alto=img.height, max_w=self.max_w, max_h=self.max_h)
            return result

        result["status"] = "success"
        result["messages"] = self._get_translated_messages("valid")
        result["message"] = result["messages"].get("es", "")
        result["details"] = self._get_translated_details("valid", ancho=img.width, alto=img.height, formato=ext)
        return result
