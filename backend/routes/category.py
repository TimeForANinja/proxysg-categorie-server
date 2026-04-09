from apiflask import APIBlueprint, APIFlask
from db.db_singleton import get_db
from log import log_debug
from routes.schemas.category import ListCategoriesOutput, CategoryOutput, ListMembersOutput, MemberOutput, \
    category_input_schema, CategoryInput, member_input_schema, MemberInput
from routes.schemas.generic_output import GenericOutput


def add_category_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding Category Blueprint')
    category_bp = APIBlueprint('Categories', __name__)


    @category_bp.get('/api/branch/<branch>/category')
    @category_bp.doc(summary='List all Categories', description='List all Categories for a given branch', tags=['Categories'])
    @category_bp.output(ListCategoriesOutput)
    def get_categories(branch: str):
        db = get_db()
        categories = db.specials.fetch_categories(branch)
        return {
            'status': 'success',
            'message': 'Categories fetched successfully',
            'data': categories,
        }

    @category_bp.post('/api/branch/<branch>/category')
    @category_bp.doc(summary='Create a Category', description='Create a new Category for a given branch', tags=['Categories'])
    @category_bp.input(category_input_schema, location='json', arg_name='category_data')
    @category_bp.output(CategoryOutput)
    def create_category(branch: str, category_data: CategoryInput):
        db = get_db()
        category = db.categories.add_category(branch, category_data.name)
        return {
            'status': 'success',
            'message': 'Category created successfully',
            'data': category,
        }

    @category_bp.delete('/api/branch/<branch>/category/<category_id>')
    @category_bp.doc(summary='Delete a Category', description='Delete a Category by ID for a given branch', tags=['Categories'])
    @category_bp.output(GenericOutput)
    def delete_category(branch: str, category_id: str):
        db = get_db()
        db.categories.delete_category(branch, category_id)
        return {
            'status': 'success',
            'message': 'Category deleted successfully',
        }


    @category_bp.get('/api/branch/<branch>/category/<category_id>/url')
    @category_bp.doc(summary='List all URLs in Category', description='List all URLs and their constraints for a given category', tags=['Categories', 'Urls'])
    @category_bp.output(ListMembersOutput)
    def get_category_urls(branch: str, category_id: str):
        db = get_db()
        members = db.categories.get_category_members(branch, category_id)
        return {
            'status': 'success',
            'message': 'Category members fetched successfully',
            'data': members,
        }

    @category_bp.post('/api/branch/<branch>/category/<category_id>/url')
    @category_bp.doc(summary='Add URL to Category', description='Add a new URL member to a category', tags=['Categories', 'Urls'])
    @category_bp.input(member_input_schema, location='json', arg_name='member_data')
    @category_bp.output(MemberOutput)
    def add_category_url(branch: str, category_id: str, member_data: MemberInput):
        db = get_db()
        member = db.categories.add_member(
            branch,
            category_id,
            member_data.url,
            member_data.constraint,
        )
        return {
            'status': 'success',
            'message': 'URL added to category successfully',
            'data': member,
        }

    @category_bp.delete('/api/branch/<branch>/category/<category_id>/url/<url>')
    @category_bp.doc(summary='Remove URL from Category', description='Remove a URL member from a category', tags=['Categories', 'Urls'])
    @category_bp.output(GenericOutput)
    def delete_category_url(branch: str, category_id: str, url: str):
        db = get_db()
        db.categories.delete_member(branch, category_id, url)
        return {
            'status': 'success',
            'message': 'URL removed from category successfully',
        }

    app.register_blueprint(category_bp)
