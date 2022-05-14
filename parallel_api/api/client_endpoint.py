import zmq
import threading
import pickle
import logging


LOGGER = logging.getLogger('client-endpoint')
logging.basicConfig(level=logging.DEBUG)


class ClientEndpoint:

    RECEIVED_COUNTER = 0
    SENT_COUNTER = 0

    def __init__(self, cluster_port: int):
        self.cluster_port = cluster_port

        self._received_results = {}
        self._lock = threading.Lock()
        self._read_thread = None

        self.__established_connection()

    def __established_connection(self):
        context = zmq.Context()
        self._client = context.socket(zmq.PAIR)
        self._client.connect(f"tcp://127.0.0.1:{self.cluster_port}")
        LOGGER.info(f'Connected to {self.cluster_port}')

        self._read_thread = threading.Thread(
            target=self.__received_result,
            daemon=True,
            name='read_thread'
        )

        self._read_thread.start()

    @staticmethod
    def __decode_result(result):
        # Make separate function for future
        # If result would need specific decoder
        decoded_result = pickle.loads(result)
        return decoded_result

    def __received_result(self):
        while True:
            result = self._client.recv()
            self.RECEIVED_COUNTER += 1
            decoded_result = self.__decode_result(result)
            self._received_results[decoded_result[0]] = decoded_result[1]

    def get_result(self, idx: int):
        return self._received_results.pop(idx, None)

    def send_task(self, task):
        self._client.send(task)
