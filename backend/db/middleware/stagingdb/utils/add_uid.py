import uuid
from dataclasses import asdict
from typing import Dict, Any, List, Tuple


def add_uid_to_object(mutable_obj: Any) -> Tuple[str, Dict[str, Any]]:
    """
    Generate a UUID and add it to an object's data.

    @param mutable_obj: The mutable object to add a UUID to
    @return: A tuple containing the generated UUID and the object data with the UUID added
    """
    obj_id = str(uuid.uuid4())
    obj_data = asdict(mutable_obj)
    obj_data.update({
        'id': obj_id,
    })
    return obj_id, obj_data
