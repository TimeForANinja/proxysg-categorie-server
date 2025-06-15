import re
import time
from typing import List, Tuple

from auth.auth_user import AuthUser
from db.abc.category import MutableCategory, Category
from db.abc.url import MutableURL, URL
from db.stagingdb.category_db import StagingDBCategory
from db.stagingdb.url_category_db import StagingDBURLCategory
from db.stagingdb.url_db import StagingDBURL


class ExistingCat:
    """Class for a single category read from an existing Database file"""
    name: str
    urls: List[str]
    def __init__(self, name: str, urls: List[str]):
        self.name = name
        self.urls = urls


# TODO: input validation for both Categories and URLs
def create_in_db(
        db_url: StagingDBURL,
        db_cats: StagingDBCategory,
        db_url_cats: StagingDBURLCategory,
        auth: AuthUser,
        new_cat_candidates: List[ExistingCat],
        category_prefix: str
    ):
    """
    This method creates a DB as read from an existing file in the provided DB.

    If cats / urls already exist, we'll only map them.

    :param db_url: The StagingDBURL to use for the DB operations
    :param db_cats: The StagingDBCategory to use for the DB operations
    :param db_url_cats: The StagingDBURLCategory to use for the DB operations
    :param auth: The AuthUser to use for the DB operations
    :param new_cat_candidates: The list of categories to import
    :param category_prefix: The prefix to use for the new categories
    """
    # add prefix to cats
    for cat in new_cat_candidates:
        cat.name = category_prefix + cat.name

    # get existing data from db
    existing_cats = db_cats.get_all_categories()
    existing_urls = db_url.get_all_urls()

    # create all entries and mappings for existing customDB in db
    for new_cat_candidate in new_cat_candidates:
        # identify a cat or create a new one
        new_cat, cat_created = _find_or_create_cat(db_cats, auth, new_cat_candidate, existing_cats)
        if cat_created:
            existing_cats.append(new_cat)

        for new_url_candidate in new_cat_candidate.urls:
            # identify url or create a new one
            new_url, url_created = _find_or_create_url(db_url, auth, new_url_candidate, existing_urls)
            if url_created:
                existing_urls.append(new_url)

            # map url to cat, if not already done
            if not new_cat.id in new_url.categories:
                db_url_cats.add_url_category(auth, new_url.id, new_cat.id)

def create_urls_db(db_url: StagingDBURL, auth: AuthUser, new_urls: List[str]):
    """
    This method ensures a list of URLs is in the DB.

    If urls already exist, we'll simply ignore them.

    :param db_url: The DBInterface to use for the DB operations
    :param auth: The AuthUser to use for the DB operations
    :param new_urls: The list of urls to import
    """
    # get existing data from db
    existing_urls = db_url.get_all_urls()

    for new_url_candidate in new_urls:
        # identify url or create a new one
        new_url, url_created = _find_or_create_url(db_url, auth, new_url_candidate, existing_urls)
        if url_created:
            existing_urls.append(new_url)

def _find_or_create_cat(db_cats: StagingDBCategory, auth: AuthUser, new_cat_candidate: ExistingCat, existing_cats: List[Category]) -> Tuple[Category, bool]:
    """
    Utility method to find or create a category in the DB.
    It returns the category and a boolean indicating if it was created or not.

    :param db_cats: The StagingDBCategory to use for the DB operations
    :param auth: The AuthUser to use for the DB operations
    :param new_cat_candidate: The category to import
    :param existing_cats: The list of existing categories to check against
    :return: A tuple containing the category and a boolean indicating if it was created or not.
    """
    for ec in existing_cats:
        if ec.name == new_cat_candidate.name:
            return ec, False
    new_cat = db_cats.add_category(auth, MutableCategory(
        name=new_cat_candidate.name,
        color=1,
        description=f'Imported on {time.strftime("%Y-%m-%d %H:%M:%S")}',
    ))
    return new_cat, True

def _find_or_create_url(db_url: StagingDBURL, auth: AuthUser, new_url_candidate: str, existing_urls: List[URL]) -> Tuple[URL, bool]:
    """
    Utility method to find or create a URL in the DB.
    It returns the URL and a boolean indicating if it was created or not.

    :param db_url: The StagingDBURL to use for the DB operations
    :param auth: The AuthUser to use for the DB operations
    :param new_url_candidate: The URL to import
    :param existing_urls: The list of existing URLs to check against
    :return: A tuple containing the URL and a boolean indicating if it was created or not.
    """
    for eu in existing_urls:
        if eu.hostname == new_url_candidate:
            return eu, False
    # not found, so create a new one
    new_url = db_url.add_url(auth, MutableURL(
        hostname=new_url_candidate,
        description=f'Imported on {time.strftime("%Y-%m-%d %H:%M:%S")}',
    ))
    return new_url, True

def parse_db(db_str: str, allow_uncategorized: bool = False) -> Tuple[List[ExistingCat], List[str]]:
    """
    Parses the provided database string into a list of categories with associated URLs.

    @param db_str: The database string to parse
    @param allow_uncategorized: If True, uncategorized URLs will be included in the result.
    @return: A tuple containing a list of categories and a list of uncategorized URLs.
    """
    categories = []
    uncategorized = []
    current_cat = None

    # Regex to match 'define category <cat_name>', with optional quotes around cat_name
    define_category_regex = re.compile(r'define category (?:"([^"]+)"|([^\s"]+))')

    for line in db_str.split('\n'):
        # Remove comments and strip leading/trailing whitespace
        clean_line = line.split(';')[0].strip()

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
            else:
                if not allow_uncategorized:
                    # Any other string outside a category is a syntax error
                    raise ValueError(f'Syntax error: Unexpected line outside category: \'{clean_line}\'')
                else:
                    uncategorized.append(clean_line)
        else:
            # Inside a category
            if clean_line.lower() == 'end':
                # End the current category
                categories.append(current_cat)
                current_cat = None
            elif clean_line not in current_cat.urls:
                # Add the line as a URL to the current category if it's not already in there
                current_cat.urls.append(clean_line)

    if current_cat is not None:
        # If still inside a category when the file ends, it's an error
        raise ValueError('Syntax error: Category not properly ended with \'end\'')

    return categories, uncategorized
