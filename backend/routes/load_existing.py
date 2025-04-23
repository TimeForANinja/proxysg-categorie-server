import re
import time
from typing import List
from apiflask import APIBlueprint
from marshmallow_dataclass import class_schema

from auth.auth_singleton import get_auth_if
from db.category import MutableCategory
from db.db import DBInterface
from db.db_singleton import get_db
from db.url import MutableURL
from log import log_debug
from routes.schemas.generic_output import GenericOutput
from routes.schemas.load_existing import ExistingCat, ExistingDBInput


def create_in_db(db: DBInterface, new_cats: List[ExistingCat]):
    """
    This method creates a DB as read from an existing file in the provided DB.

    If cats / urls already exist, we'll only map them.

    :param db: The DBInterface to use for the DB operations
    :param new_cats: The list of categories to import
    """
    # get existing data from db
    existing_cats = db.categories.get_all_categories()
    existing_urls = db.urls.get_all_urls()

    # create all entries and mappings for existing customDB in db
    for new_cat in new_cats:
        # identify a cat or create a new one
        my_cat = None
        for ec in existing_cats:
            if ec.name == new_cat.name:
                my_cat = ec
                break
        if my_cat is None:
            my_cat = db.categories.add_category(MutableCategory(
                name=new_cat.name,
                color=1,
                description=f'Imported on {time.strftime("%Y-%m-%d %H:%M:%S")}',
            ))

        for new_url in new_cat.urls:
            # identify url or create a new one
            my_url = None
            for eu in existing_urls:
                if eu.hostname == new_url:
                    my_url = eu
                    break
            if my_url is None:
                my_url = db.urls.add_url(MutableURL(
                    hostname=new_url,
                    description=f'Imported on {time.strftime("%Y-%m-%d %H:%M:%S")}',
                ))
                # add to existing URLs
                # this helps to not create URLs multiple times
                # if they exist in multiple cats
                existing_urls.append(my_url)

            # map url to cat, if not already done
            if not my_cat.id in my_url.categories:
                db.url_categories.add_url_category(my_url.id, my_cat.id)

def parse_db(db_str: str) -> List[ExistingCat]:
    """
    Parses the provided database string into a list of categories with associated URLs.
    """
    categories = []
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
                # Any other string outside a category is a syntax error
                raise ValueError(f'Syntax error: Unexpected line outside category: \'{clean_line}\'')
        else:
            # Inside a category
            if clean_line.lower() == 'end':
                # End the current category
                categories.append(current_cat)
                current_cat = None
            else:
                # Add the line as a URL to the current category
                current_cat.urls.append(clean_line)

    if current_cat is not None:
        # If still inside a category when the file ends, it's an error
        raise ValueError('Syntax error: Category not properly ended with \'end\'')

    return categories


def add_other_bp(app):
    log_debug('ROUTES', 'Adding other Blueprint')
    auth_if = get_auth_if(app)
    auth = auth_if.get_auth()
    other_bp = APIBlueprint('other', __name__)

    # Route to upload an existing category db
    @other_bp.post('/api/upload_existing_db')
    @other_bp.doc(summary='Upload existing DB', description='Upload an existing database to the server')
    @other_bp.input(class_schema(ExistingDBInput)(), location='json', arg_name='existing_db')
    @other_bp.output(GenericOutput)
    @other_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def load_existing(existing_db: ExistingDBInput):
        db_if = get_db()

        # parse db into an intermediate object
        categories = parse_db(existing_db.categoryDB)
        # ush the intermediate objects to the main db
        create_in_db(db_if, categories)

        db_if.history.add_history_event('existing db imported', auth.current_user, [], [], [])

        return {
            'status': 'success',
            'message': 'Database successfully loaded',
        }

    app.register_blueprint(other_bp)
