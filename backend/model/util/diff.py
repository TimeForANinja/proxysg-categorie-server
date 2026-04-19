from typing import List, Optional, Tuple

from db.abc.db import DBInterface


def list_obj_diff(backend: DBInterface, a: List[str], b: Optional[List[str]], cls: type[any], props: List[str]) -> List[str]:
    """
    List the IDs of all objects that have been modified (added or removed) between two lists.
    """

    # take diff of the hash lists
    new_obj, del_obj = list_diff(a, b)
    # then fetch all hashes that changed
    modified_objects = cls.batch_read(backend, new_obj + del_obj)

    # convert to set to deduplicate
    return list(set([
        # fetch all properties of the object, that the user wants to track
        getattr(obj, p)
        for obj in modified_objects
        for p in props
        if hasattr(obj, p)
    ]))


def list_diff(a: List[str], b: Optional[List[str]]) -> Tuple[List[str], List[str]]:
    """calc the added and removed items between two lists"""
    if b is None:
        return a, []
    return list(set(a) - set(b)), list(set(b) - set(a))
