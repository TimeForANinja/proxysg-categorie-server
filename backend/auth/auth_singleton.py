from apiflask import APIFlask

from auth.auth import AuthHandler
from auth.rest.rest_auth import RESTAuthRealm
from auth.static.static_auth import StaticAuthRealm
from auth.radius.radius_auth import RadiusAuthRealm
from auth.util.jwt_singleton import get_jwt_handler
from log import log_info


def get_auth_if(app: APIFlask) -> AuthHandler:
    with app.app_context():
        auth_if = app.config.get('SINGLETONS', {}).get('AUTH', None)

        if auth_if is None:
            jwt = get_jwt_handler(app)
            realms = []

            auth_order = app.config.get('AUTH', {}).get('ORDER', 'local')
            for auth_type in auth_order.split(','):
                if auth_type == 'local':
                    local_cfg: dict = app.config.get('AUTH', {}).get('LOCAL', {})
                    static_user = local_cfg.get('USER', 'admin')
                    static_password = local_cfg.get('PASSWORD', 'nw_admin_2025')
                    log_info('AUTH', 'Adding Static Realm', { 'user': static_user })
                    realm = StaticAuthRealm(jwt, static_user, static_password)
                    realms.append(realm)
                elif auth_type == 'radius':
                    radius_cfg: dict = app.config.get('AUTH', {}).get('RADIUS', {})
                    radius_server = radius_cfg.get('SERVER')
                    radius_secret = radius_cfg.get('SECRET')
                    log_info('AUTH', 'Adding Radius Realm', { 'server': radius_server })
                    realm = RadiusAuthRealm(jwt, radius_server, radius_secret)
                    realms.append(realm)
                elif auth_type == 'rest':
                    rest_cfg: dict = app.config.get('AUTH', {}).get('REST', {})
                    auth_url = rest_cfg.get('AUTH_URL')
                    verify_url = rest_cfg.get('VERIFY_URL')
                    # check for false or not false, so that we default to 'true' for all other values
                    ssl_verify = rest_cfg.get('SSL_VERIFY', 'true').lower() != 'false'
                    paths = {
                        'username': rest_cfg.get('PATH_USERNAME', 'username'),
                        'groups': rest_cfg.get('PATH_GROUPS', 'groups'),
                        'token': rest_cfg.get('PATH_TOKEN', 'token'),
                    }
                    log_info(
                        'AUTH',
                        'Adding REST Realm',
                        { 'auth_url': auth_url, 'verify_url': verify_url, 'ssl_verify': ssl_verify, 'paths': paths })
                    realm = RESTAuthRealm(auth_url, verify_url, ssl_verify, paths)
                    realms.append(realm)
                else:
                    raise ValueError(f'Unsupported APP_AUTH_ORDER TYPE: {auth_type}')

            auth_if = AuthHandler(realms)
            app.config.setdefault('SINGLETONS', {})
            app.config['SINGLETONS']['AUTH'] = auth_if

        return auth_if
