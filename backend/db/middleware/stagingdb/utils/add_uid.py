import uuid
from typing import Dict, Any, List, Tuple


def add_uid_to_object(mutable_obj: Any) -> Tuple[str, Dict[str, Any]]:
    """
    Generate a UUID and add it to an object's data.

    @param mutable_obj: The mutable object to add a UUID to
    @return: A tuple containing the generated UUID and the object data with the UUID added
    """
    obj_id = str(uuid.uuid4())
    # prefer __dict__ over asdict() for performance reasons
    # this goes for here and every other use of __dict__ / asdict()
    # see https://stackoverflow.com/a/52229565
    # since we currently only have simple, non-nested dataclasses, this is fine
    obj_data = mutable_obj.__dict__
    obj_data.update({
        'id': obj_id,
    })
    return obj_id, obj_data


def add_uid_to_objects(mutable_obj: List[Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Generate a UUID and add it to each object's data.
    The same as add_uid_to_object, but for a list of objects.

    @param mutable_obj: The list of mutable objects to add UUIDs to
    @return: A tuple containing the list of generated UUIDs and the list of object data with the UUIDs added
    """
    ids = []
    objects = []
    for obj in mutable_obj:
        obj_id, obj_data = add_uid_to_object(obj)
        ids.append(obj_id)
        objects.append(obj_data)

    return ids, objects
