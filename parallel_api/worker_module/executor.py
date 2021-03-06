import json
import logging

from .worker import Worker
from os import cpu_count


LOGGER = logging.getLogger('executor')
logging.basicConfig(level=logging.WARNING)


class Executor:
    """
    Server for all workers, getting commands and tasks from scheduler
    Delegate task to workers, and aggregate results,
    After executor send response with id of task and result
    """

    def __init__(self, task_list, result_list, lock):
        # Create workers and set status to IDLE
        self._workers = {
            idx: Worker()
            for idx in range(cpu_count())
        }

        self._task_queue = task_list
        self._result_queue = result_list
        self._lock = lock

        self.__main_loop()

    @property
    def queue(self):
        return self._task_queue

    def add_task(self, task: json) -> None:
        """
        Function for adding new task to queue
        @param task: json, serialized task
        @return: None
        """
        self._task_queue.append(task)

    def __main_loop(self):
        """
        Main loop function, that keep running while executor
        is connected to cluster
        @return: None
        """
        while True:
            # While there are workers without task,
            # take task from queue and send it to worker
            while self.__get_idle_worker() is not None and self._task_queue:
                idle_worker: Worker = self._workers[self.__get_idle_worker()]
                with self._lock:
                    task = self._task_queue.pop()
                LOGGER.debug('Task delegated')
                idle_worker.execute_task(task)
                continue

            # Get results from workers and send it to ServerWorker
            finished_workers = self.__get_result_from_worker()

            if finished_workers:
                LOGGER.debug('There some finished workers')
                results = self.__get_results(finished_workers)
                self.__send_result(results)

    @staticmethod
    def __get_results(finished_workers: list):
        """
        Function for getting results from workers
        @param finished_workers: list(Worker) FINISHED
        @return: list[(idx, result)]
        """
        worker_responses = [worker.result for worker in finished_workers]
        results = [(response['idx'], response['result']) for response in worker_responses]
        return results

    def __send_result(self, results):
        for result in results:
            with self._lock:
                self._result_queue.append(result)

    def __get_idle_worker(self) -> int:
        """
        Helper function for getting id of idle worker
        @return: id of idle worker
        """
        idle_worker_id = None
        for idx, worker in self._workers.items():
            if worker.status.value == 0:
                idle_worker_id = idx
                break
        return idle_worker_id

    def __get_result_from_worker(self):
        """
        Helper function
        @return: dict, list of FINISHED workers
        """
        finished_workers = [worker for worker in self._workers.values() if worker.status.value == 2]
        return finished_workers