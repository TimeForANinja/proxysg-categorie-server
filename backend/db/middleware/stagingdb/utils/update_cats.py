from typing import List, Callable, Tuple

from log import log_debug


def analyse_set_categories(
    is_cats: List[str],
    should_cats: List[str],
) -> Tuple[List[str], List[str]]:
    """
    Utility to convert from "set categories" to added/removed categories.

    :param is_cats: Current categories
    :param should_cats: New categories
    :return: Tuple of added and removed categories
    """
    added = list(set(should_cats) - set(is_cats))
    removed = list(set(is_cats) - set(should_cats))

    return added, removed


def set_categories(
    is_cats: List[str],
    should_cats: List[str],
    add_cat: Callable[[str], None],
    remove_cat: Callable[[str], None],
    dry_run: bool,
) -> Tuple[List[str], List[str]]:
    """
    Utility method to update categories

    :param is_cats: Current categories
    :param should_cats: New categories
    :param add_cat: Function to add a category
    :param remove_cat: Function to remove a category
    :param dry_run: Whether to perform a dry run (no changes are made to the database)
    :return: Tuple of added and removed categories
    """
    added, removed = analyse_set_categories(is_cats, should_cats)

    if not dry_run:
        for x in added: add_cat(x)
        for x in removed: remove_cat(x)

    return added, removed
