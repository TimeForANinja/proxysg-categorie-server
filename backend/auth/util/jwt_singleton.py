import os
from apiflask import APIFlask
from flask import g

from auth.util.jwt_handler import JWTHandler


def get_jwt_handler(app: APIFlask) -> JWTHandler:
    with app.app_context():
        jwt_handler = getattr(g, '_jwt', None)

        if jwt_handler is None:
            lifetime = int(os.getenv('APP_JWT_LIFETIME'))
            secret_key = os.getenv('APP_JWT_SECRET')

            jwt_handler = g._jwt = JWTHandler(lifetime, secret_key)

        return jwt_handler
