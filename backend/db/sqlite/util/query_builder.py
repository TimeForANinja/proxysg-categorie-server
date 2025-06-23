from typing import TypeVar, Any, Mapping

T = TypeVar('T')

def build_update_query(mut_obj: T, field_mappings: Mapping[str, str]) -> tuple[list[str], list[Any]]:
    """
    Build SQL update query parts based on non-None fields in any object.

    Args:
        mut_obj: Any object containing the fields to update
        field_mappings: Dictionary mapping object attributes to SQL column names

    Returns:
        Tuple of (list of update expressions, list of parameters)

    Example:
        field_mappings = {
            'name': 'user_name',
            'email': 'email_address'
        }
        updates, params = _build_update_query(user, field_mappings)
    """
    updates = []
    params = []

    for obj_field, sql_field in field_mappings.items():
        value = getattr(mut_obj, obj_field, None)
        if value is not None:
            updates.append(f'{sql_field} = ?')
            params.append(value)

    return updates, params
