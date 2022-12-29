import json

def parse_val(val):
    return json.loads(val) if isinstance(val, str) else val
