from typing import Callable
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import pickle
import marshal
from types import FunctionType
from random import getrandbits


class TaskStatus(Enum):
    IDLE = 0
    RUNNING = 1
    FINISHED = 2


class Worker:
    """
    It's just interface for creating independent process
    and executing task on it, with response as the result
    """

    def __init__(self):
        self._status = TaskStatus.IDLE
        self._result = None

    @property
    def status(self):
        return self._status

    @property
    def result(self):
        if self._status == TaskStatus.RUNNING or self._status == TaskStatus.IDLE:
            return None
        self._status = TaskStatus.IDLE
        result = self._result
        self._result = None
        return result

    def execute_task(self, task) -> None:
        """
        Function for executing task from queue
        Can return anything
        @param task: serialised task as json
        @return: None
        """
        self._status = TaskStatus.RUNNING

        idx, func, args, kwargs = self.__deserialize_task(task)
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)

        self._status = TaskStatus.FINISHED
        self._result = {
            'idx': idx,
            'result': future.result()
        }

    @staticmethod
    def __deserialize_task(task) -> tuple[int, Callable, list, dict]:
        """
        Function for deserializing task from json to tuple
        of function, *args and **kwargs of this function
        @param task: json
        @return: tuple(int, Callable, list, dict)
        """
        deserialized_task = pickle.loads(task)

        function_code = marshal.loads(deserialized_task.get('function'))
        function = FunctionType(function_code, globals(), f'{hash(getrandbits(20))}')
        return (deserialized_task.get('idx'),
                function,
                deserialized_task.get('args'),
                deserialized_task.get('kwargs'))


if __name__ == "__main__":
    pass
