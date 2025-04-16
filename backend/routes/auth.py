from apiflask import APIBlueprint
from marshmallow_dataclass import class_schema

from auth.auth_singleton import get_auth_if
from log import log_debug
from routes.schemas.auth import JWTHeaderInput, LoginInput, LoginOutput, VerifyOutput

def add_auth_bp(app):
    log_debug('ROUTES', 'Adding Authentication Blueprint')
    auth_if = get_auth_if(app)
    auth_bp = APIBlueprint('authentication', __name__)

    @auth_bp.post('/api/auth/verify')
    @auth_bp.input(class_schema(JWTHeaderInput)(), location='headers', arg_name='token')
    @auth_bp.output(VerifyOutput)
    def handle_verify(token: JWTHeaderInput):
        user = auth_if.verify_token(token.jwt_token)
        if user is None:
            return {
                'status': 'failed',
                'message': 'Invalid token',
            }
        else:
            return {
                'status': 'success',
                'message': 'Login verified successfully',
                'data': user,
            }


    @auth_bp.post('/api/auth/login')
    @auth_bp.input(class_schema(LoginInput)(), location='json', arg_name='login_input')
    @auth_bp.output(LoginOutput)
    def handle_auth(login_input: LoginInput):
        login = auth_if.check_login(login_input.username, login_input.password)
        if login is None:
            return {
                'status': 'failed',
                'message': 'Invalid credentials',
            }
        else:
            return {
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'token': login[0],
                    'user': login[1],
                }
            }

    app.register_blueprint(auth_bp)
