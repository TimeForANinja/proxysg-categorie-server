from typing import Optional, Tuple, Dict
import requests
from flask import request

from auth.auth_user import AuthUser
from auth.auth_realm import AuthRealmInterface
from log import log_info, log_error


class RESTAuthRealm(AuthRealmInterface):
    def __init__(
            self,
            auth_url: str,
            verify_url: str,
            ssl_verify: bool,
            paths: Dict[str, str]
    ):
        """
        :param auth_url: URL to authenticate with username / pw
        :param verify_url: URL to verify a token
        :param ssl_verify: false to disable SSL verification
        :param paths: A dict of paths for dynamic JSON key extraction
            Example: {
                "username": "user.name",
                "groups": "user.groups",
                "token": "token"
            }
        """
        self.verify_url = verify_url
        self.auth_url = auth_url
        self.ssl_verify = ssl_verify
        self.paths = paths

    @staticmethod
    def _get_json_key(json_obj: Dict, key: str) -> any:
        """
        Recursively retrieves a value from a JSON object using a dot-separated path.

        :param json_obj: The JSON object to retrieve the value from
        :param key: The dot-separated path to the value
        """
        keys = key.split(".")
        value = json_obj
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        return value

    def verify_token(self, token: str) -> Optional[AuthUser]:
        h = {
            "Authorization": f"Bearer {token}"
        }
        r = requests.get(
            self.verify_url,
            headers=h,
            verify=self.ssl_verify
        )

        if r.status_code != 200:
            log_error( "AUTH", f"Authentication error: SRC_IP:{request.remote_addr}", r.json())
            return None

        resp_obj = r.json()
        log_info( "AUTH", f"Auth successfully: SRC_IP:{request.remote_addr}", r.json())
        user = AuthUser(
            username = self._get_json_key(resp_obj, self.paths.get("username")),
            roles = self._get_json_key(resp_obj, self.paths.get("groups")),
        )

        return user

    def check_login(self, username: str, password: str) -> Optional[Tuple[str, AuthUser]]:
        payload = {
            "username": username,
            "password": password
        }

        try:
            r = requests.post(
                self.auth_url,
                json=payload,
                verify=self.ssl_verify,
            )

            if r.status_code != 200:
                log_error( "AUTH", f"Authentication error: SRC_IP:{request.remote_addr}", r.json())
                return None

            resp_obj = r.json()
            log_info("AUTH", f"Auth successfully: SRC_IP:{request.remote_addr}", resp_obj)
            user = AuthUser(
                username = self._get_json_key(resp_obj, self.paths.get("username")),
                roles = self._get_json_key(resp_obj, self.paths.get("groups")),
            )
            rest_token = self._get_json_key(resp_obj, self.paths.get("token"))
            return rest_token, user
        except requests.RequestException as e:
            log_error("Auth", f"Authentication error: SRC_IP:{request.remote_addr}", e)
            return None
