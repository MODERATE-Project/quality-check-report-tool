from typing import Dict, Tuple, Optional, Any
from core.epc_dto import EpcDto
from .base_rule import BaseRule, register_rule_class

# Tabla de demanda de ACS en función del número de dormitorios (en litros/día)
DEMANDA_POR_DORMITORIOS = {
    "1": 42,   # 1,5 personas * 28 L/día
    "2": 84,   # 3 personas * 28 L/día
    "3": 112,  # 4 personas * 28 L/día
    "4": 140,  # 5 personas * 28 L/día
    "5": 168,  # 6 personas * 28 L/día
    "6": 196,  # 7 personas * 28 L/día
    "6+": 196  # Más de 6 dormitorios, mismo valor que 6 (ajustar según normativa)
}

# Factores de descentralización según el CTE
FACTOR_DESCENTRALIZACION = {
    "3": 1.00,
    "10": 0.95,
    "20": 0.90,
    "50": 0.85,
    "75": 0.80,
    "100": 0.75,
    "101": 0.70
}


@register_rule_class
class DemandaDiariaACSRule(BaseRule):
    """
    Regla que se encarga de (1) preguntar al usuario lo necesario
    para comprobar la DemandaDiariaACS según el CTE, y (2) validar
    esa demanda contra el nº de dormitorios o de viviendas.
    """
    
    def get_question(self, epc: EpcDto) -> Optional[Tuple[str, Dict[str, Dict[str, Any]]]]:
        """
        Devuelve una tupla (id_de_la_regla, dict_preguntas) si se necesita
        preguntar algo al usuario, o None si no hay nada que preguntar.

        Lógica:
        - Si el 'building_type' está dentro de la lista de 'values' (residenciales):
          * Si es BloqueDeViviendaCompleto -> pregunta '¿Cuántas viviendas hay en el bloque?'
          * En caso contrario -> pregunta '¿Cuántos dormitorios tiene la vivienda?'
        - Si no está en la lista -> no hace falta preguntar nada -> return None
        """

        building_type = epc.get_value_by_xpath(self.parameters["xpath_tipo_edificio"])
        valid_types = self.parameters.get("values", [])

        # Solo preguntamos si el building_type está en los tipos residenciales
        if building_type not in valid_types:
            return None

        questions_to_ask: Dict[str, Dict[str, Any]] = {}

        # Distinguimos entre BloqueDeViviendaCompleto y los demás
        if building_type == "BloqueDeViviendaCompleto":
            questions_to_ask[f"{self.id}_0"] = {
                "text": (
                    "Para verificar la demanda de ACS, indica cuántas viviendas hay "
                    "en el bloque (factor de centralización)."
                ),
                "type": "integer"
            }
        else:
            # ViviendaUnifamiliar, ViviendaIndividualEnBloque, etc.
            questions_to_ask[f"{self.id}_0"] = {
                "text": (
                    "Para verificar la demanda de ACS, indica cuántos dormitorios "
                    "tiene la vivienda."
                ),
                "type": "integer"
            }

        # Si no hay preguntas (caso raro), devolvemos None
        if not questions_to_ask:
            return None

        # Devolvemos la tupla con (id_regla, dict_preguntas)
        return (self.id, questions_to_ask)


    def validate(self, epc: EpcDto, user_responses: Dict[str, Any]) -> Dict:
        """
        1. Toma la DemandaDiariaACS del XML.
        2. Según building_type, lee la respuesta (nº dormitorios o nº viviendas).
        3. Calcula la demanda 'esperada' y la compara con la real.
        4. Devuelve dict con 'error' si falla, o un dict vacío si pasa.
        """

        # Extraer tipo de edificio y demanda real del XML
        building_type = epc.get_value_by_xpath(self.parameters["xpath_tipo_edificio"])
        demanda_acs_str = epc.get_value_by_xpath(self.parameters["DemandaDiariaACS"])
        if not demanda_acs_str:
            return {"error": "No se especifica DemandaDiariaACS en el XML."}

        try:
            demanda_acs_real = float(demanda_acs_str)
        except ValueError:
            return {"error": "DemandaDiariaACS no es un valor numérico válido."}

        # La respuesta del usuario: en get_question() usamos f"{self.id}_0"
        user_response_key = f"{self.id}_0"
        if user_response_key not in user_responses:
            # Si no está la respuesta, no podemos validar
            return {"error": "No se ha recibido respuesta del usuario para DemandaDiariaACS."}

        try:
            user_value = int(user_responses[user_response_key])
        except ValueError:
            return {"error": "La respuesta del usuario no es un número entero válido."}

        # Calculamos la demanda 'esperada' según el caso
        if building_type == "BloqueDeViviendaCompleto":
            # 1) Si es bloque, primero definimos una demanda base "por vivienda".
            #    Aquí hay distintas interpretaciones. Una forma: asumes 42 L/día (mínimo)
            #    *cuando desconozco dormitorios de cada una* o la media que defina la normativa.
            #    Ajusta según tu modelo. Ejemplo ultra simple: 42 L por vivienda.

            demanda_base_por_vivienda = 42.0  # Podrías usar un promedio más elaborado
            demanda_base_total = demanda_base_por_vivienda * user_value

            # 2) Aplicas factor de centralización
            factor = self._obtener_factor_descentralizacion(user_value)
            demanda_acs_esperada = demanda_base_total * factor

        else:
            # Caso 'ViviendaUnifamiliar' o 'ViviendaIndividualEnBloque'
            # 1) Obtenemos la demanda base usando la tabla DEMANDA_POR_DORMITORIOS
            n_dormitorios = user_value
            if n_dormitorios >= 6:
                # Usamos la clave '6+'
                demanda_acs_esperada = DEMANDA_POR_DORMITORIOS["6+"]
            else:
                # Convertimos a str para indexar: "1", "2", "3", ...
                demanda_acs_esperada = DEMANDA_POR_DORMITORIOS.get(str(n_dormitorios), 42.0)

        # Comparamos demanda_acs_real con demanda_acs_esperada
        # Definimos un margen de tolerancia (por ejemplo, +/- 10%):
        margen_admitido = 0.10
        inferior = demanda_acs_esperada * (1 - margen_admitido)
        superior = demanda_acs_esperada * (1 + margen_admitido)

        if not (inferior <= demanda_acs_real <= superior):
            return {
                "error": (
                    f"La DemandaDiariaACS real ({demanda_acs_real:.2f} L/día) no concuerda con "
                    f"la esperada ({demanda_acs_esperada:.2f} L/día ±10%)."
                )
            }

        # Si todo OK
        return {}

    def _obtener_factor_descentralizacion(self, num_viviendas: int) -> float:
        """
        Ejemplo sencillo: busca el primer 'umbral' en FACTOR_DESCENTRALIZACION
        que sea >= num_viviendas. Si no encuentra, usa el factor de 101.
        Ajusta la lógica a tus rangos reales.
        """
        # Ordenamos las keys (str) como ints
        thresholds = sorted(int(k) for k in FACTOR_DESCENTRALIZACION.keys())
        for th in thresholds:
            if num_viviendas <= th:
                return FACTOR_DESCENTRALIZACION[str(th)]
        # Si no encuentra ninguno (más de 101 viviendas), devolvemos el factor "101"
        return FACTOR_DESCENTRALIZACION["101"]