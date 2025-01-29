from typing import Dict
from ..input.input_layer import InputLayer, XmlInputLayer
from .rules_factory import RulesFactory
from ..validation.validator_engine import validatorEngine
from .rule_json_builder import RuleJsonBuilder
import json
import os.path
import logging
from ..config import RULES_JASON_PATH, RULES_BASE_PATH, RULES_CACHE_PATH, RULES_CLASS_PATH
from .prepare_output import validation_results_to_html



logger = logging.getLogger(__name__)

class PipelineManager:
    def __init__(self):
        """
        Initializes the PipelineManager with its own instances of input layer and rule manager.
        """
        self.inputLayer = XmlInputLayer()
        self.ruleManager = RulesFactory()
        self.validatorEngine = validatorEngine()
        self.builder = RuleJsonBuilder(
            rule_directory = RULES_JASON_PATH, #"rules_json",
            base_file = RULES_BASE_PATH, #"rules_base.json",
            cache_file = RULES_CACHE_PATH #"rules_cache.json"
        )
        # Construir las reglas (usará el caché "rules_cache.json" si no hay cambios)
        rules = self.builder.build_rules()
        self.ruleManager.load_rules()
        # Mostrar las reglas ensambladas
        print(json.dumps(rules, indent=4, ensure_ascii=False))
        
    def process_request(self, file) -> Dict:
        """
        Processes an XML file and applies the loaded rules.

        Args:
            file (str): Path to the XML file.

        Returns:
            Dict: Processed data after applying rules.
        """

        epc = self.inputLayer.process_input(file)


        

        # Comprobación de reglas cargadas
        print("Common rules:")
        for rule in self.ruleManager.common_rules:
            print(rule)

        print("\nModel rules:")
        for model, rules in self.ruleManager.models.items():
            print(f"Model: {model}")
            for rule in rules:
                print(rule)

        # self.validatorEngine.execute_validations(epc, self.ruleManager.common_rules)

        logger.debug("Vamos a aplicar las reglas al documento: ")
        validation_results = self.ruleManager.apply_rules(epc)
        # Imprimir resultados (para depuración)
        logger.debug("Resultados de las validaciones:")
        logger.debug(json.dumps(validation_results, indent=4, ensure_ascii=False))

        return validation_results


