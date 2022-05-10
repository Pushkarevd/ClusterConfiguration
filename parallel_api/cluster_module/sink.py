import zmq
import threading
import copy
import logging


LOGGER = logging.getLogger('sink')
logging.basicConfig(level=logging.DEBUG)


class Sink:

    def __init__(self, self_port):
        self._self_port = self_port
        self._results = []

        self._lock = threading.Lock()

    def __init_server(self):
        context = zmq.Context()
        self._receiver = context.socket(zmq.PULL)
        self._receiver.bind(f"tcp://*:{self._self_port}")

        # Waiting for start of the batch
        self._receiver.recv()
        reading_thread = threading.Thread(target=self.__result_waiting, daemon=True, name='sink_reader')
        reading_thread.start()

    def __result_waiting(self):
        while True:
            result = self._receiver.recv()
            self._results.append(result)

    def get_results(self) -> list:
        with self._lock:
            result_copy = copy.deepcopy(self._results)
            self._results = []
        return result_copy
