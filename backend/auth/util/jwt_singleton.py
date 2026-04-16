from apiflask import APIFlask

from auth.util.jwt_handler import JWTHandler


def get_jwt_handler(app: APIFlask) -> JWTHandler:
    with app.app_context():
        jwt_handler = app.config.get('SINGLETONS', {}).get('JWT', None)

        if jwt_handler is None:
            lifetime = int(app.config.get('JWT', {}).get('LIFETIME', '21600'))
            secret_key = app.config.get('JWT', {}).get('SECRET')

            jwt_handler = JWTHandler(lifetime, secret_key)
            app.config.setdefault('SINGLETONS', {})
            app.config['SINGLETONS']['JWT'] = jwt_handler

        return jwt_handler
