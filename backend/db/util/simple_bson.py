from typing import Dict, List, Any, Union
import bson


BSON_SUPPORTED_TYPES = Union[List[str], Dict[str, Any]]


def bson_encode(value: BSON_SUPPORTED_TYPES) -> bytes:
    """Encode a complex object into BSON bytes."""
    return bson.encode({'data': value})


def bson_decode(data: bytes) -> BSON_SUPPORTED_TYPES:
    """Encode a complex object from BSON bytes."""
    doc = bson.decode(data)
    return doc["data"]
