import re
import unicodedata
from typing import Dict, List, Tuple
from .base_rule import BaseRule, register_rule_class


# ───────────────────────── utilidades de normalización ──────────────────────────
def _normalize_text(text: str) -> str:
    """Minuscula, sin acentos, sin espacios extra."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode()
    return re.sub(r"\s+", " ", text.lower()).strip()


_VERSION_PREFIX = re.compile(r"\b(v\.?|ver\.?)\s*", re.IGNORECASE)
_VERSION_EXTRACT = re.compile(r"(\d+(?:\.\d+)*[a-z]?)", re.I)


def _clean_version(ver: str) -> str:
    """Quita 'v.', 'ver', espacios, deja solo dígitos/puntos/letra final."""
    ver = _VERSION_PREFIX.sub("", ver.lower())
    return _VERSION_EXTRACT.search(ver).group(1) if _VERSION_EXTRACT.search(ver) else ""


def _split_version(ver: str) -> Tuple[List[int], str]:
    """
    '2025a'   -> ([2025], 'a')
    '2.3'     -> ([2,3], '')
    '20160906'-> ([20160906], '')
    """
    match = re.match(r"^([0-9.]*)([a-z]?)$", ver)
    nums = [int(x) for x in match.group(1).split(".") if x] if match else []
    letter = match.group(2) if match else ""
    return nums, letter


def _is_newer_or_equal(ver: str, min_ver: str) -> bool:
    """Devuelve True si ver >= min_ver (segmentos numéricos y letra final)."""
    n1, l1 = _split_version(ver)
    n2, l2 = _split_version(min_ver)

    # Igualamos longitudes rellenando con ceros
    max_len = max(len(n1), len(n2))
    n1 += [0] * (max_len - len(n1))
    n2 += [0] * (max_len - len(n2))

    if n1 != n2:
        return n1 > n2
    # Si números iguales, compara letra ('' < 'a' < 'b' …)
    return l1 >= l2


# ───────────────────────── clase de la regla ─────────────────────────────────────
@register_rule_class
class ProcedimientoVersionCheckRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters["xpath"]
        # Ordenamos por longitud descendente para que “Complemento CEX” se pruebe antes que “CEX”
        self.valid_versions = dict(
            sorted(
                self.parameters.get("valid_versions", {}).items(),
                key=lambda kv: -len(kv[0])
            )
        )

    # -------------------------------------------------------------------------
    def validate(self, epc: "EpcDto") -> Dict:
        result = {
            "rule_id":     self.id,
            "status":      "error",
            "message":     "",
            "description": self.description,
            "details":     {}
        }

        proc_raw = epc.get_value_by_xpath(self.xpath)
        if proc_raw is None:
            result["message"] = f"No se encontró valor para el XPath: {self.xpath}"
            return result

        proc_norm = _normalize_text(proc_raw)

        # 1) detectar el nombre de procedimiento
        proc_name = None
        remaining = ""
        for name in self.valid_versions:
            if _normalize_text(name) in proc_norm:
                proc_name = name
                remaining = proc_norm.replace(_normalize_text(name), " ").strip()
                break

        if proc_name is None:
            result["message"] = f"El procedimiento '{proc_raw}' no está definido en las versiones válidas."
            return result

        # 2) extraer y limpiar la versión encontrada
        version_found = _clean_version(remaining)
        if not version_found:
            result["message"] = f"No se encontró una versión válida en '{proc_raw}'."
            result["details"] = {"provided_procedure": proc_name}
            return result

        # 3) comparar contra versión mínima
        min_version = _clean_version(self.valid_versions[proc_name])

        if _is_newer_or_equal(version_found, min_version):
            result.update({
                "status":  "success",
                "message": (f"El procedimiento '{proc_name}' con la versión "
                            f"'{version_found}' es válido."),
                "details": {
                    "validated_procedure": proc_name,
                    "validated_version":   version_found
                }
            })
        else:
            result.update({
                "message": (f"La versión '{version_found}' del procedimiento '{proc_name}' "
                            f"no es válida. Se esperaba la versión '{min_version}' o posterior."),
                "details": {
                    "provided_procedure": proc_name,
                    "provided_version":   version_found,
                    "expected_min_version": min_version
                }
            })

        return result
