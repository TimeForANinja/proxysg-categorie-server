from typing import Dict, Any


def find_diff(old: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
    """Utility to find the difference between two dictionaries."""
    diffs = {}
    keys = set(list(old.keys()) + list(new.keys()))
    for key in keys:
        if not key in old:
            diffs[key] = new[key]
        elif not key in new:
            diffs[key] = "<removed>"
        elif old[key] != new[key]:
            diffs[key] = new[key]
    return diffs


def diff_str(old: Dict[str, Any], new: Dict[str, Any]) -> str:
    """Utility to calculate the diff between two dicts and format the result as a string."""
    diffs = find_diff(old, new)
    resp = []
    for key, val in diffs.items():
        resp.append(f"{key}={val}")
    return ",".join(resp)
