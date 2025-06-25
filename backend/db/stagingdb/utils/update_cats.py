from typing import List, Callable, Tuple

from log import log_debug


def set_categories(
    is_cats: List[str],
    should_cats: List[str],
    add_cat: Callable[[str], None],
    remove_cat: Callable[[str], None],
) -> Tuple[List[str], List[str]]:
    """
    Utility method to update categories

    :param is_cats: Current categories
    :param should_cats: New categories
    :param add_cat: Function to add a category
    :param remove_cat: Function to remove a category
    """
    added = set(should_cats) - set(is_cats)
    removed = set(is_cats) - set(should_cats)

    log_debug("DEBUG", "set_categories", {
        "is_cats": is_cats,
        "should_cats": should_cats,
        "added": added,
        "removed": removed,
    })

    for add in added:
        add_cat(add)
    for rem in removed:
        remove_cat(rem)

    return added, removed
