from apiflask import APIBlueprint
from marshmallow.fields import Integer

from db.db_singleton import get_db
from marshmallow_dataclass import class_schema
from apiflask.fields import List, Nested
from typing import List as tList
from dataclasses import field, dataclass

from db.url import MutableURL, URL
from routes.schemas.generic_output import GenericOutput

url_bp = APIBlueprint('url', __name__)


@dataclass
class SetCategoriesInput:
    """Class for input schema for set categories"""
    categories: tList[int] = field(default_factory=list)

class CreateOrUpdateOutput(GenericOutput):
    """Output schema for create/update url"""
    data = Nested(class_schema(URL)(), required=True, description="URL")

class ListResponseOutput(GenericOutput):
    """Output schema for list of URL"""
    data = List(Nested(class_schema(URL)()), required=True, description="List of URLs")

class ListCategoriesOutput(GenericOutput):
    """Output schema for listing Categories of a URL"""
    data = List(Integer, required=True, description="List of Categories")


# Route to fetch all URLs
@url_bp.get('/api/url')
@url_bp.doc(summary='List all URLs', description='List all URLs in the database')
@url_bp.output(ListResponseOutput)
def get_urls():
    db_if = get_db()
    urls = db_if.urls.get_all_urls()
    return {
        "status": "success",
        "message": "URLs fetched successfully",
        "data": urls,
    }


# Route to update URL name
@url_bp.put('/api/url/<int:url_id>')
@url_bp.doc(summary='Update URL name', description='Update the name of a URL')
@url_bp.input(class_schema(MutableURL)(), location='json', arg_name="mut_url")
@url_bp.output(CreateOrUpdateOutput)
def update_url(url_id: int, mut_url: MutableURL):
    db_if = get_db()
    new_url = db_if.urls.update_url(url_id, mut_url)
    db_if.history.add_history_event(f"URL {url_id} updated")
    return {
        "status": "success",
        "message": "URL updated successfully",
        "data": new_url
    }


# Route to delete a URL
@url_bp.delete('/api/url/<int:url_id>')
@url_bp.doc(summary="Delete a URL", description="Delete a URL using its ID")
@url_bp.output(GenericOutput)
def delete_url(url_id: int):
    db_if = get_db()
    db_if.urls.delete_url(url_id)
    db_if.history.add_history_event(f"URL {url_id} deleted")
    return {
        "status": "success",
        "message": "url_id deleted successfully"
    }


# Route to create a new URL
@url_bp.post('/api/url')
@url_bp.doc(summary="Create a new URL", description="Create a new URL with a given name")
@url_bp.input(class_schema(MutableURL)(), location='json', arg_name="mut_url")
@url_bp.output(CreateOrUpdateOutput)
def create_url(mut_url: MutableURL):
    db_if = get_db()
    new_url = db_if.urls.add_url(mut_url)
    db_if.history.add_history_event(f"URL {new_url.id} created")

    return {
        "status": "success",
        "message": "URL successfully created",
        "data": new_url
    }


# Route to add a Category to a URL
@url_bp.post('/api/url/<int:url_id>/category/<int:cat_id>')
@url_bp.doc(summary="add cat to url", description="Add the provided Category ID to the URL.Category List")
def add_token_category(url_id: int, cat_id: int):
    db_if = get_db()
    db_if.url_categories.add_url_category(url_id, cat_id)
    db_if.history.add_history_event(f"Added cat {cat_id} to url {url_id}")
    return {
        "status": "success",
        "message": "Category successfully added to URL"
    }


# Route to delete a Category from a URL
@url_bp.delete('/api/url/<int:url_id>/category/<int:cat_id>')
@url_bp.doc(summary="remove cat from url", description="Remove the provided Category ID from the URL.Category List")
def delete_token_category(url_id: int, cat_id: int):
    db_if = get_db()
    db_if.url_categories.delete_url_category(url_id, cat_id)
    db_if.history.add_history_event(f"Removed cat {cat_id} from url {url_id} deleted")
    return {
        "status": "success",
        "message": "Category successfully removed from URL"
    }


# Route to set Categories to a given List
@url_bp.post('/api/url/<int:url_id>/category')
@url_bp.doc(summary="overwrite url categories", description="Set the Categories of a URL to the provided list")
@url_bp.input(class_schema(SetCategoriesInput)(), location='json', arg_name="set_cats")
@url_bp.output(ListCategoriesOutput)
def set_url_categories(url_id: int, set_cats: SetCategoriesInput):
    db_if = get_db()
    is_cats = db_if.url_categories.get_url_categories_by_url(url_id)

    added = list(set(set_cats.categories) - set(is_cats))
    removed = list(set(is_cats) - set(set_cats.categories))

    for cat in added:
        db_if.url_categories.add_url_category(url_id, cat)
    for cat in removed:
        db_if.url_categories.delete_url_category(url_id, cat)

    db_if.history.add_history_event(f"Updated Cats for URL {url_id} from {','.join([str(c) for c in is_cats])} to {','.join([str(c) for c in set_cats.categories])}")
    return {
        "status": "success",
        "message": "URL Categories successfully updated",
        "data": set_cats.categories,
    }
