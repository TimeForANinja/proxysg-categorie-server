import socket


def get_server_ip() -> str:
    return socket.gethostbyname(socket.gethostname())
