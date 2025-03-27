from apiflask import APIBlueprint
from db.db_singleton import get_db
from marshmallow_dataclass import class_schema
from apiflask.fields import List, Nested

from auth import get_auth, AUTH_ROLES_RW, AUTH_ROLES_RO
from db.category import MutableCategory, Category
from routes.schemas.generic_output import GenericOutput

category_bp = APIBlueprint('categories', __name__)


class CreateOrUpdateOutput(GenericOutput):
    """Output schema for create/update category"""
    data = Nested(class_schema(Category)(), required=True, description="Category")

class ListResponseOutput(GenericOutput):
    """Output schema for list of categories"""
    data = List(Nested(class_schema(Category)()), required=True, description="List of Categories")


# Route to fetch all Categories
@category_bp.get('/api/category')
@category_bp.doc(summary='List all Categories', description='List all Categories in the database')
@category_bp.output(ListResponseOutput)
@category_bp.auth_required(get_auth(), roles=[AUTH_ROLES_RO])
def get_categories():
    db_if = get_db()
    categories = db_if.categories.get_all_categories()
    return {
        "status": "success",
        "message": "Categories fetched successfully",
        "data": categories,
    }


# Route to update Category name
@category_bp.put('/api/category/<int:cat_id>')
@category_bp.doc(summary='Update Category name', description='Update the name of a Category')
@category_bp.input(class_schema(MutableCategory)(), location='json', arg_name="mut_cat")
@category_bp.output(CreateOrUpdateOutput)
@category_bp.auth_required(get_auth(), roles=[AUTH_ROLES_RW])
def update_category(cat_id: int, mut_cat: MutableCategory):
    db_if = get_db()
    new_category = db_if.categories.update_category(cat_id, mut_cat)
    db_if.history.add_history_event(f"Category {cat_id} updated")
    return {
        "status": "success",
        "message": "Category updated successfully",
        "data": new_category
    }


# Route to delete a Category
@category_bp.delete('/api/category/<int:cat_id>')
@category_bp.doc(summary="Delete a Category", description="Delete a Category using its ID")
@category_bp.output(GenericOutput)
@category_bp.auth_required(get_auth(), roles=[AUTH_ROLES_RW])
def delete_category(cat_id: int):
    db_if = get_db()
    db_if.categories.delete_category(cat_id)
    db_if.history.add_history_event(f"Category {cat_id} deleted")
    return {
        "status": "success",
        "message": "Category deleted successfully"
    }


# Route to create a new Category
@category_bp.post('/api/category')
@category_bp.doc(summary="Create a Category", description="Create a new Category with a given name")
@category_bp.input(class_schema(MutableCategory)(), location='json', arg_name="mut_cat")
@category_bp.output(CreateOrUpdateOutput)
@category_bp.auth_required(get_auth(), roles=[AUTH_ROLES_RW])
def create_category(mut_cat: MutableCategory):
    db_if = get_db()
    new_category = db_if.categories.add_category(mut_cat)
    db_if.history.add_history_event(f"Category {new_category.id} created")

    return {
        "status": "success",
        "message": "Category successfully created",
        "data": new_category
    }
