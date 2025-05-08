from apiflask import APIBlueprint, APIFlask
from marshmallow_dataclass import class_schema

from db.db_singleton import get_db
from auth.auth_singleton import get_auth_if
from db.abc.category import MutableCategory
from log import log_debug
from routes.schemas.generic_output import GenericOutput
from routes.schemas.category import ListCategoriesResponseOutput, CreateOrUpdateCategoryOutput, ListSubCategoriesOutput, SetSubCategoriesInput


def add_category_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding Category Blueprint')
    auth_if = get_auth_if(app)
    auth = auth_if.get_auth()
    category_bp = APIBlueprint('categories', __name__)

    # Route to fetch all Categories
    @category_bp.get('/api/category')
    @category_bp.doc(summary='List all Categories', description='List all Categories in the database')
    @category_bp.output(ListCategoriesResponseOutput)
    @category_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RO])
    def get_categories():
        db_if = get_db()
        categories = db_if.categories.get_all_categories()
        return {
            'status': 'success',
            'message': 'Categories fetched successfully',
            'data': categories,
        }

    # Route to update Category name
    @category_bp.put('/api/category/<string:cat_id>')
    @category_bp.doc(summary='Update Category name', description='Update the name of a Category')
    @category_bp.input(class_schema(MutableCategory)(), location='json', arg_name='mut_cat')
    @category_bp.output(CreateOrUpdateCategoryOutput)
    @category_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def update_category(cat_id: str, mut_cat: MutableCategory):
        new_category = get_db().categories.update_category(auth.current_user, cat_id, mut_cat)
        return {
            'status': 'success',
            'message': 'Category updated successfully',
            'data': new_category
        }

    # Route to delete a Category
    @category_bp.delete('/api/category/<string:cat_id>')
    @category_bp.doc(summary='Delete a Category', description='Delete a Category using its ID')
    @category_bp.output(GenericOutput)
    @category_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def delete_category(cat_id: str):
        get_db().categories.delete_category(auth.current_user, cat_id)
        return {
            'status': 'success',
            'message': 'Category deleted successfully'
        }

    # Route to create a new Category
    @category_bp.post('/api/category')
    @category_bp.doc(summary='Create a Category', description='Create a new Category with a given name')
    @category_bp.input(class_schema(MutableCategory)(), location='json', arg_name='mut_cat')
    @category_bp.output(CreateOrUpdateCategoryOutput)
    @category_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def create_category(mut_cat: MutableCategory):
        new_category = get_db().categories.add_category(auth.current_user, mut_cat)
        return {
            'status': 'success',
            'message': 'Category successfully created',
            'data': new_category
        }

    # Route to add a Sub-Category to a Category
    @category_bp.post('/api/category/<string:cat_id>/category/<string:sub_cat_id>')
    @category_bp.doc(summary='add sub-cat to cat', description='Add the provided Category ID to the Category.Category List')
    @category_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def add_sub_category(cat_id: str, sub_cat_id: str):
        get_db().sub_categories.add_sub_category(auth.current_user, cat_id, sub_cat_id)
        return {
            'status': 'success',
            'message': 'Sub-Category successfully added to Category'
        }

    # Route to delete a Sub-Category from a Category
    @category_bp.delete('/api/category/<string:cat_id>/category/<string:sub_cat_id>')
    @category_bp.doc(summary='remove cat from token', description='Remove the provided Category ID from the Category.Category List')
    @category_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def delete_sub_category(cat_id: str, sub_cat_id: str):
        get_db().sub_categories.delete_sub_category(auth.current_user, cat_id, sub_cat_id)
        return {
            'status': 'success',
            'message': 'Sub-Category successfully removed from Category'
        }

    # Route to set Sub-Categories to a given List
    @category_bp.post('/api/category/<string:cat_id>/category')
    @category_bp.doc(summary='overwrite token categories', description='Set the Sub-Categories of a Category to the provided list')
    @category_bp.input(class_schema(SetSubCategoriesInput)(), location='json', arg_name='set_cats')
    @category_bp.output(ListSubCategoriesOutput)
    @category_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def set_sub_categories(cat_id: str, set_cats: SetSubCategoriesInput):
        get_db().sub_categories.set_sub_categories(auth.current_user, cat_id, set_cats.categories)
        return {
            'status': 'success',
            'message': 'Sub-Categories successfully updated',
            'data': set_cats.categories,
        }

    app.register_blueprint(category_bp)
