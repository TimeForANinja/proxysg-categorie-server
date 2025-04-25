import time
from typing import Optional, Tuple, List, Union, ByteString
from pyrad.client import Client
from pyrad.dictionary import Dictionary
from pyrad.packet import AccessRequest, AccessAccept

from auth.auth_user import AuthUser
from auth.auth_realm import AuthRealmInterface
from auth.util.jwt_data import TokenData
from auth.util.jwt_handler import JWTHandler
from auth.util.role_map import parse_role_map, apply_role_map, RoleMap
from auth.util.server_ip import get_server_ip


class RadiusAuthRealm(AuthRealmInterface):
    jwt: JWTHandler
    role_map: RoleMap
    client: Client

    def __init__(self, jwt: JWTHandler, server: str, secret: str, role_map: str):
        self.jwt = jwt
        self.role_map = parse_role_map(role_map)
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

        # default to no permissions
        user_roles: List[str] = []

        # (Try to) Extract groups/roles from the RADIUS response (adjust based on your server's attributes)
        # TODO: check if this works
        # Option 1: Cisco-AVPair Attribute
        if 'Cisco-AVPair' in response:
            av_pairs: Union[ByteString, List[ByteString]] = response['Cisco-AVPair']
            if isinstance(av_pairs, list):
                for pair in av_pairs:
                    if pair.startswith(b'group-name='):
                        group = pair.decode('utf-8').split('=')[1]
                        user_roles.append(group)
        # Option 2: Class Attribute
        if 'Class' in response:
            # 'Class' is a common attribute often used for roles/groups
            group_data: ByteString = response['Class']
            # Decode and split by delimiter if needed
            # it is typically stored as a byte object
            roles_from_class = group_data.decode('utf-8').split(',')
            user_roles.extend(roles_from_class)
        # Option 3: Reply-Message
        if 'Reply-Message' in response:
            # Assign the reply message as the group
            user_roles.append(response['Reply-Message'])

        # Map roles from external to Internal
        user_roles = apply_role_map(user_roles, self.role_map)

        # Login was successful; generate token and user details
        token_data = TokenData(
            username=username,
            roles=user_roles,
            realm='radius',
            date_of_creation=int(time.time())
        )
        token = self.jwt.generate_token(token_data)
        return token, token_data.to_auth_user()
