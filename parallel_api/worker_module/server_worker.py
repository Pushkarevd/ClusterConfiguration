import pickle
import threading
import logging
import zmq
import copy

from os import environ
from threading import Lock


LOGGER = logging.getLogger(f'worker {environ["COMPUTERNAME"]}')
logging.basicConfig(level=logging.DEBUG)


class RepeatTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class ServerWorker:

    def __init__(self, receiving_addr, sending_addr):
        self._receviving_addr = receiving_addr
        self._sending_addr = sending_addr

        self._task_queue = []
        self._result_queue = []

        self._lock = Lock()

        self.__main_loop()

    def __main_loop(self):
        context = zmq.Context()

        self._receiver = context.socket(zmq.PULL)
        self._receiver.connect(f"tcp://{self._receviving_addr}")

        self._sender = context.socket(zmq.PUSH)
        self._sender.connect(f"tcp://{self._sending_addr}")

        LOGGER.info(f'Connection established')

        self._read_thread = threading.Thread(target=self.__get_task, daemon=True, name='read_thread')
        self._send_thread = RepeatTimer(0.3, self.__send_result)

        self._send_thread.start()
        self._read_thread.start()

    def __get_task(self):
        while True:
            task = self._receiver.recv()
            LOGGER.info('Task received')
            self._task_queue.append(task)

    def get_task(self):
        with self._lock:
            tasks = copy.deepcopy(self._task_queue)
            self._task_queue = []
        return tasks

    def add_result(self, results):
        with self._lock:
            self._result_queue.extend(results)

        LOGGER.info('Result added')

    def __send_result(self):
        if self._result_queue:
            while self._result_queue:
                result = pickle.dumps(self._result_queue.pop(0))
                LOGGER.info(f'Result sent to {self._sending_addr}')
                self._sender.send(result)


if __name__ == '__main__':
    worker = ServerWorker('127.0.0.1:2020', '127.0.0.1:2021')