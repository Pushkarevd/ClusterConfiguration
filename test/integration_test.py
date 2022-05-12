import zmq
import marshal
import pickle
import random


def foo(x, y):
    return x ** 2 + y ** 2


function_code = foo.__code__
serialized_function = marshal.dumps(function_code)

tasks = [
    {
        'idx': random.getrandbits(12),
        'args': [i + 2, i ** 2],
        'kwargs': {},
        'function': serialized_function
    }
    for i in range(100)
]


class Pair:

    def __init__(self, address='127.0.0.1:55167'):
        self.address = address

    def connect(self):
        context = zmq.Context()
        self._client = context.socket(zmq.PAIR)
        self._client.connect(f'tcp://{self.address}')

        # Send all tasks
        for task in tasks:
            self._client.send(pickle.dumps(task))

        # Receiving results
        while True:
            result = self._client.recv()
            decoded_result = pickle.loads(result)
            print(decoded_result)


if __name__ == "__main__":
    client = Pair()
    client.connect()

