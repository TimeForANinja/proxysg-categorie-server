from apiflask import APIBlueprint
from marshmallow_dataclass import class_schema

from auth.auth_singleton import get_auth_if
from db.db_singleton import get_db
from db.util.parse_existing_db import parse_db, create_in_db, create_urls_db
from log import log_debug, log_info
from routes.schemas.generic_output import GenericOutput
from routes.schemas.load_existing import ExistingDBInput


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

        log_info("API", "Step 01")
        # parse db into an intermediate object
        categories, uncategorized = parse_db(existing_db.categoryDB, True)

        log_info("API","Step 02")
        # push the intermediate objects to the main db
        create_in_db(db_if, categories, existing_db.prefix)
        log_info("API","Step 03")
        create_urls_db(db_if, uncategorized)
        log_info("API","Step 04")

        db_if.history.add_history_event('existing db imported', auth.current_user, [], [], [])

        return {
            'status': 'success',
            'message': 'Database successfully loaded',
        }

    app.register_blueprint(other_bp)
