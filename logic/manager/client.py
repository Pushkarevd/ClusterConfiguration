import socket
import logging
import json
from time import sleep


LOGGER = logging.getLogger('client')
LOGGER.addHandler(logging.StreamHandler())


class ClientException(Exception):
    """
    Exception for socket client
    """
    pass


class Client(object):
    """
    Class for connection to workers
    Main module will create multiple instances of this class
    Will execute commands in parallel
    """

    def __init__(self, server_ip, server_port):
        self.ip = server_ip
        self.port = server_port
        self.os = None
        self.cores = None
        self.name = None
        self.cpu_usage = None
        self.ram_usage = None

    def connection_loop(self):
        LOGGER.info(f'Client started connection to {self.ip}:{self.port}')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                self.discover_server(sock)
                while sock:
                    sleep(10)
                    self.get_status(sock)
            except socket.error:
                LOGGER.warning(f"Can't connect to {self.ip}:{self.port}")
                raise ClientException(f"Can't connect to {self.ip}:{self.port}")

    def discover_server(self, sock: socket.socket) -> None:
        """
        Discover server worker
        Update worker OS and number of CPU cores
        :param sock:
        :return None:
        """
        LOGGER.info(f'Discover worker')
        sock.connect((self.ip, self.port))
        sock.sendall(b'DISCOVER')

        try:
            response = json.loads(sock.recv(1024).decode())
            self.cores = response.get('cores')
            self.os = response.get('os')
            self.name = response.get('name')
        except UnicodeDecodeError:
            LOGGER.warning(f"Message from worker can't be decoded")
            raise ClientException(f"Can't decode message: {response}")

        if not response:
            raise ClientException(f"Something went wrong")
        LOGGER.info("Worker successfully discovered")

    def get_status(self, sock: socket.socket) -> None:
        """
        Get status of workers: Cpu usage and Ram usage
        :param sock: socket.socket
        :return: dict
        """
        LOGGER.info(f'Getting status of {self.ip}:{self.port}')
        command = b'STATUS'

        sock.sendall(command)
        try:
            response = sock.recv(1024)
        except Exception:
            # TO DO
            # Change location of all Exception and change to Custome one
            LOGGER.warning(f'Something went wrong with {self.ip}:{self.port}')
            raise ClientException(f'Something went wrong with {self.ip}:{self.port}')

        self.cpu_usage = response.get('cpu_usage')
        self.ram_usage = response.get('ram_usage')
        LOGGER.info(f"Got status of {self.ip}:{self.port}")


if __name__ == '__main__':
    pass