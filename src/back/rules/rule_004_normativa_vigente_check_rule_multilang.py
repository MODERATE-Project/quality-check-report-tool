from .base_rule import BaseRule, register_rule_class
from typing import Dict
from unidecode import unidecode
import re


@register_rule_class
class NormativaVigenteCheckRule(BaseRule):
    _ALNUM = re.compile(r"[a-z0-9]")

    def __init__(self, rule_data: Dict):
        super().__init__(rule_data)
        self.xpath = self.parameters["xpath"]
        self.conditions = self.parameters.get("conditions", [])

    # ──────────────────────────────────────────────────────────────────────
    @staticmethod
    def _clean(text: str) -> str:
        """→ minúsculas, sin tildes, dejamos solo a‑z0‑9 (concatenado)"""
        txt = unidecode(text.lower())
        return "".join(NormativaVigenteCheckRule._ALNUM.findall(txt))

    # ──────────────────────────────────────────────────────────────────────
    def _get_translated_messages(self, key: str, **kwargs) -> dict:
        messages = self.parameters.get("messages", {}).get(key, {})
        return {
            lang: tpl.format(**kwargs) if tpl else ""
            for lang, tpl in messages.items()
        }

    def _get_translated_details(self, key: str, **kwargs) -> dict:
        details_template = self.parameters.get("details", {}).get(key, {})
        return {
            lang: {
                k: v.format(**kwargs) if isinstance(v, str) else v
                for k, v in detail.items()
            }
            for lang, detail in details_template.items()
        }


    def validate(self, epc: "EpcDto") -> Dict:
        res = self._new_result()

        normativa_raw = epc.get_value_by_xpath(self.xpath)
        ano_raw = epc.get_value_by_xpath("//IdentificacionEdificio/AnoConstruccion")

        if normativa_raw is None:
            res["messages"] = self._get_translated_messages("missing_normativa", field=self.xpath)
            res["message"] = res["messages"].get("es", "")
            return res
        if ano_raw is None:
            res["messages"] = self._get_translated_messages("missing_ano")
            res["message"] = res["messages"].get("es", "")
            return res
        try:
            ano = int(ano_raw)
        except ValueError:
            res["messages"] = self._get_translated_messages("ano_not_numeric", value=ano_raw)
            res["message"] = res["messages"].get("es", "")
            return res

        normativa_clean = self._clean(normativa_raw)

        cond = next(
            (
                c for c in self.conditions
                if (c.get("range", {}).get("min") is None or ano >= c["range"]["min"]) and
                   (c.get("range", {}).get("max") is None or ano <= c["range"]["max"])
            ),
            None
        )

        if cond is None:
            res["messages"] = self._get_translated_messages("no_rule_for_year", ano=ano)
            res["message"] = res["messages"].get("es", "")
            return res

        expected_variants = [
            self._clean(v) for v in cond.get("expected_value", "").split("/") if v.strip()
        ]

        if normativa_clean in expected_variants:
            res["status"] = "success"
            res["messages"] = self._get_translated_messages("valid", normativa=normativa_raw, ano=ano)
            res["message"] = res["messages"].get("es", "")
            res["details"] = self._get_translated_details(
            "valid_normativa",
            normativa=normativa_raw,
            ano=ano,
            esperado=cond.get("expected_value")
        )
        else:
            res["messages"] = self._get_translated_messages("invalid", normativa=normativa_raw, ano=ano)
            res["message"] = res["messages"].get("es", "")
            res["details"] = self._get_translated_details(
            "invalid_normativa",
            normativa=normativa_raw,
            ano=ano,
            esperado=cond.get("expected_value")
        )

        return res
        if ano_raw is None:
            res["message"] = "No se encontró el año de construcción (<AnoConstruccion>)."
            return res
        try:
            ano = int(ano_raw)
        except ValueError:
            res["message"] = f"'AnoConstruccion' no es numérico: {ano_raw}"
            return res

        normativa_clean = self._clean(normativa_raw)

        # → Condición cuyo rango incluye el año
        cond = next(
            (
                c for c in self.conditions
                if (c.get("range", {}).get("min") is None or ano >= c["range"]["min"]) and
                   (c.get("range", {}).get("max") is None or ano <= c["range"]["max"])
            ),
            None
        )

        if cond is None:
            res["message"] = f"No se encontró normativa válida para el año {ano}."
            return res

        expected_variants = [
            self._clean(v) for v in cond.get("expected_value", "").split("/")
            if v.strip()
        ]

        if normativa_clean in expected_variants:
            res.update({
                "status":  "success",
                "message": (f"La normativa '{normativa_raw}' es válida para el año "
                            f"{ano}."),
                "details": {
                    "validated_normativa":        normativa_raw,
                    "validated_ano_construccion": ano,
                    "expected_normativa":         cond.get("expected_value")
                }
            })
        else:
            res.update({
                "message": ("La normativa aplicada no concuerda con la correspondiente "
                            "al año de construcción de la edificación."),
                "details": {
                    "provided_normativa":      normativa_raw,
                    "validated_ano_construccion": ano,
                    "expected_normativa":      cond.get("expected_value")
                }
            })

        return res
