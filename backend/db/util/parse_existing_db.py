import re
import time
from typing import List, Tuple, Dict

from auth.auth_user import AuthUser
from db.dbmodel.category import MutableCategory
from db.dbmodel.url import MutableURL
from db.middleware.abc.db import MiddlewareDB
from log import log_debug, log_error


class ExistingCat:
    """Class for a single category read from an existing Database file"""
    name: str
    urls: List[str]
    def __init__(self, name: str, urls: List[str]):
        self.name = name
        self.urls = urls


# TODO: input validation for both Categories and URLs
def create_in_db(
    db: MiddlewareDB,
    auth: AuthUser,
    new_cat_candidates: List[ExistingCat],
    category_prefix: str
):
    """
    This method creates a DB as read from an existing file in the provided DB.

    If cats / urls already exist, we'll only map them.

    :param db: The DBInterface to use for the DB operations
    :param auth: The AuthUser to use for the DB operations
    :param new_cat_candidates: The list of categories to import
    :param category_prefix: The prefix to use for the new categories
    """
    if not new_cat_candidates:
        return

    # add prefix to cats
    for cat in new_cat_candidates:
        cat.name = category_prefix + cat.name

    ## identify all categories that are missing
    _ensure_cats_exist(db, auth, [x.name for x in new_cat_candidates])

    ## identify all urls that are missing
    new_url_candidates = [u for x in new_cat_candidates for u in x.urls]
    create_urls_db(db, auth, new_url_candidates)

    ## identify all cat -> url mappings that are missing
    missing_mappings: Dict[str, List[str]] = {}
    # fetch existing cats/urls and convert to dicts for a faster lookup
    # since we fetch after create_urls_db / _ensure_cats_exist was called, the new items should already exist
    existing_cats = db.categories.get_all_categories()
    existing_urls = db.urls.get_all_urls()
    existing_cats_by_name = {cat.name: cat for cat in existing_cats}
    existing_urls_by_hostname = {url.hostname: url for url in existing_urls}

    for cat in new_cat_candidates:
        # identify category
        cat_item = existing_cats_by_name.get(cat.name)
        if cat_item is None:
            # should never happen, since we're creating the cats above
            log_error("existing_db", "Failed to find Category", {"cat": cat.name})
            raise Exception(f'Category "{cat.name}" not found')

        for url in cat.urls:
            # identify url
            url_item = existing_urls_by_hostname.get(url)
            if url_item is None:
                # should never happen, since we're creating the urls above
                log_error("existing_db", "Failed to find URL", {"cat": cat.name, 'url': url})
                raise Exception(f'URL "{url}" not found')

            # both cat and url of mapping identified
            # add it to the list of mappings to create if it's new
            if cat_item.id not in url_item.categories:
                missing_mappings.setdefault(url_item.id, []).append(cat_item.id)

    log_debug('existing_db', 'creating missing url-category mappings', {
        'hasCategories': len(existing_cats),
        'hasUrls': len(existing_urls),
        'hasMappings': sum(len(x.categories) for x in existing_urls),
        'shouldMappings': sum(len(x.urls) for x in new_cat_candidates),
        'missingMappings': len(missing_mappings),
    })
    db.url_categories.add_url_categories(auth, missing_mappings)

def create_urls_db(db: MiddlewareDB, auth: AuthUser, new_url_candidates: List[str]):
    """
    This method ensures a list of URLs is in the DB.

    If urls already exist, we'll simply ignore them.

    :param db: The DBInterface to use for the DB operations
    :param auth: The AuthUser to use for the DB operations
    :param new_url_candidates: The list of urls to import
    """
    if not new_url_candidates:
        return

    existing_urls = db.urls.get_all_urls()
    missing_urls = _find_not_existing([x.hostname for x in existing_urls], new_url_candidates)
    log_debug('existing_db', 'creating missing urls', {
        'has': len(existing_urls),
        'should': len(new_url_candidates),
        'missing': len(missing_urls),
    })
    db.urls.add_urls(auth, [
        MutableURL(
            hostname=mu,
            description=f'Imported on {time.strftime("%Y-%m-%d %H:%M:%S")}',
        ) for mu in missing_urls
    ])

def _find_not_existing(has: List[str], should: List[str]) -> List[str]:
    return list(set(should) - set(has))

def _ensure_cats_exist(db: MiddlewareDB, auth: AuthUser, new_cat_candidates: List[str]):
    existing_cats = db.categories.get_all_categories()
    missing_cats = _find_not_existing([x.name for x in existing_cats], new_cat_candidates)
    log_debug('existing_db', 'creating missing categories', {
        'has': len(existing_cats),
        'should': len(new_cat_candidates),
        'missing': len(missing_cats),
    })
    db.categories.add_categories(auth, [
        MutableCategory(
            name=mc,
            color=1,
            description=f'Imported on {time.strftime("%Y-%m-%d %H:%M:%S")}',
        ) for mc in missing_cats
    ])

def parse_db(db_str: str, allow_uncategorized: bool = False) -> Tuple[List[ExistingCat], List[str]]:
    """
    Parses the provided database string into a list of categories with associated URLs.

    @param db_str: The database string to parse
    @param allow_uncategorized: If True, uncategorized URLs will be included in the result.
    @return: A tuple containing a list of categories and a list of uncategorized URLs.
    """

    # use sets as a quick way to deduplicate, instead of checking "is in" every time
    categories = []
    uncategorized = set()
    current_cat = None
    # utility for all URLs of the current_cat, but as a set
    current_urls = set()

    # Regex to match 'define category <cat_name>', with optional quotes around cat_name
    define_category_regex = re.compile(r'define category (?:"([^"]+)"|([^\s"]+))')

    for line in db_str.splitlines():
        # Remove comments and strip leading/trailing whitespace
        clean_line = line.split(';', 1)[0].strip()

        if not clean_line:
            # Ignore empty lines
            continue

        if current_cat is None:
            # Not inside a category
            define_match = define_category_regex.match(clean_line)
            if define_match:
                # Start a new category
                cat_name = define_match.group(1) or define_match.group(2)
                current_cat = ExistingCat(name=cat_name, urls=[])
                current_urls = set() # reset url set for the new category
            else:
                if not allow_uncategorized:
                    # Any other string outside a category is a syntax error
                    raise ValueError(f'Syntax error: Unexpected line outside category: \'{clean_line}\'')
                else:
                    uncategorized.add(clean_line)
        else:
            # Inside a category
            if clean_line.lower() == 'end':
                # End the current category
                current_cat.urls = list(current_urls)
                categories.append(current_cat)
                current_cat = None
            else:
                # no need to check for "clean_line not in current_urls"
                # since we already use a set for deduplication
                current_urls.add(clean_line)

    if current_cat is not None:
        # If still inside a category when the file ends, it's an error
        raise ValueError('Syntax error: Category not properly ended with \'end\'')

    return categories, list(uncategorized)
