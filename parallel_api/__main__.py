import argparse
import logging
import multiprocessing as mp

from cluster_module.cluster_endpoint import ClusterEndpoint
from cluster_module.helpers import get_free_port
from cluster_module.monitor import Monitor
from cluster_module.sink import Sink
from cluster_module.ventilator import Ventilator
from worker_module.executor import Executor
from worker_module.server_worker import ServerWorker
from worker_module.status import Status


LOGGER = logging.getLogger('init_pipeline')
logging.basicConfig(level=logging.DEBUG)


def worker_pipeline(ip='127.0.0.1', port=2020):
    # Init Status
    status_client = Status(ip, port)
    LOGGER.info('Status Client started')
    while status_client.view_ports is None:
        pass

    ventilator_port, sink_port = status_client.view_ports
    LOGGER.info(f'Ventilator port - {ventilator_port}\n'
                f'Sink port - {sink_port}')

    ventilator_address = f"{ip}:{ventilator_port}"
    sink_address = f"{ip}:{sink_port}"

    server_worker = ServerWorker(ventilator_address, sink_address)
    LOGGER.info('Server Worker started')
    executor = Executor(server_worker)
    LOGGER.info('Executor started')


def host_pipeline(port):
    monitor = Monitor(port)
    LOGGER.info('Monitor started')

    vent_port, sink_port = monitor.get_vent_and_sink_ports

    LOGGER.info(f'Port for ventilator - {vent_port}\n'
                f'Port for sink - {sink_port}')

    sink = Sink(sink_port)
    LOGGER.info(f'Sink started')

    ventilator = Ventilator(self_port=vent_port, sink_port=sink_port)
    LOGGER.info(f'Ventilator initialize')

    endpoint_port = get_free_port()

    print(f'Endpoint port - {endpoint_port}. For module execution, use this port.')

    cluster_endpoint = ClusterEndpoint(endpoint_port, ventilator, sink)
    LOGGER.info('Endpoint started')
    while not monitor.view_statuses:
        pass
    LOGGER.info(monitor.view_statuses)
    ventilator.start_server()
    LOGGER.info('Ventilator ready for work')


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        '-t',
        '--type',
        type=str,
        choices=['worker', 'host'],
        default='host',
        required=True
    )

    argparser.add_argument(
        '-d',
        '--destination',
        type=str
    )
    argparser.add_argument(
        '-p',
        '--port',
        type=int
    )

    argparser.add_argument(
        '--ui',
        action='store_true',
        default=False
    )

    args = argparser.parse_known_args()[0]

    if args.type == 'host':
        # Do host things
        host_port = args.port
        host_pipeline(host_port)
    else:
        host_address = args.destination
        ip = host_address[:host_address.find(':')]
        port = int(host_address[host_address.find(':') + 1:])
        # Do worker things
        worker_pipeline(ip, port)
