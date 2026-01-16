from typing import Dict, Any


def desc(description: str) -> Dict[str, Any]:
    """
    Utility function to simplify the nesting of descriptions in metadata.

    Marshmallow 4 moved 'description' from a field argument to a nested key
    within the 'metadata' dictionary. Since marshmallow-dataclass unpacks
    all field metadata directly into the field constructor, descriptions
    must be double-nested as {'metadata': {'description': ...}} to be
    correctly recognized during schema generation.
    This utility simplifies this boilerplate into a simple function call.
    """
    return {'metadata': {'description': description}}
