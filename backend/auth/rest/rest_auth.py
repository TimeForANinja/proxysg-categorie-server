import copy
from typing import Optional, Tuple, Dict, Any
import requests
from flask import request

from auth.auth_user import AuthUser
from auth.auth_realm import AuthRealmInterface
from auth.util.role_map import parse_role_map, apply_role_map, RoleMap
from log import log_info, log_error
from apiflask import APIFlask


class RESTAuthRealm(AuthRealmInterface):
    verify_url: str
    auth_url: str
    ssl_verify: bool
    paths: Dict[str, str]
    role_map: RoleMap

    def __init__(
        self,
        auth_url: str,
        verify_url: str,
        ssl_verify: bool,
        paths: Dict[str, str],
        role_map: str,
    ):
        """
        :param auth_url: URL to authenticate with username / pw
        :param verify_url: URL to verify a token
        :param ssl_verify: false to disable SSL verification
        :param paths: A dict of paths for dynamic JSON key extraction
            Example: {
                'username': 'user.name',
                'groups': 'user.groups',
                'token': 'token'
            }
        :param role_map: A string of role mappings in the format:
        """
        self.verify_url = verify_url
        self.auth_url = auth_url
        self.ssl_verify = ssl_verify
        self.paths = paths
        self.role_map = parse_role_map(role_map)

    @staticmethod
    def _get_json_key(json_obj: Dict[str, Any], key: str) -> Any:
        """
        Recursively retrieves a value from a JSON object using a dot-separated path.

        :param json_obj: The JSON object to retrieve the value from
        :param key: The dot-separated path to the value
        """
        keys = key.split('.')
        value = json_obj
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # If the path is invalid, return none
                return None
        return value

    @staticmethod
    def _update_json_key(json_obj: Dict[str, Any], key: str, new_value: Any = "*"):
        """
        Recursively updates a key's value in a JSON object using a dot-separated path.

        :param json_obj: The JSON object to modify
        :param key: The dot-separated path to the key to be updated
        :param new_value: The value to set for the specified key (default is "*")
        """
        keys = key.split('.')
        value = json_obj

        # traverse to the second-to-last level
        for k in keys[:-1]:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # If the path is invalid, do nothing
                return

        # Update the value of the final key
        if isinstance(value, dict):
            value[keys[-1]] = new_value

    def _process_auth_response(self, response) -> Tuple[Optional[str], Optional[AuthUser]]:
        """
        Process authentication response and extract user information.

        :param response: The response object from the authentication request
        :return: A tuple of (rest_token, AuthUser), where rest_token may be None if not present
        """
        if response.status_code != 200:
            log_error('AUTH', f'Authentication error: SRC_IP:{request.remote_addr}', response.json())
            return None, None

        resp_obj = response.json()
        raw_roles = self._get_json_key(resp_obj, self.paths.get('groups'))
        mapped_roles = apply_role_map(raw_roles, self.role_map)

        user = AuthUser(
            username=self._get_json_key(resp_obj, self.paths.get('username')),
            roles=mapped_roles,
        )

        # Always extract the token (or return "None" if not present)
        rest_token = self._get_json_key(resp_obj, self.paths.get('token'))

        # Create a clean copy for logging (without the token)
        resp_obj_clean = copy.deepcopy(resp_obj)
        resp_obj_clean['mappedRoles'] = mapped_roles
        self._update_json_key(resp_obj_clean, self.paths.get('token'), "*****")
        log_info('AUTH', f'Auth successfully: SRC_IP:{request.remote_addr}', resp_obj_clean)

        return rest_token, user

    def verify_token(self, token: str) -> Optional[AuthUser]:
        payload = {
            'token': token,
        }

        try:
            r = requests.post(
                self.verify_url,
                verify=self.ssl_verify,
                json=payload,
            )

            _, user = self._process_auth_response(r)
            return user
        except requests.RequestException as e:
            log_error('Auth', f'Authentication error: SRC_IP:{request.remote_addr}', e)
            return None

    def check_login(self, username: str, password: str) -> Optional[Tuple[str, AuthUser]]:
        payload = {
            'username': username,
            'password': password
        }

        try:
            r = requests.post(
                self.auth_url,
                json=payload,
                verify=self.ssl_verify,
            )

            return self._process_auth_response(r)
        except requests.RequestException as e:
            log_error('Auth', f'Authentication error: SRC_IP:{request.remote_addr}', e)
            return None


# Plugin API
def auth_fits(app: APIFlask, auth_type: str) -> bool:
    """
    Return True if this module handles the provided auth_type entry from AUTH.ORDER.
    """
    return auth_type.strip().lower() == 'rest'


def build_auth_realm(app: APIFlask, _jwt_unused) -> AuthRealmInterface:
    """
    Build and return the StaticAuthRealm using values from app.config.
    """
    # REST does not use local JWT; it defers to remote; still conform to signature
    rest_cfg = app.config.get('AUTH', {}).get('REST', {})
    auth_url = rest_cfg.get('AUTH_URL')
    verify_url = rest_cfg.get('VERIFY_URL')
    ssl_verify: bool = str(rest_cfg.get('SSL_VERIFY', 'true')).lower() != 'false'
    rest_role_map = rest_cfg.get('ROLE_MAP', "")
    paths = {
        'username': rest_cfg.get('PATH_USERNAME', 'username'),
        'groups': rest_cfg.get('PATH_GROUPS', 'groups'),
        'token': rest_cfg.get('PATH_TOKEN', 'token'),
    }
    log_info('AUTH', 'Adding REST Realm', {
        'auth_url': auth_url,
        'verify_url': verify_url,
        'ssl_verify': ssl_verify,
        'paths': paths,
    })
    return RESTAuthRealm(auth_url, verify_url, ssl_verify, paths, rest_role_map)
