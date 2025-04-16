import time
from typing import Optional, Tuple
from pyrad.client import Client
from pyrad.dictionary import Dictionary
from pyrad.packet import AccessRequest, AccessAccept

from auth.auth_user import AuthUser, AUTH_ROLES_RO
from auth.auth_realm import AuthRealmInterface
from auth.util.jwt_data import TokenData
from auth.util.jwt_handler import JWTHandler
from auth.util.server_ip import get_server_ip


class RadiusAuthRealm(AuthRealmInterface):
    def __init__(self, jwt: JWTHandler, server: str, secret: str):
        self.jwt = jwt
        self.client = Client(server=server, secret=secret, dict=Dictionary('dictionary'))

    def verify_token(self, token: str) -> Optional[AuthUser]:
        token_data = self.jwt.verify_token(token)
        if not token_data:
            # Token is invalid or expired
            return None
        return token_data.to_auth_user()

    def check_login(self, username: str, password: str) -> Optional[Tuple[str, AuthUser]]:
        # Create a RADIUS Access Request packet
        request = self.client.CreateAuthPacket(
            code=AccessRequest,
            User_Name=username,
            NAS_IP_Address=get_server_ip(),
        )
        request['User-Password'] = request.PwCrypt(password) # Encrypt the password

        # Send the request to RADIUS server and await a response
        response = self.client.SendPacket(request)
        if response.code != AccessAccept:
            return None  # Login failed

        # Extract groups/roles from the RADIUS response (adjust based on your server's attributes)
        # TODO: check if this works
        if 'Class' in response:  # Common attribute used for roles/groups
            # Parse the roles/groups from the Class attribute
            group_data = response['Class']  # Typically a byte object
            user_roles = group_data.decode('utf-8').split(',')  # Decode and split by delimiter if needed
        elif 'Reply-Message' in response:  # Example: Use the Reply-Message for roles
            user_roles = [response['Reply-Message']]  # Assign the reply message as the group
        else:
            # Fallback: Use a default role if no groups are provided (optional)
            user_roles = [AUTH_ROLES_RO]

        # Login was successful; generate token and user details
        token_data = TokenData(
            username=username,
            roles=user_roles,
            realm='radius',
            date_of_creation=int(time.time())
        )
        token = self.jwt.generate_token(token_data)
        return token, token_data.to_auth_user()
