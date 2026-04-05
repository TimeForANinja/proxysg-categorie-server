from typing import Dict, List
import bson


def encode_list_str(values: List[str]) -> bytes:
    """Encode a list[str] into BSON bytes."""
    return bson.encode({'list': values})


def decode_list_str(data: bytes) -> List[str]:
    """Decode BSON bytes back into a list[str]."""
    doc = bson.decode(data)
    return doc["list"]


def _encode_dict_str_list_str(mapping: Dict[str, List[str]]) -> bytes:
    """Encode a dict[str, list[str]] into BSON bytes."""
    return bson.encode({'dict': mapping})


def _decode_dict_str_list_str(data: bytes) -> Dict[str, List[str]]:
    """Decode BSON bytes back into a dict[str, list[str]]."""
    doc = bson.decode(data)
    return doc["dict"]


def encode_dict_str(mapping: Dict[str, str]) -> bytes:
    """Encode a dict[str, str] into BSON bytes."""
    return bson.encode({'dict': mapping})


def decode_dict_str(data: bytes) -> Dict[str, str]:
    """Decode BSON bytes back into a dict[str, str]."""
    doc = bson.decode(data)
    return doc["dict"]
