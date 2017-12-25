import json


def save(plans):
    with open("plans.json", 'w') as f:
        json.dump(plans, f)
