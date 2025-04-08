import os
from apiflask import APIFlask
from flask import g

from auth.auth import AuthHandler
from auth.static.static_auth import StaticAuthRealm


def get_auth_if(app: APIFlask) -> AuthHandler:
    with app.app_context():
        auth_if = getattr(g, '_auth_if', None)

        if auth_if is None:
            realms = []

            auth_order = os.getenv('APP_AUTH_ORDER', 'local')
            for auth_type in auth_order.split(','):
                if auth_type == 'local':
                    auth_user = os.getenv('APP_AUTH_LOCAL_USER', 'admin')
                    auth_password = os.getenv('APP_AUTH_LOCAL_PASSWORD', 'nw_admin_2025')
                    realm = StaticAuthRealm(auth_user, auth_password)
                    realms.append(realm)
                else:
                    raise ValueError(f"Unsupported APP_AUTH_TYPE: {auth_type}")

            auth_if = g._auth_if = AuthHandler(realms)

        return auth_if
