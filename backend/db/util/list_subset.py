from collections import defaultdict
from typing import Dict, List, Any

from db.abc.constants import KEY_LENGTH, TYPE_KEY, TypeIDs

from util.hash import sha256_hash
from util.simple_bson import bson_encode, BSON_SUPPORTED_TYPES


def _split_list_subset(entries: List[str]) -> Dict[str, List[str]]:
    """split the list into subsets, based on the first KEY_LENGTH characters"""
    subsets = defaultdict(list)
    for x in entries:
        key, val = x[:KEY_LENGTH], x[KEY_LENGTH:]
        subsets[key].append(val)
    return subsets


def build_superset(entries: List[str]) -> List[BSON_SUPPORTED_TYPES]:
    raw_data: List[BSON_SUPPORTED_TYPES] = []

    subsets = _split_list_subset(entries)

    # calc subset hashes track them for the superset
    superset: Dict[str, Any] = {TYPE_KEY: TypeIDs.TYPE_ID_LIST_LARGE}
    for key, val in subsets.items():
        subset_hash = sha256_hash(bson_encode(val))
        superset[key] = subset_hash
        raw_data.append(val)

    # now store the superset
    raw_data.append(superset)

    return raw_data


def strip_type(data: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if k != TYPE_KEY}
