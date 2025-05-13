from apiflask import APIBlueprint
from marshmallow_dataclass import class_schema

from auth.auth_singleton import get_auth_if
from db.db_singleton import get_db
from db.util.parse_existing_db import parse_db
from log import log_debug
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

        # parse db into an intermediate object
        categories, uncategorized = parse_db(existing_db.categoryDB, True)

        # push the intermediate objects to the main db
        db_if.existing.save_existing(auth.current_user, categories, existing_db.prefix, uncategorized)

        return {
            'status': 'success',
            'message': 'Database successfully loaded',
        }

    @other_bp.post('/api/commit')
    @other_bp.doc(summary='Commit Staged Changes', description='Commit all staged changes to the database')
    @other_bp.output(GenericOutput)
    @other_bp.auth_required(auth, roles=[auth_if.AUTH_ROLES_RW])
    def handle_commit():
        # Call the commit method to push staged changes to the database
        get_db().commit()
        return {
            'status': 'success',
            'message': 'All staged changes have been committed to the database'
        }

    app.register_blueprint(other_bp)
