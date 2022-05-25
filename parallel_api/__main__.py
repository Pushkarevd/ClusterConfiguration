import argparse
import logging
import multiprocessing
import os
import sys

from parallel_api.cluster_module.cluster_endpoint import ClusterEndpoint
from parallel_api.cluster_module.helpers import get_my_ip, get_free_port
from parallel_api.cluster_module.monitor import Monitor
from parallel_api.cluster_module.sink import Sink
from parallel_api.cluster_module.ventilator import Ventilator
from parallel_api.worker_module.executor import Executor
from parallel_api.worker_module.server_worker import ServerWorker
from parallel_api.worker_module.status import Status

if not __package__:
    path = os.path.join(os.path.dirname(__file__), os.pardir)
    sys.path.insert(0, path)


LOGGER = logging.getLogger("init_pipeline")
logging.basicConfig(level=logging.DEBUG)


def worker_pipeline(ip: str, port: int):
    # Init Status
    manager = multiprocessing.Manager()
    task_list = manager.list()
    result_list = manager.list()
    lock = manager.Lock()

    status_client = Status(ip, port)
    LOGGER.info("Status Client started")
    while status_client.view_ports is None:
        pass

    ventilator_port, sink_port = status_client.view_ports
    LOGGER.info(f"Ventilator port - {ventilator_port}\n" f"Sink port - {sink_port}")

    ventilator_address = f"{ip}:{ventilator_port}"
    sink_address = f"{ip}:{sink_port}"
    server_worker = ServerWorker(
        ventilator_address, sink_address, task_list, result_list, lock
    )
    server_process = multiprocessing.Process(
        target=server_worker.main_loop, daemon=True
    )
    server_process.start()

    LOGGER.info("Server Worker started")
    executor = Executor(task_list, result_list, lock)
    LOGGER.info("Executor started")


def host_pipeline(port, endpoint=None):
    self_ip = get_my_ip()
    monitor = Monitor(port)
    LOGGER.info("Monitor started")

    vent_port, sink_port = monitor.get_vent_and_sink_ports

    LOGGER.info(f"Port for ventilator - {vent_port}\n" f"Port for sink - {sink_port}")

    sink = Sink(sink_port)
    LOGGER.info(f"Sink started")

    ventilator = Ventilator(self_port=vent_port, sink_port=sink_port)
    LOGGER.info(f"Ventilator initialize")

    endpoint_port = get_free_port() if endpoint is None else endpoint
    print(f"Host ip - {self_ip}")

    print(f"Endpoint port - {endpoint_port}. For module execution, use this port.")

    cluster_endpoint = ClusterEndpoint(endpoint_port, ventilator, sink)
    LOGGER.info("Endpoint started")
    while not monitor.view_statuses:
        pass
    LOGGER.info(monitor.view_statuses)
    ventilator.start_server()
    LOGGER.info("Ventilator ready for work")


def main(target, *args):
    pipeline_process = multiprocessing.Process(target=target, args=args, daemon=True)
    pipeline_process.start()
    while True:
        try:
            pass
        except KeyboardInterrupt:
            LOGGER.info("Stop cluster")
            sys.exit(0)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=["worker", "host"],
        default="host",
        required=True,
    )

    argparser.add_argument("-d", "--destination", type=str)
    argparser.add_argument("-p", "--port", type=int)
    argparser.add_argument("-e", "--endpoint", type=int)

    argparser.add_argument("--ui", action="store_true", default=False)

    args = argparser.parse_known_args()[0]

    host_args = args.port, args.endpoint
    worker_args = args.destination.split(":") if args.destination is not None else None

    target = {
        "host": main(host_pipeline, *host_args),
        "worker": main(worker_pipeline, *worker_args),
    }
