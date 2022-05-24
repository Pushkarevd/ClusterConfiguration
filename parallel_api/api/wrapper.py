from functools import wraps

from .distributed_task import DistributedTask


def cluster_function(endpoint):
    def _cluster_function(func):
        @wraps(func)
        def inner(*args, **kwargs):
            return DistributedTask(endpoint, func, *args, **kwargs)

        return inner

    return _cluster_function
