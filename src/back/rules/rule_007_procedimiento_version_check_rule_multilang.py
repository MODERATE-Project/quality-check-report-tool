from .base_rule import BaseRule, register_rule_class
import re
import unicodedata
from typing import Dict, List, Tuple


def _normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode()
    return re.sub(r"\s+", " ", text.lower()).strip()


_VERSION_PREFIX = re.compile(r"\b(v\.?|ver\.?)\s*", re.IGNORECASE)
_VERSION_EXTRACT = re.compile(r"(\d+(?:\.\d+)*[a-z]?)", re.I)

def _clean_version(ver: str) -> str:
    ver = _VERSION_PREFIX.sub("", ver.lower())
    return _VERSION_EXTRACT.search(ver).group(1) if _VERSION_EXTRACT.search(ver) else ""

def _split_version(ver: str) -> Tuple[List[int], str]:
    match = re.match(r"^([0-9.]*)([a-z]?)$", ver)
    nums = [int(x) for x in match.group(1).split(".") if x] if match else []
    letter = match.group(2) if match else ""
    return nums, letter

def _is_newer_or_equal(ver: str, min_ver: str) -> bool:
    n1, l1 = _split_version(ver)
    n2, l2 = _split_version(min_ver)
    max_len = max(len(n1), len(n2))
    n1 += [0] * (max_len - len(n1))
    n2 += [0] * (max_len - len(n2))
    return n1 > n2 or (n1 == n2 and l1 >= l2)


@register_rule_class
class ProcedimientoVersionCheckRule(BaseRule):
    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters["xpath"]
        self.valid_versions = dict(
            sorted(self.parameters.get("valid_versions", {}).items(), key=lambda kv: -len(kv[0]))
        )

    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        messages = self.parameters.get("messages", {}).get(key, {})
        return {lang: msg.format(**kwargs) for lang, msg in messages.items()}

    def _get_translated_details(self, key: str, **kwargs) -> dict:
        template = self.parameters.get("details", {}).get(key, {})
        return {
            lang: {k: v.format(**kwargs) for k, v in detail.items()}
            for lang, detail in template.items()
        }

    def validate(self, epc: "EpcDto") -> Dict:
        result = self._new_result()

        proc_raw = epc.get_value_by_xpath(self.xpath)
        if proc_raw is None:
            result["messages"] = self._get_translated_messages("missing_value", xpath=self.xpath)
            return result

        proc_norm = _normalize_text(proc_raw)
        proc_name, remaining = None, ""

        for name in self.valid_versions:
            if _normalize_text(name) in proc_norm:
                proc_name = name
                remaining = proc_norm.replace(_normalize_text(name), " ").strip()
                break

        if proc_name is None:
            result["messages"] = self._get_translated_messages("unknown_procedure", raw=proc_raw)
            return result

        version_found = _clean_version(remaining)
        if not version_found:
            result["messages"] = self._get_translated_messages("missing_version", raw=proc_raw)
            result["details"] = self._get_translated_details("missing_version", procedure=proc_name)
            return result

        min_version = _clean_version(self.valid_versions[proc_name])
        if _is_newer_or_equal(version_found, min_version):
            result["status"] = "success"
            result["messages"] = self._get_translated_messages("valid", procedure=proc_name, version=version_found)
            result["details"] = self._get_translated_details("valid", procedure=proc_name, version=version_found)
        else:
            result["messages"] = self._get_translated_messages("invalid", procedure=proc_name, version=version_found, expected=min_version)
            result["details"] = self._get_translated_details("invalid", procedure=proc_name, version=version_found, expected=min_version)

        return result
