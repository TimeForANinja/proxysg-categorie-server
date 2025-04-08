from apiflask import APIBlueprint, APIFlask
from marshmallow.fields import String
from marshmallow_dataclass import class_schema
from apiflask.fields import List, Nested
from typing import List as tList
from dataclasses import field, dataclass

from db.db_singleton import get_db
from auth.auth_singleton import get_auth_if
from db.category import MutableCategory, Category
from routes.schemas.generic_output import GenericOutput


@dataclass
class SetSubCategoriesInput:
    """Class for input schema for set sub categories"""
    categories: tList[str] = field(default_factory=list)

class CreateOrUpdateCategoryOutput(GenericOutput):
    """Output schema for create/update category"""
    data: Category = Nested(class_schema(Category)(), required=True, description="Category")

class ListCategoriesResponseOutput(GenericOutput):
    """Output schema for list of categories"""
    data: tList[Category] = List(Nested(class_schema(Category)()), required=True, description="List of Categories")

class ListSubCategoriesOutput(GenericOutput):
    """Output schema for listing Sub-Categories of a Category"""
    data: tList[str] = List(String, required=True, description="List of Sub-Categories")


def add_category_bp(app: APIFlask):
    auth_if = get_auth_if(app)
    category_bp = APIBlueprint('categories', __name__)

    # Route to fetch all Categories
    @category_bp.get('/api/category')
    @category_bp.doc(summary='List all Categories', description='List all Categories in the database')
    @category_bp.output(ListCategoriesResponseOutput)
    @category_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RO])
    def get_categories():
        db_if = get_db()
        categories = db_if.categories.get_all_categories()
        return {
            "status": "success",
            "message": "Categories fetched successfully",
            "data": categories,
        }

    # Route to update Category name
    @category_bp.put('/api/category/<string:cat_id>')
    @category_bp.doc(summary='Update Category name', description='Update the name of a Category')
    @category_bp.input(class_schema(MutableCategory)(), location='json', arg_name="mut_cat")
    @category_bp.output(CreateOrUpdateCategoryOutput)
    @category_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RW])
    def update_category(cat_id: str, mut_cat: MutableCategory):
        db_if = get_db()
        new_category = db_if.categories.update_category(cat_id, mut_cat)
        db_if.history.add_history_event(f"Category {cat_id} updated")
        return {
            "status": "success",
            "message": "Category updated successfully",
            "data": new_category
        }

    # Route to delete a Category
    @category_bp.delete('/api/category/<string:cat_id>')
    @category_bp.doc(summary="Delete a Category", description="Delete a Category using its ID")
    @category_bp.output(GenericOutput)
    @category_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RW])
    def delete_category(cat_id: str):
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
    @category_bp.output(CreateOrUpdateCategoryOutput)
    @category_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RW])
    def create_category(mut_cat: MutableCategory):
        db_if = get_db()
        new_category = db_if.categories.add_category(mut_cat)
        db_if.history.add_history_event(f"Category {new_category.id} created")

        return {
            "status": "success",
            "message": "Category successfully created",
            "data": new_category
        }

    # Route to add a Sub-Category to a Category
    @category_bp.post('/api/category/<string:cat_id>/category/<string:sub_cat_id>')
    @category_bp.doc(summary="add sub-cat to cat", description="Add the provided Category ID to the Category.Category List")
    @category_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RW])
    def add_sub_category(cat_id: str, sub_cat_id: str):
        db_if = get_db()
        db_if.sub_categories.add_sub_category(cat_id, sub_cat_id)
        db_if.history.add_history_event(f"Added sub-cat {sub_cat_id} to cat {cat_id}")
        return {
            "status": "success",
            "message": "Sub-Category successfully added to Category"
        }

    # Route to delete a Sub-Category from a Category
    @category_bp.delete('/api/category/<string:cat_id>/category/<string:sub_cat_id>')
    @category_bp.doc(summary="remove cat from token", description="Remove the provided Category ID from the Category.Category List")
    @category_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RW])
    def delete_sub_category(cat_id: str, sub_cat_id: str):
        db_if = get_db()
        db_if.sub_categories.delete_sub_category(cat_id, sub_cat_id)
        db_if.history.add_history_event(f"Removed sub-cat {sub_cat_id} from category {cat_id}")
        return {
            "status": "success",
            "message": "Sub-Category successfully removed from Category"
        }

    # Route to set Sub-Categories to a given List
    @category_bp.post('/api/category/<string:cat_id>/category')
    @category_bp.doc(summary="overwrite token categories", description="Set the Sub-Categories of a Category to the provided list")
    @category_bp.input(class_schema(SetSubCategoriesInput)(), location='json', arg_name="set_cats")
    @category_bp.output(ListSubCategoriesOutput)
    @category_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RW])
    def set_sub_categories(cat_id: str, set_cats: SetSubCategoriesInput):
        db_if = get_db()
        is_sub_cats = db_if.sub_categories.get_sub_categories_by_id(cat_id)

        added = list(set(set_cats.categories) - set(is_sub_cats))
        removed = list(set(is_sub_cats) - set(set_cats.categories))

        for cat in added:
            db_if.sub_categories.add_sub_category(cat_id, cat)
        for cat in removed:
            db_if.sub_categories.delete_sub_category(cat_id, cat)

        db_if.history.add_history_event(
            f"Updated Sub-Cats for Category {cat_id} from {','.join([str(c) for c in is_sub_cats])} to {','.join([str(c) for c in set_cats.categories])}")
        return {
            "status": "success",
            "message": "Sub-Categories successfully updated",
            "data": set_cats.categories,
        }

    app.register_blueprint(category_bp)
