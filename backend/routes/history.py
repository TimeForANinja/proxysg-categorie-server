from apiflask import APIBlueprint, APIFlask
from apiflask.fields import List, Nested
from marshmallow_dataclass import class_schema

from auth.auth_singleton import get_auth_if
from db.history import History
from db.db_singleton import get_db
from routes.schemas.generic_output import GenericOutput


class ListResponseOutput(GenericOutput):
    """Output schema for list of categories"""
    data = List(Nested(class_schema(History)()), required=True, description="List of History Events")


def add_history_bp(app: APIFlask):
    auth_if = get_auth_if(app)
    history_bp = APIBlueprint('history', __name__)

    # Route to fetch all Categories
    @history_bp.get('/api/history')
    @history_bp.doc(summary='List Change History', description='List all Changes done to the Database')
    @history_bp.output(ListResponseOutput)
    @history_bp.auth_required(auth_if.get_auth(), roles=[auth_if.AUTH_ROLES_RO])
    def get_categories():
        db_if = get_db()
        histories = db_if.history.get_history_events()
        return {
            "status": "success",
            "message": "History fetched successfully",
            "data": histories,
        }

    app.register_blueprint(history_bp)
