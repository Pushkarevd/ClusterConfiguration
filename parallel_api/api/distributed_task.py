from threading import Thread
from typing import Callable
from random import getrandbits
from functools import cache
from os import getpid
import socket
import json
import pickle


class FunctionWrapper(Thread):
    def __init__(self, function: Callable, scheduler: Scheduler, *args, **kwargs):
        Thread.__init__(self)
        # TO DO
        # Create Client for sending task to cluster
        # And Server for receiving results
        self._scheduler = scheduler
        self._func = function
        self._args = args
        self._kwargs = kwargs

    @property
    def __serialize_task(self) -> str:
        """
        Function that serialized task for sending through socket connection
        @return: str, json
        """
        pickled_function = pickle.dumps(self._func, 0).decode()

        # ID of task will contain info about machine where this task is executed
        # Will contain id of module where this task is needed
        # And id of TASK itself (12 bit)
        task = {
            'idx': self.__generate_id(),
            'function': pickled_function,
            'args': self._args,
            'kwargs': self._kwargs
        }

        serialized_task = json.dumps(task)

        return serialized_task

    def __generate_id(self):
        machine_id = self.get_my_ip()
        module_id = str(getpid())
        task_id = getrandbits(12)

        return machine_id, module_id, task_id

    @staticmethod
    @cache
    def get_my_ip() -> bytes:
        """
        Get ip of current machine in local network
        @return: ip as string
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as st:
            try:
                st.connect(('10.255.255.255', 1))
                ip = st.getsockname()[0]
            except socket.error as exc:
                return f'Error, cant connect {exc}'
        return ip

    def run(self) -> None:
        """
        When thread is started, serialize task and send it to Scheduler
        @return: None
        """
        serialized_task = self.__serialize_task
        self._scheduler.add_task_to_queue(serialized_task)


class DistributedTask:

    def __init__(self, function: Callable, *args, **kwargs):
        self._wrapped_function = FunctionWrapper(function, args, kwargs)
        self._result = self._wrapped_function.start()

    def __call__(self):
        """
        If instance of this task was called, then if task already computed then return result
        Else stop main thread
        @return: *
        """
        self._wrapped_function.join()
        return self._result


def foo(x):
    return x ** 2


if __name__ == "__main__":
    wrapped_func = DistributedTask(foo, 10)

    print('before')

    wrapped_func()

    print('between')

    print('after')
