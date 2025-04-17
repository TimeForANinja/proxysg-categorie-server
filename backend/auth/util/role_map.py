from typing import Dict, List

from auth.auth_user import AUTH_ROLES_RO, AUTH_ROLES_RW
from log import log_error

internal_role_map = {
    'ro': AUTH_ROLES_RO,
    'rw': AUTH_ROLES_RW,
}


def parse_role_map(raw: str) -> Dict[str, str]:
    """
    Try to parse a User Role-Map.
    The Role-Map allows to map external roles to internal roles.

    The Syntax for this is a comma-separated list of role mappings in the form of:
        <external_role>=<internal_role>,<external_role>=<internal_role>
    with:
        external_role: The external role (e.g., 'role1')
        internal_role: The internal role (one of 'ro' or 'rw')

    :param raw: The raw Role-Map string
    :return: A dictionary mapping external roles to internal roles, or an empty dictionary if parsing failed.
    """
    parsed_map: Dict[str, str] = {}
    parts = raw.split(',')
    for part in parts:
        segments = part.split('=')
        if len(segments) != 2:
            log_error('AUTH', 'Invalid Role-Map Fornat', { 'role_map': raw, 'segments': segments})
            continue
        if segments[1].lower() not in internal_role_map.keys():
            log_error('AUTH', 'Unknown Target Role', { 'role_map': raw, 'internal_role': segments[1].lower()})
            continue
        parsed_map[segments[0]] = internal_role_map.get(segments[1].lower())
    return parsed_map


def apply_role_map(external_roles: List[str], role_map: Dict[str, str]) -> List[str]:
    """
    Apply a Role-Map to a list of external roles.

    :param external_roles: A list of external roles
    :param role_map: A dictionary mapping external roles to internal roles
    :return: A list of internal roles, or the original list if the mapping failed.
    """
    return [
        # default to the external role if no external role is not in map
        role_map.get(x, x)
        for x in external_roles
    ]
