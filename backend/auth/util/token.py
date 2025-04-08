import os
import secrets
import tempfile


def generate_auth_token(length=64):
    """Generate a secure random authentication token."""
    return secrets.token_hex(length)


shared_token = None
def get_shared_token(file: str = "other_token.txt") -> str:
    """
    This method returns the current authentication token.

    Unfortunately writing to a tmp file is currently the best way to achieve this.
    Adding to flask g like done for the db_singleton does not work, since it's not thread safe.
    An alternative would be to use redis, but this would be overkill to set up just for this use-case.
    """
    global shared_token

    if shared_token is not None:
        return shared_token

    abs_path = os.path.join(tempfile.gettempdir(), file)

    if not os.path.exists(abs_path):
        shared_token = generate_auth_token()
        with open(abs_path, "w") as f:
            f.write(shared_token)
    else:
        with open(abs_path, "r") as f:
            shared_token = f.read().strip()

    return shared_token
