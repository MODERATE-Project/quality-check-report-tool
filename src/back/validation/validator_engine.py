

class validatorEngine:

    # def __init__(self):

    def execute_validations(self, epc, rules : dict) -> dict:
        for rule in rules: print(rule["type"])