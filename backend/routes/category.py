from apiflask import APIBlueprint, APIFlask
from db.db_singleton import get_db
from log import log_debug
from model.types.tags import Commit
from model.types.category import Category
from routes.schemas.category import ListCategoriesOutput
from routes.schemas.branch import BranchQuery

def add_category_bp(app: APIFlask):
    log_debug('ROUTES', 'Adding Category Blueprint')
    category_bp = APIBlueprint('categories', __name__)

    @category_bp.get('/api/category')
    @category_bp.doc(summary='List all Categories', description='List all Categories for a given branch')
    @category_bp.input(BranchQuery, location='query')
    @category_bp.output(ListCategoriesOutput)
    def get_categories(query_data):
        branch = query_data.get('branch')
        db = get_db()
        commit = Commit.read_branch(db.backend, branch)
        # TODO: add to "special" section of api routes
        categories = [Category.read(db.backend, h) for h in commit.head.categories]
        return {
            'status': 'success',
            'message': 'Categories fetched successfully',
            'data': categories,
        }

    app.register_blueprint(category_bp)
