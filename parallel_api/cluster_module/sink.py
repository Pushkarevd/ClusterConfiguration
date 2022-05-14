import zmq
import threading
import copy
import logging


LOGGER = logging.getLogger('sink')
logging.basicConfig(level=logging.WARNING)


class Sink:

    def __init__(self, self_port):
        self._self_port = self_port
        self._results = []

        self._lock = threading.Lock()
        self.__init_server()

    def __init_server(self):
        context = zmq.Context()
        self._receiver = context.socket(zmq.PULL)
        self._receiver.bind(f"tcp://*:{self._self_port}")

        # Waiting for start of the batch

        reading_thread = threading.Thread(target=self.__result_waiting, daemon=True, name='sink_reader')
        reading_thread.start()

    def __result_waiting(self):
        self._receiver.recv()
        LOGGER.info('Received first byte')
        while True:
            result = self._receiver.recv()
            LOGGER.info(f'Received result')
            self._results.append(result)

    def get_results(self) -> list:
        with self._lock:
            result_copy = copy.deepcopy(self._results)
            self._results = []
        return result_copy
