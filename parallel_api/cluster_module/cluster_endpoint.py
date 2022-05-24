import zmq
import logging
import threading

LOGGER = logging.getLogger("cluster-endpoint")
logging.basicConfig(level=logging.DEBUG)


class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class ClusterEndpoint:
    """
    Class for getting task from lib API
    Getting new tasks from executed task
    And execute on cluster
    """

    def __init__(self, port, ventilator, sink):
        self._port = port
        self._ventilator = ventilator
        self._sink = sink

        self.__start_receiver()

    def __start_receiver(self):
        context = zmq.Context()
        self._server = context.socket(zmq.PAIR)
        self._server.bind(f"tcp://*:{self._port}")

        self._send_thread = RepeatTimer(0.3, self.__sending_results)
        self._receiving_thread = threading.Thread(
            target=self.__receiving_task, daemon=True, name="receiving_thread"
        )
        self._receiving_thread.start()
        self._send_thread.start()

    def __receiving_task(self):
        while True:
            msg = self._server.recv()
            LOGGER.debug(f"Message received")

            # Send new task to main Ventilator
            self._ventilator.send_task(msg)

    def __sending_results(self):
        results = self._sink.get_results()
        if results:
            for result in results:
                LOGGER.debug(f"Result sent")
                self._server.send(result)
