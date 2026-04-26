from typing import List, Optional, Tuple

from db.abc.db import DBInterface


def list_obj_diff(
        backend: DBInterface,
        a: List[str],
        b: Optional[List[str]],
        cls: type[any],
        props: List[str],
        exclude: Optional[List[str]] = None
) -> List[str]:
    """
    List the IDs of all objects that have been modified (added or removed) between two lists.

    :param backend: The database backend to use.
    :param a: The first list of object IDs.
    :param b: The second list of object IDs, or None to compare against an empty list.
    :param cls: The class type of the objects being compared.
    :param props: The properties of the objects to track for changes.
    :param exclude: Optional list of object IDs to exclude from the result.
    :return: List of object IDs that have been modified.
    """

    # take diff of the hash lists
    new_obj, del_obj = list_diff(a, b)
    # then fetch all hashes that changed
    modified_objects = cls.batch_read(backend, new_obj + del_obj)

    # convert to set to deduplicate
    changed_ids = list(set([
        # fetch all properties of the object, that the user wants to track
        getattr(obj, p)
        for obj in modified_objects
        for p in props
        if hasattr(obj, p)
    ]))

    if exclude:
        # remove any excluded IDs
        changed_ids = [c for c in changed_ids if c not in exclude]

    return changed_ids


def list_diff(a: List[str], b: Optional[List[str]]) -> Tuple[List[str], List[str]]:
    """
    Calculate the added and removed items between two lists
    :param a: The first list
    :param b: The second list, or None to compare against an empty list
    :return: Tuple of added and removed items
    """
    if b is None:
        return a, []
    return list(set(a) - set(b)), list(set(b) - set(a))
