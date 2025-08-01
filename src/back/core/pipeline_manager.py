from typing import Dict
from input.input_layer import InputLayer, XmlInputLayer
from core.rules_factory import RulesFactory
from validation.validator_engine import validatorEngine
from core.rule_json_builder import RuleJsonBuilder
import json
import os.path
import logging
from config import RULES_JASON_PATH, RULES_BASE_PATH, RULES_CACHE_PATH, RULES_CLASS_PATH
# from core.prepare_output import validation_results_to_html



logger = logging.getLogger(__name__)

class PipelineManager:
    epc = None
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
        self.epc = None
        # Construir las reglas (usará el caché "rules_cache.json" si no hay cambios)
        rules = self.builder.build_rules()
        self.ruleManager.load_rules()
        # Mostrar las reglas ensambladas
        print(json.dumps(rules, indent=4, ensure_ascii=False))
        
    def process_request(self, file, questions) -> Dict:
        """
        Processes an XML file and applies the loaded rules.

        Args:
            file (str): Path to the XML file.

        Returns:
            Dict: Processed data after applying rules.
        """

        self.epc = self.inputLayer.process_input(file)


        

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
        validation_results = self.ruleManager.apply_rules(self.epc,questions)
        # Imprimir resultados (para depuración)
        logger.debug("Resultados de las validaciones:")
        logger.debug(json.dumps(validation_results, indent=4, ensure_ascii=False,default=lambda o: list(o) if isinstance(o, set) else str(o)))

        return validation_results
    
    def prepare_questions_to_user(self, file) -> Dict:
        """
        Prepares the questions to be asked to the user based on the validation results.

        Args:
            validation_results (Dict): Validation results after applying rules.

        Returns:
            Dict: Questions to be asked to the user.

        """

        self.epc = self.inputLayer.process_input(file)
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

        logger.debug("Vamos buscar reglas con pregunta hacia el usuario ")
        questions = self.ruleManager.get_questions(self.epc)
        # Imprimir resultados (para depuración)
        logger.debug("Preguntas para el usuario:")
        #recorrer y mostar las preguntas
        logger.debug(questions)

        return questions


