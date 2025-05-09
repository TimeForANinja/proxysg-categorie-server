import copy
from typing import Optional, Tuple, Dict, Any
import requests
from flask import request

from auth.auth_user import AuthUser
from auth.auth_realm import AuthRealmInterface
from auth.util.role_map import parse_role_map, apply_role_map, RoleMap
from log import log_info, log_error, log_debug


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
    def _update_json_key(json_obj: Dict[str, Any], key: str, new_value: Any = "*") -> None:
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

            if r.status_code != 200:
                log_error( 'AUTH', f'Authentication error: SRC_IP:{request.remote_addr}', r.json())
                return None

            resp_obj = r.json()
            raw_roles = self._get_json_key(resp_obj, self.paths.get('groups'))
            mapped_roles = apply_role_map(raw_roles, self.role_map)
            log_debug( 'AUTH', f'Auth successfully: SRC_IP:{request.remote_addr}', r.json(), {'mappedRoles': mapped_roles})
            user = AuthUser(
                username = self._get_json_key(resp_obj, self.paths.get('username')),
                roles = mapped_roles,
            )

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

            if r.status_code != 200:
                log_error( 'AUTH', f'Authentication error: SRC_IP:{request.remote_addr}', r.json())
                return None

            resp_obj = r.json()
            raw_roles = self._get_json_key(resp_obj, self.paths.get('groups'))
            mapped_roles = apply_role_map(raw_roles, self.role_map)
            # !! WATCH OUT !!
            # we should never log the token
            resp_obj_clean = copy.deepcopy(resp_obj)
            resp_obj_clean['mappedRoles'] = mapped_roles
            self._update_json_key(resp_obj_clean, self.paths.get('token'), "*****")
            log_info('AUTH', f'Auth successfully: SRC_IP:{request.remote_addr}', resp_obj_clean)

            user = AuthUser(
                username = self._get_json_key(resp_obj, self.paths.get('username')),
                roles = mapped_roles,
            )
            rest_token = self._get_json_key(resp_obj, self.paths.get('token'))
            return rest_token, user
        except requests.RequestException as e:
            log_error('Auth', f'Authentication error: SRC_IP:{request.remote_addr}', e)
            return None
