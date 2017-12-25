import json


def save(plans):
    with open("plans.json", 'w') as f:
        json.dump(plans, f)


def load():
    with open("plans.json", 'r') as f:
        return json.load(f)
