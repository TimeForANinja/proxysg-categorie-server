import re
import time
from typing import List, Tuple

from db.category import MutableCategory
from db.db import DBInterface
from db.url import MutableURL


class ExistingCat:
    """Class for a single category read from an existing Database file"""
    name: str
    urls: List[str]
    def __init__(self, name: str, urls: List[str]):
        self.name = name
        self.urls = urls


# TODO: input validation for both Categories and URLs
def create_in_db(db: DBInterface, new_cat_candidates: List[ExistingCat], category_prefix: str):
    """
    This method creates a DB as read from an existing file in the provided DB.

    If cats / urls already exist, we'll only map them.

    :param db: The DBInterface to use for the DB operations
    :param new_cat_candidates: The list of categories to import
    :param category_prefix: The prefix to use for the new categories
    """
    # add prefix to cats
    for cat in new_cat_candidates:
        cat.name = category_prefix + cat.name

    ##########
    # start by making sure all URLs and CATs exist
    # we already have existing code for that,
    # and that way we only need to worry about the URL to CAT mappings
    ##########

    categories = [category.name for category in new_cat_candidates]
    create_categories_db(db, categories)

    # some trickery with list(set(xxx)) to get a unique list of URLs
    urls = list(set(
        url
        for category in new_cat_candidates
        for url in category.urls
    ))
    create_urls_db(db, urls)

    ##########
    # now re-fetch the cats and urls and build the mapping list we need
    ##########

    # get existing data from db
    existing_cats = db.categories.get_all_categories()
    existing_urls = db.urls.get_all_urls()

    # Prepare bulk operations
    url_cat_mappings = []

    # Prepare URL-category mappings
    for new_cat_candidate in new_cat_candidates:
        # Find category ID
        cat = next((ec for ec in existing_cats if ec.name == new_cat_candidate.name), None)
        # then go through all URLs
        for new_url_candidate in new_cat_candidate.urls:
            # Find URL ID
            url = next((eu for eu in existing_urls if eu.hostname == new_url_candidate), None)
            # Check if there is a mapping, and if not schedule it for creation
            if cat.id not in url.categories:
                url_cat_mappings.append((url.id, cat.id))

    # Bulk create URL-category mappings
    if url_cat_mappings:
        db.url_categories.bulk_add_url_category(url_cat_mappings)


def create_categories_db(db: DBInterface, new_cats: List[str]):
    """
    This method ensures a list of categories is in the DB.

    If cats already exist, we'll simply ignore them.

    :param db: The DBInterface to use for the DB operations
    :param new_cats: The list of categories to import
    """
    # get existing data from db
    existing_cats = db.categories.get_all_categories()

    # Prepare Categories to create
    cats_to_create = []


    # Identify categories and URLs to create
    for new_cat_candidate in new_cats:
        # Check if the category exists (by name)
        cat_exists = any(ec.name == new_cat_candidate for ec in existing_cats)

        # If the category doesn't exist, prepare to create it
        if not cat_exists:
            cats_to_create.append(MutableCategory(
                name=new_cat_candidate,
                color=1,
                description=f'Imported on {time.strftime("%Y-%m-%d %H:%M:%S")}',
            ))

    # Bulk create Categories
    if cats_to_create:
        db.categories.bulk_add_category(cats_to_create)


def create_urls_db(db: DBInterface, new_urls: List[str]):
    """
    This method ensures a list of URLs is in the DB.

    If urls already exist, we'll simply ignore them.

    :param db: The DBInterface to use for the DB operations
    :param new_urls: The list of urls to import
    """
    # get existing data from db
    existing_urls = db.urls.get_all_urls()

    # Prepare URLs to create
    urls_to_create = []

    # Identify URLs that don't exist yet
    for new_url_candidate in new_urls:
        # Check if the url exists (by name)
        url_exists = any(eu.hostname == new_url_candidate for eu in existing_urls)

        # If the URL doesn't exist, prepare to create it
        if not url_exists:
            urls_to_create.append(MutableURL(
                hostname=new_url_candidate,
                description=f'Imported on {time.strftime("%Y-%m-%d %H:%M:%S")}',
            ))

    # Bulk create URLs
    if urls_to_create:
        db.urls.bulk_add_url(urls_to_create)


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
            else:
                # Add the line as a URL to the current category if it's not already there
                if clean_line not in current_cat.urls:
                    current_cat.urls.append(clean_line)

    if current_cat is not None:
        # If still inside a category when the file ends, it's an error
        raise ValueError('Syntax error: Category not properly ended with \'end\'')

    return categories, uncategorized
