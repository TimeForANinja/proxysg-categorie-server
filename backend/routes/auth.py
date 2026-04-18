from apiflask import APIBlueprint

from auth.auth_singleton import get_auth_if
from db.db_singleton import get_db
from util.log import log_debug
from model.util.error import ModelError
from routes.schemas.auth import jwt_header_schema, JWTHeaderInput, VerifyOutput, verify_output_schema, LoginOutput, \
    login_output_schema, LoginInput, login_input_schema, LoginOutputData
from routes.schemas.error import ErrorResponse, OutCanError


def add_auth_bp(app):
    log_debug('ROUTES', 'Adding Authentication Blueprint')
    auth_if = get_auth_if(app)
    auth_bp = APIBlueprint('authentication', __name__)

    @auth_bp.post('/api/auth/verify')
    @auth_bp.input(jwt_header_schema, location='headers', arg_name='token')
    @auth_bp.output(verify_output_schema)
    def handle_verify(token: JWTHeaderInput) -> OutCanError[VerifyOutput]:
        user = auth_if.verify_token(token.jwt_token)
        if user is None:
            return ErrorResponse(ModelError('Invalid token'))
        else:
            return VerifyOutput(
                status='success',
                message='Token verified successfully',
                data=user,
            )

    @auth_bp.post('/api/auth/login')
    @auth_bp.input(login_input_schema, location='json', arg_name='login_input')
    @auth_bp.output(login_output_schema)
    def handle_auth(login_input: LoginInput) -> OutCanError[LoginOutput]:
        result = auth_if.check_login(login_input.username, login_input.password)
        if result is None:
            return ErrorResponse(ModelError('Invalid credentials'))
        else:
            # check if we need to init
            db = get_db()
            db.core.check_init(result[1])

            # reply
            return LoginOutput(
                status='success',
                message='Login successful',
                data=LoginOutputData(
                    token=result[0],
                    user=result[1],
                )
            )

    app.register_blueprint(auth_bp)
