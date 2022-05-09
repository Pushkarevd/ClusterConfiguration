import threading
import logging
import socket
import time
import json

LOGGER = logging.getLogger('monitor')


class Monitor:
    """
    Socket Server for monitoring workers
    Getting cpu and ram usage.
    Give zmq ventilator information
    about new worker
    """

    def __init__(self, port=2020):
        self._port = port

        self._lock = threading.Lock()
        self._worker = []
        self._workers_info = {}

        self.__get_random_free_port()
        self.__init_server()

    def __get_random_free_port(self) -> None:
        """
        Get ports for Ventilator and Sink
        @return: None
        """
        sock_1 = socket.socket()
        sock_1.bind(('', 0))
        self._ventilator_port = sock_1.getsockname()[1]

        sock_2 = socket.socket()
        sock_2.bind(('', 0))
        self._sink_port = sock_2.getsockname()[1]

        sock_1.close()
        sock_2.close()

    def __init_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            LOGGER.info('Monitor server started')
            sock.bind(('localhost', self._port))
            sock.listen(20)

            while True:
                conn, addr = sock.accept()

                LOGGER.info(f'New worker {addr} connected')
                # ID of connection is position of connection in worker list
                self._worker.append(conn)
                thread = threading.Thread(
                    target=self.__handle_worker,
                    args=(conn, addr,),
                    daemon=True,
                    name=f'worker {len(self._worker)}'
                )
                thread.start()

    def __init_msg(self, conn):
        # First message - Ventilator and Sink ports
        msg = json.dumps(
            {
                'ventilator': self._ventilator_port,
                'sink': self._sink_port
            }
        ).encode()

        try:
            conn.send(msg)

            check = conn.recv(1024)
            if check.decode() != 'ACK':
                raise ConnectionError
        except ConnectionResetError:
            conn.close()
            return False

    def __handle_worker(self, conn, addr):

        self.__init_msg(conn)

        while True:
            try:
                conn.send(b'STATUS')

                status = conn.recv(1024)
                parsed_status = json.loads(status.decode())
                with self._lock:
                    self._workers_info[addr] = parsed_status
                time.sleep(3)
            except ConnectionResetError:
                conn.close()
                return False

    @property
    def view_statuses(self):
        print(self._workers_info)


if __name__ == '__main__':
    server = Monitor()