import threading
import socket
import psutil
import logging
import time
import json


LOGGER = logging.getLogger('status_worker')


class Status:

    def __init__(self, ip, port):
        self._ip = ip
        self._port = port

        self.__established_connection()

    def __wait_connection(self, sock):
        for tries in range(1, 11):
            try:
                sock.connect((self._ip, self._port))
                break
            except ConnectionError:
                LOGGER.warning(f"Can't connect to {self._ip}:{self._port}\n"
                               f"Attempt {tries}")
            if tries == 10:
                raise ConnectionError(f"Can't connect to {self._ip}:{self._port}\n"
                                      f"Check address and try again")
            time.sleep(1)

    def __get_init_msg(self, sock):
        msg = sock.recv(1024)

        sock.send(b'ACK')

        decoded_msg = json.loads(msg.decode())

        self._ventilator_port = decoded_msg.get('ventilator')
        self._sink_port = decoded_msg.get('sink')

    def __established_connection(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

            self.__wait_connection(sock)
            self.__get_init_msg(sock)

            while True:
                msg = sock.recv(1024)
                if msg.decode() != 'STATUS':
                    raise ConnectionError(f'Command from server is wrong,'
                                          f' check address and try one more time')
                status = self.__get_status()
                sock.send(status)

    @staticmethod
    def __get_status():
        return json.dumps({
            'cpu': psutil.cpu_percent(),
            'ram': psutil.virtual_memory().percent,
            'name': socket.gethostname(),
            'cores': psutil.cpu_count()
        }).encode()

    @property
    def view_ports(self):
        if self._ventilator_port is None or self._sink_port is None:
            return None
        return self._ventilator_port, self._sink_port


if __name__ == "__main__":
    client = Status('127.0.0.1', 2020)