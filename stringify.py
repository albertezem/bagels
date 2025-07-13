from decimal import Decimal

def stringify_keys(obj):
    """
    Recursively walk obj, and whenever we see a dict,
    convert its keys to strings via str(key).
    """
    if isinstance(obj, dict):
        new = {}
        for key, val in obj.items():
            new_key = str(key)
            new[new_key] = stringify_keys(val)
        return new
    elif isinstance(obj, list):
        return [stringify_keys(item) for item in obj]
    elif isinstance(obj, Decimal):
        return str(obj)
    else:
        return obj


# your original nested dict
d = {
    "best_guess": "012",
    "response": {
        (0, 0, 2): {
            "best_guess": "013",
            "response": {
                (0, 0, 2): {
                    "best_guess": "016",
                    "response": {(0, 0, 3): {"value": 0}},
                    "value": 1,
                },
                (0, 0, 3): {
                    "best_guess": "013",
                    "response": {(0, 0, 3): {"value": 0}},
                    "value": 0,
                },
            },
            "value": 1.5,
        },
        (0, 0, 3): {
            "best_guess": "012",
            "response": {(0, 0, 3): {"value": 0}},
            "value": 0,
        },
        (0, 1, 0): {
            "best_guess": "234",
            "response": {(0, 0, 3): {"value": 0}},
            "value": 1,
        },
    },
    "value": 2.0,
}

