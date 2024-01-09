import json
import os

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
config = {}
config = json.load(open(config_path, 'r', encoding='utf-8'))

def get_config(key=None):
    return config.get(key, None) if key else config