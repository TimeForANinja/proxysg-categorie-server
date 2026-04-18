from typing import List, Optional, Tuple

from db.abc.db import DBInterface


def list_obj_diff(backend: DBInterface, a: List[str], b: Optional[List[str]], cls: type[any], props: List[str]) -> List[str]:
    """
    List the IDs of all objects that have been modified (added or removed) between two lists.
    """
    collector = set()

    new_obj, del_obj = list_diff(a, b)
    for obj_hash in new_obj + del_obj:
        url = cls.read(backend, obj_hash)
        for p in props:
            collector.add(getattr(url, p))

    return list(collector)


def list_diff(a: List[str], b: Optional[List[str]]) -> Tuple[List[str], List[str]]:
    """calc the added and removed items between two lists"""
    if b is None:
        return a, []
    return list(set(a) - set(b)), list(set(b) - set(a))
