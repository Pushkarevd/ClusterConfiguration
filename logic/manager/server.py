import socket
import os
import logging
import json
import psutil
from argparse import ArgumentParser


LOGGER = logging.getLogger(f"Worker {socket.gethostname()}")
LOGGER.addHandler(logging.StreamHandler())


class ServerException(Exception):
    """
    Custom Exception for worker(server)
    """
    pass


class Server:

    def __init__(self, port: int):
        self.port = port

    def start_server(self):
        commands = {
            # Function for server discovery
            'DISCOVER': self.discover_server,
            # Function for server status
            'STATUS': self.status
        }

        # Create socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            LOGGER.info(f'Server on {self.port} has started.')
            sock.bind(('localhost', self.port))

            sock.listen(1)

            # Establish connection
            conn, addr = sock.accept()

            # While client connected
            while conn:
                LOGGER.info(f'Client {addr} has connected')
                received_data = None
                # Message loop
                while received_data != 'STOP':
                    try:
                        received_data = conn.recv(1024)
                        received_data = received_data.decode()

                        command = commands.get(received_data)
                    except UnicodeError:
                        LOGGER.warning("Can't decode received command")

                    except ConnectionAbortedError:
                        raise Exception(f"Client aborted connection")

                    if command:
                        LOGGER.info(f'Server execute {command}')
                        message = command()
                    else:
                        LOGGER.warning(f'Server get unknown command {command}')
                        message = b"FAULT"

                    conn.sendall(message)

    @staticmethod
    def discover_server() -> bytes:
        """
        Return main information about server
        :return: dict{Number of cores, OS name}
        """
        response: dict = {
            'cores': os.cpu_count(),
            'os': os.name,
            'name': socket.gethostname()
        }
        encoded_json = json.dumps(response).encode()
        return encoded_json

    @staticmethod
    def status():
        """
        Get status of current tasks
        :return dict: CPU usage, RAM usage
        """
        status = {
            'cpu_usage': psutil.cpu_percent(),
            'ram_usage': psutil.virtual_memory().percent
        }

        return status


if __name__ == '__main__':
    argparse = ArgumentParser()
    argparse.add_argument('--port', type=int)
    args = argparse.parse_known_args()[0]
    server = Server(args.port)
    server.start_server()