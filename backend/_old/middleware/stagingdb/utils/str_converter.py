import json
from typing import List

from db.middleware.stagingdb.utils.cache import SessionCache


def stringify_list(l: List[str]) -> str:
    """Convert a list of strings to a JSON string."""
    escaped = json.dumps(l)
    # skip the opening and closing brackets
    return escaped[1:-1]


def stringify_category_changes(cache: SessionCache, added_ids: List[str], removed_ids: List[str]) -> str:
    """Convert added/removed lists of category IDs to a human-readable string."""
    added_cats = stringify_list([cache.get_category(cid).name for cid in added_ids])
    removed_cats = stringify_list([cache.get_category(cid).name for cid in removed_ids])
    if added_cats and removed_cats:
        return f"added {added_cats}, removed {removed_cats}"
    if added_cats:
        return f"added {added_cats}"
    if removed_cats:
        return f"removed {removed_cats}"
    return "n/a"
