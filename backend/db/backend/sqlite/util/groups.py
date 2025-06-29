from typing import List


def join_str_group(obj: List[str]) -> str:
    """
    This method joins a list of strings into a comma-separated string.

    :param obj: The list of strings to be joined
    :return: A comma-separated string
    """
    return ",".join(obj)

def split_opt_str_group(group: str | None) -> List[str]:
    """
    This method splits a comma-separated string into a list of strings.

    :param group: The comma-separated string to be split
    :return: A list of strings
    """
    if group is None or group == '':
        return []
    return split_str_group(group)


def split_str_group(group: str) -> List[str]:
    """
    This method splits a comma-separated string into a list of strings.

    :param group: The comma-separated string to be split
    :return: A list of strings
    """
    parts = group.split(',')
    return [
        str(part).strip()
        for part
        in parts
    ]
