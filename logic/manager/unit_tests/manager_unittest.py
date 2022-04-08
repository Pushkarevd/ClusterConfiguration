import unittest
import socket
import os
from multiprocessing import Process
from ..manager import ProcessManager
from ..server import Server


def create_server(port):
    server = Server(port)
    server.start_server()


class ManagerTestCases(unittest.TestCase):

    def test_process_manager(self):
        # Expected result
        expected_response = {
            0: {
                'name': socket.gethostname(),
                'os': os.name,
                'cores': os.cpu_count()
            },
            1: {
                'name': socket.gethostname(),
                'os': os.name,
                'cores': os.cpu_count()
            }
        }

        # Start two instance of server
        process_1 = Process(target=create_server, args=(2020, ))
        process_2 = Process(target=create_server, args=(2021,))

        process_1.start()
        process_2.start()

        ADDRESS = 'localhost'

        list_of_servers = [(ADDRESS, 2020), (ADDRESS, 2021)]
        # Create instance of manager
        manager = ProcessManager(list_of_servers)
        manager.create_clients_in_parallel()

        response = manager.get_workers_info()

        process_1.join()
        process_2.join()
        self.assertEqual(response, expected_response)


if __name__ == '__main__':
    unittest.main()