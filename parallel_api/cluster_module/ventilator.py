import zmq


class Ventilator:

    def __init__(self, self_port, sink_port):
        self._self_port = self_port
        self._sink_port = sink_port

        self._sink = None
        self._sender = None

    def start_server(self):
        context = zmq.Context()
        self._sender = context.socket(zmq.PUSH)
        self._sender.bind(f'tcp://*:{self._self_port}')

        # Adding connection to the sink for synchronize START of batch
        self._sink = context.socket(zmq.PUSH)
        self._sink.connect(f"tcp://localhost:{self._sink_port}")

        # Empty msg, signals start of batch
        self._sink.send(b'')

    def send_task(self, task: bytes):
        """
        Interface for sending task to worker
        @param task: Serialized task
        @return: None
        """
        self._sender.send(task)