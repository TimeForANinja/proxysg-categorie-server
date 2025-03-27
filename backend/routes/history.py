from apiflask import APIBlueprint
from apiflask.fields import List, Nested
from marshmallow_dataclass import class_schema

from auth import get_auth, AUTH_ROLES_RO
from db.history import History
from db.db_singleton import get_db
from routes.schemas.generic_output import GenericOutput

history_bp = APIBlueprint('history', __name__)


class ListResponseOutput(GenericOutput):
    """Output schema for list of categories"""
    data = List(Nested(class_schema(History)()), required=True, description="List of History Events")


# Route to fetch all Categories
@history_bp.get('/api/history')
@history_bp.doc(summary='List Change History', description='List all Changes done to the Database')
@history_bp.output(ListResponseOutput)
@history_bp.auth_required(get_auth(), roles=[AUTH_ROLES_RO])
def get_categories():
    db_if = get_db()
    histories = db_if.history.get_history_events()
    return {
        "status": "success",
        "message": "History fetched successfully",
        "data": histories,
    }

