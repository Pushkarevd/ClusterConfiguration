import pickle
import threading
import socket
import psutil
import logging
import time


LOGGER = logging.getLogger('status_worker')
logging.basicConfig(level=logging.WARNING)


class Status:

    def __init__(self, ip, port):
        self._ip = ip
        self._port = port

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__established_connection()

    def __wait_connection(self):
        for tries in range(1, 11):
            try:
                self._sock.connect((self._ip, self._port))
                break
            except ConnectionError:
                LOGGER.warning(f"Can't connect to {self._ip}:{self._port}\n"
                               f"Attempt {tries}")
            if tries == 10:
                raise ConnectionError(f"Can't connect to {self._ip}:{self._port}\n"
                                      f"Check address and try again")
            time.sleep(1)

    def __get_init_msg(self):
        msg = self._sock.recv(1024)
        LOGGER.info(f'Init message received')
        self._sock.send(b'ACK')

        decoded_msg = pickle.loads(msg)

        self._ventilator_port = decoded_msg.get('ventilator')
        self._sink_port = decoded_msg.get('sink')

        LOGGER.info(f'Ventilator port - {self._ventilator_port}\n'
                    f'Sink port - {self._sink_port}')

    def __established_connection(self):
        self.__wait_connection()
        self.__get_init_msg()

        self._status_thread = threading.Thread(
            target=self.__status_loop,
            daemon=True,
            name='status_thread'
        )

        self._status_thread.start()

    def __status_loop(self):
        while True:
            msg = self._sock.recv(1024)
            if msg.decode() != 'STATUS':
                raise ConnectionError(f'Command from server is wrong,'
                                      f' check address and try one more time')
            status = self.__get_status()
            self._sock.send(status)

    @staticmethod
    def __get_status():
        return pickle.dumps({
            'cpu': psutil.cpu_percent(),
            'ram': psutil.virtual_memory().percent,
            'name': socket.gethostname(),
            'cores': psutil.cpu_count()
        })

    @property
    def view_ports(self):
        if self._ventilator_port is None or self._sink_port is None:
            return None
        return self._ventilator_port, self._sink_port


if __name__ == "__main__":
    client = Status('127.0.0.1', 2020)