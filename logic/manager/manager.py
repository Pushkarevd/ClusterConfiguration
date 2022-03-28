import ssl
import socket
import logging

from helper import get_my_ip


LOGGER = logging.Logger('manager')


class NetworkManager:
    """
    This class manages all network connections
    by socket with ssl.
    """

    def __init__(self, ips: list[str]):
        self.ips = ips
        self.root_ip = get_my_ip()

    def connect_to_ip(self, ip: str):
        context = ssl.create_default_context()
        LOGGER.info(f'Trying to connect to {ip}')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            with context.wrap_socket(sock, server_hostname=ip) as secure_sock:
                print(secure_sock.version())


test = NetworkManager(['192.168.0.100'])
test.connect_to_ip(test.ips[0])