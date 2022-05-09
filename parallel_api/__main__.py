import argparse

from ClusterConfiguration.parallel_api.worker_module.executor import Executor
from worker_module.status import Status
from worker_module.server_worker import ServerWorker

from ClusterConfiguration.parallel_api.cluster_module.scheduler import Scheduler


def worker_pipeline(ip, port):
    # Init Status
    status_client = Status(ip, port)
    while status_client.view_ports is None:
        pass

    ventilator_port, sink_port = status_client.view_ports
    ventilator_address = f"{ip}:{ventilator_port}"
    sink_address = f"{ip}:{sink_port}"

    server_worker = ServerWorker(ventilator_address, sink_address)
    executor = Executor(server_worker)

def host_pipeline():
    scheduler = Scheduler()



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
    else:
        host_address = args.destination
        ip = host_address[:host_address.find(':')]
        port = host_address[host_address.find(':') + 1:]
        # Do worker things
