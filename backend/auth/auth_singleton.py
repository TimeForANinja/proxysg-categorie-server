import os
from apiflask import APIFlask
from flask import g

from auth.auth import AuthHandler
from auth.static.static_auth import StaticAuthRealm
from auth.radius.radius_auth import RadiusAuthHandler
from auth.util.jwt_singleton import get_jwt_handler


def get_auth_if(app: APIFlask) -> AuthHandler:
    with app.app_context():
        auth_if = getattr(g, '_auth_if', None)

        if auth_if is None:
            jwt = get_jwt_handler(app)
            realms = []

            auth_order = os.getenv('APP_AUTH_ORDER', 'local')
            for auth_type in auth_order.split(','):
                if auth_type == 'local':
                    static_user = os.getenv('APP_AUTH_LOCAL_USER', 'admin')
                    static_password = os.getenv('APP_AUTH_LOCAL_PASSWORD', 'nw_admin_2025')
                    realm = StaticAuthRealm(jwt, static_user, static_password)
                    realms.append(realm)
                elif auth_type == 'radius':
                    radius_server = os.getenv('APP_AUTH_RADIUS_SERVER')
                    radius_secret = os.getenv('APP_AUTH_RADIUS_SECRET')
                    realm = RadiusAuthHandler(jwt, radius_server, radius_secret)
                    realms.append(realm)
                else:
                    raise ValueError(f"Unsupported APP_AUTH_ORDER TYPE: {auth_type}")

            auth_if = g._auth_if = AuthHandler(realms)

        return auth_if
