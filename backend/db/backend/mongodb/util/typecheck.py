import orjson

def is_json(data: str):
    """Check if a string is valid JSON."""
    try:
        orjson.loads(data)
    except:
        return False
    return True
