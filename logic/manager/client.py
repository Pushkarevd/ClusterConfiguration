import socket
import os
import logging
import json


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

    def connection_loop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                self.discover_server(sock)
                sock.sendall(b'STOP')
            except socket.error:
                raise Exception(f"Can't connect to {self.server_ip}:{self.server_port}")

    def discover_server(self, sock: socket.socket) -> None:
        """
        Discover server worker
        Update worker OS and number of CPU cores
        :param sock:
        :return None:
        """
        sock.connect((self.ip, self.port))
        sock.sendall(b'DISCOVER')

        try:
            response = json.loads(sock.recv(1024).decode())
            self.cores = response.get('cores')
            self.os = response.get('os')
        except UnicodeDecodeError:
            raise Exception(f"Can't decode message: {response}")

        if not response:
            # TO DO
            # Change to custom Exception
            raise Exception(f"Something went wrong")


if __name__ == '__main__':
    client = Client('localhost', 2020)
    client.connection_loop()
    print(client.cores)