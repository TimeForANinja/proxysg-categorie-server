import re
from typing import List, Optional, Set


class ExistingCat:
    """Class for a single category read from an existing Database file"""
    name: str
    urls: Set[str]

    def __init__(self, name: str):
        self.name = name
        self.urls = set()


def parse_db(db_str: str) -> List[ExistingCat]:
    """
    Parses the provided database string into a list of categories with associated URLs.

    @param db_str: The database string to parse
    @return: A list of categories (with associated URLs).
    """
    categories: List[ExistingCat] = []

    # Currently "open" Category
    current_cat: Optional[ExistingCat] = None

    # Regex to match 'define category <cat_name>', with optional quotes around cat_name
    define_category_regex = re.compile(r'^define category (?:"([^"]+)"|([^\s"]+))$')

    for line in db_str.splitlines():
        # Remove comments and strip leading/trailing whitespace
        clean_line = line.split(";", 1)[0].strip()

        if not clean_line:
            # Ignore empty lines
            continue

        if current_cat is None:
            # Not inside a category
            define_match = define_category_regex.match(clean_line)
            if define_match:
                # Start a new category
                cat_name = define_match.group(1) or define_match.group(2)
                current_cat = ExistingCat(name=cat_name)
            else:
                # Any other string outside a category is a syntax error
                raise ValueError(f'Syntax error: Unexpected line outside category: "{clean_line}"')
        else:
            # Inside a category
            if clean_line.lower() == "end":
                # End the current category
                categories.append(current_cat)
                # clear the current category for the next iteration
                current_cat = None
            else:
                current_cat.urls.add(clean_line)

    if current_cat is not None:
        # If still inside a category when the file ends, it's an error
        raise ValueError('Syntax error: Category not properly ended with "end"')

    return categories
