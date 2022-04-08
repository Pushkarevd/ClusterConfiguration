import time

from client import Client, ClientException
import threading
import logging
import re
from typing import Union

LOGGER = logging.getLogger('manager')
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())


class ProcessManagerException(Exception):
    """
    Custom Manager Exception
    """
    pass


class ProcessManager:

    def __init__(self):
        # Client - machine that was 'discovered'
        self.clients = {}

    def get_workers_info(self) -> list[dict]:
        """
        Get all information about workers
        :return:
        """
        response = [
            {
                'name': client.name,
                'os': client.os,
                'cores': client.cores
            } for client in self.clients
        ]

        return response

    def get_workers_status(self) -> list[dict]:
        """
        Get CPU and RAM usage for all workers
        :return: list[dict]
        """
        response = [
            {
                'cpu_usage': client.cpu_usage,
                'ram_usage': client.ram_usage
            } for client in self.clients
        ]
        LOGGER.warning(response)

    def add_new_client(self, client_data: str) -> bool:
        """
        Add new client to the class
        Creating new worker from this client
        :param client_data: string that define client ip and port
        :return: bool, if new client was create - True, else False
        """
        # Parse ip and port from string
        ip_pattern = '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        port_pattern = '(?<=:)[0-9]{1,6}'

        ip = re.findall(ip_pattern, client_data)
        port = re.findall(port_pattern, client_data)

        # Validate new client (ip, port)
        if len(ip) != 1 or len(port) != 1:
            LOGGER.warning(f"Can't parse {client_data}")
        ip = ip[0]
        port = int(port[0])
        LOGGER.info(f'New client {ip}:{port}')

        # Check if client already exists
        if (ip, port) in self.clients.keys():
            LOGGER.warning(f'Client {ip}:{port} already exists')
            raise ProcessManagerException(f'Client {ip}:{port} already exists')

        # Init connection, add only after 'discover' operation
        try:
            # Create process with Daemon=True, that mean if Parent process stops, child will be stopped too
            thread = threading.Thread(
                target=self.init_new_client,
                args=((ip, port),),
                daemon=True
            )
            thread.start()
        except ProcessManagerException as err:
            LOGGER.warning(err)
            return False

        return True

    def init_new_client(self, client: tuple) -> None:
        """
        Initialize connection between Manager and Client
        :param client: tuple (ip, port)
        """
        client = Client(*client)
        # Try create client and connect to it
        try:
            # If connection was established
            self.clients[client] = client
            client.connection_loop()
        except ClientException:
            self.clients.pop(client, None)
            raise ProcessManagerException()


if __name__ == "__main__":
    manager = ProcessManager()
    manager.add_new_client('127.0.0.1:2020')
    while True:
        manager.get_workers_status()
        time.sleep(5)
