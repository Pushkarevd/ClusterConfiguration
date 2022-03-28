import socket
import os
import logging
import json


class Server:

    def __init__(self, port: int):
        self.port = port
        self.LOGGER = logging.getLogger('server')

    def start_server(self):
        COMMANDS = {
            # Function for server discovery
            'DISCOVER': self.discover_server,
            # Function for server status
            'STATUS': None
        }

        # Create socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            self.LOGGER.info(f'Server on {self.port} has started.')
            sock.bind(('localhost', self.port))

            sock.listen(1)

            # Establish connection
            conn, addr = sock.accept()

            # While client connected
            while conn:
                self.LOGGER.info(f'Client {addr} has connected')
                received_data = None
                # Message loop
                while received_data != 'STOP':
                    try:
                        received_data = conn.recv(1024)
                        received_data = received_data.decode()

                        command = COMMANDS.get(received_data)
                    except UnicodeError:
                        self.LOGGER.warning("Can't decode received command")

                    except ConnectionAbortedError:
                        raise Exception(f"Client aborted connection")

                    if command:
                        self.LOGGER.info(f'Server execute {command}')
                        message = command()
                    else:
                        self.LOGGER.warning(f'Server get unknown command {command}')
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
            'os': os.name
        }
        encoded_json = json.dumps(response).encode()
        return encoded_json

    @staticmethod
    def status():
        """
        Get status of current tasks
        :return:
        """
        # TO DO
        # Find method for getting MPI tasks status
        pass


if __name__ == '__main__':
    server = Server(2020)
    server.start_server()