import jwt
import datetime
from typing import Optional

from auth.util.jwt_data import TokenData


class JWTHandler:
    lifetime: int
    secret_key: str

    def __init__(self, lifetime: int, secret_key: str):
        self.lifetime = lifetime
        self.secret_key = secret_key

    def generate_token(self, data: TokenData) -> str:
        """
        Generate a JWT token with the provided data.

        :param data: Dictionary to include in the token payload.
        :return: Encoded JWT token as a string.
        """
        # Set the expiration time for the token
        expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=self.lifetime)
        # Add expiration and other custom fields to the payload
        payload = {
            'data': data.to_dict(),
            'exp': expiration_time
        }
        # Encode the token using the secret key
        token: str = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token


    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Verify a JWT token and return the decoded payload if valid.

        :param token: JWT token as a string.
        :return: Decoded payload as a dictionary if the token is valid, otherwise None.
        """
        try:
            # decode the token using the secret key
            decoded_data = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            data = decoded_data.get('data')  # return the original data (from the payload)
            if not data:
                # the token Content is invalid
                return None
            return TokenData.from_dict(data)
        except jwt.ExpiredSignatureError:
            # the token has expired
            return None
        except jwt.InvalidTokenError:
            # the token is invalid
            return None
