from typing import Dict
from input.input_layer import InputLayer, XmlInputLayer
from .rules_manager import RuleManager
from validation.validator_engine import validatorEngine

class PipelineManager:
    def __init__(self):
        """
        Initializes the PipelineManager with its own instances of input layer and rule manager.
        """
        self.inputLayer = XmlInputLayer()
        self.ruleManager = RuleManager()
        self.validatorEngine = validatorEngine()
        
    def process_request(self, file) -> Dict:
        """
        Processes an XML file and applies the loaded rules.

        Args:
            file (str): Path to the XML file.

        Returns:
            Dict: Processed data after applying rules.
        """
        epc = self.inputLayer.process_input(file)

        self.ruleManager.load_rules()

        self.validatorEngine.execute_validations(epc, self.ruleManager.common_rules)

        # processed_data = self.ruleManager.apply_rules(epc)

        return epc


