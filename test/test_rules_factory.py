import sys, os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/back'))
sys.path.insert(0, path)
from core import rules_factory

# Instanciar la factoría
factory = rules_factory.RulesFactory() #rule_file="rules_json")

factory.load_rules()

print("Common rules:")
for rule in factory.common_rules:
    print(rule)

print("\nModel rules:")
for model, rules in factory.models.items():
    print(f"Model: {model}")
    for rule in rules:
        print(rule)