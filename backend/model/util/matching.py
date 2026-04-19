from collections import defaultdict
from typing import Optional, Iterable, List, Dict, Set

from model.types.category import Category
from model.types.mappings import ChildCategoryMapping, URLCategoryMapping
from model.types.url import URL


def best_match_url(candidate: str, urls: Iterable[URL]) -> Optional[URL]:
    """
    Finds the best matching URL from a list of URLs based on a candidate string.

    The function iterates through the list of URLs and compares the candidate string
    with each URL's hostname. It returns the URL with the longest matching hostname
    as the best match. If no match is found, it returns None.
    """
    best_url = None
    best_len = -1
    for u in urls:
        if candidate == u.url:
            # perfect match, so stop the search
            best_url = u
            break
        if candidate.endswith("." + u.url):
            # we've found part of the hostname
            score = len(u.url)
            # only save if this is the best we've found
            if score > best_len:
                best_len = score
                best_url = u
    return best_url


def unnest_categories(
        root_cat: Category,
        cat_lut: Dict[str, Category],
        mappings: List[ChildCategoryMapping],
        reverse: bool = False,
) -> List[Category]:
    """
    Recursively unnests child categories from a root category, following the provided mappings.

    :param root_cat: The root category to start unnesting from.
    :param cat_lut: A lookup table for categories.
    :param mappings: The mappings to follow.
    :param reverse: Set to true to reverse order and unnest from child to parent.
    :return: A list of categories, including the root category.
    """
    visited: Set[str] = set()
    # init with the root category, this will, however, include the root in the "visited" set
    to_visit: Set[str] = {root_cat.id}

    # convert mappings to LUT for faster access
    mapping_lut = defaultdict(list)
    for m in mappings:
        if reverse:
            mapping_lut[m.child_category_id].append(m.category_id)
        else:
            mapping_lut[m.category_id].append(m.child_category_id)

    uut = to_visit.pop()
    while uut:
        if uut not in visited:
            visited.add(uut)
            for m in mapping_lut[uut]:
                to_visit.add(m)
        uut = to_visit.pop() if len(to_visit) else None

    return [cat_lut[c] for c in visited]


def resolve_url_memberships(
        cats: List[Category],
        mappings: List[URLCategoryMapping],
) -> Dict[str, List[str]]:
    """
    Map a list of URLS (by ID) to the Categories they are Member of
    """
    url_cat_lut = defaultdict(list)
    for m in mappings:
        match_cat = next((c for c in cats if c.id == m.category_id), None)
        if match_cat:
            url_cat_lut[m.url_id].append(match_cat.id)
    return url_cat_lut
