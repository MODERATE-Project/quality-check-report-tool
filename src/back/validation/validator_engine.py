import logging

class validatorEngine:

    # def __init__(self):

    def execute_validations(self, epc, rules : dict) -> dict:
        logger = logging.getLogger(__name__)
        for rule in rules: 
            logger.debug("Regla: " + rule.id + " - Descripcion: " + rule.description)
            #print("Regla: " + rule.id + " - Descripcion: " + rule.description)
            
