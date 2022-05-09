import zmq


class TaskReceiver:
    """
    Class for getting task from lib API
    Getting new tasks from executed task
    And execute on cluster
    """
    def __init__(self, port, ventilator):
        self._port = port
        self._ventilator = ventilator

        self.__start_receiver()

    def __start_receiver(self):
        context = zmq.Context()
        self._receiver = context.socket(zmq.REP)
        self._receiver.bind(f"tcp://*:{self._port}")

        while True:
            msg = self._receiver.recv()
            if not isinstance(msg, bytes):
                self._receiver.send('ERROR')

            # Send new task to main Ventilator
            self._ventilator.send_task(msg)
            self._receiver.send(b'ACK')