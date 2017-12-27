import json


def save(json_file, data):
    with open(json_file, 'w') as f:
        json.dump(data, f)


def load(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)
