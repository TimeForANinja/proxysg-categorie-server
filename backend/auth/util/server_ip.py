import socket


def get_server_ip() -> str:
    """
    Util function to get the server IP address.
    """
    return socket.gethostbyname(socket.gethostname())
