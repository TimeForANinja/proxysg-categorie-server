from typing import List

def split_opt_str_group(group: str | None) -> List[str]:
    if group is None or group == "":
        return []
    return split_str_group(group)

def split_str_group(group: str) -> List[str]:
    parts = group.split(",")
    return [
        str(part)
        for part
        in parts
    ]
