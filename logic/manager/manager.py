import time

from client import Client, ClientException
from helper import parse_ip
import logging
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
        self.clients_ips = []
        self.clients = []

    def __update_status_of_all_workers(self):
        """
        Updates all workers statuses
        @return: None
        """
        for client in self.clients:
            client.get_status()

    def get_workers_info(self) -> list[dict]:
        """
        API for UI to get all information about machines
        @return: list[dict] with all workers info
        """
        self.__update_status_of_all_workers()

        response = [
            {
                "name": worker.name,
                "cores": worker.cores,
                "os": worker.os,
                "cpu_usage": worker.cpu_usage,
                "ram_usage": worker.ram_usage
            } for worker in self.clients
        ]

        return response

    def add_new_client(self, client_data: str) -> bool:
        """
        Add new client to the class
        Creating new worker from this client
        :param client_data: string that define client ip and port
        :return: bool, if new client was create - True, else False
        """
        # Parse ip and port from string
        client = parse_ip(client_data)
        if client is None:
            LOGGER.warning(f"Can't parse ip address {client_data}")
            return False

        LOGGER.info(f'New client {client[0]}:{client[1]}')

        # Check if client already exists
        if client in self.clients_ips:
            LOGGER.warning(f'Client {client[0]}:{client[1]} already exists')
            raise ProcessManagerException(f'Client {client[0]}:{client[1]} already exists')

        # Init connection, add only after 'discover' operation
        try:
            worker = Client(*client)
            worker.discover_server()
        except ClientException as err:
            LOGGER.warning(err)
            return False

        self.clients_ips.append(client)
        self.clients.append(worker)
        return True


if __name__ == "__main__":
    manager = ProcessManager()
    manager.add_new_client('127.0.0.1:2020')
    while True:
        print(manager.get_workers_status())
        time.sleep(5)
