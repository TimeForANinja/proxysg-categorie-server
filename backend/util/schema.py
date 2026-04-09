from dataclasses import field
from typing import Dict, Any
from apiflask.fields import Field as tField


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

def to_field(f: tField, **kwargs):
    """
    Convert an APIFlask Type to a Dataclass Type.
    This is required for any Dataclass being converted to a Schema using class_schema(xxx)()
    If not done so, the following warning will be raised:
    ```
    UserWarning: <class 'routes.schemas.url.ListURLOutput'> has already been added to the spec.
    ```
    """
    return field(
        metadata={
            "marshmallow_field": f,
        },
        **kwargs,
    )
