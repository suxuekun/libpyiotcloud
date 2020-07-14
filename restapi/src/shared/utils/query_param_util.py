

import json


def get_boolean_value(value: str):
    result = False
    if value == 'false' or value == 'true':
        result = json.loads(value)
    
    return result
