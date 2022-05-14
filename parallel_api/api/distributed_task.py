from random import getrandbits
import pickle
import marshal


class DistributedTask:
    """
    Wrapper for distributed function
    """
    def __init__(self, endpoint, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._endpoint = endpoint
        self._task_id = getrandbits(16)

        self._result = None

        self.__send_task()

    def __serialize_task(self):
        serialized_function = marshal.dumps(self.func.__code__)
        task = pickle.dumps(
            {
                'idx': self._task_id,
                'function': serialized_function,
                'args': self.args,
                'kwargs': self.kwargs if self.kwargs else {}
            }
        )
        return task

    def __send_task(self):
        serialized_task = self.__serialize_task()
        self._endpoint.send_task(serialized_task)

    @property
    def result(self):
        """
        Take CPU resource till result
        Came from cluster
        """
        while self._result is None:
            # While result is none -> try to get result from endpoint
            self._result = self._endpoint.get_result(self._task_id)
        print(1)
        return self._result
