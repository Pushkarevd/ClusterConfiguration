import socket
import re
from typing import Tuple, Union


def get_my_ip() -> str:
    """
    Get ip of current machine in local network
    :return: ip as string
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as st:
        try:
            st.connect(('10.255.255.255', 1))
            ip = st.getsockname()[0]
        except socket.error as exc:
            return f'Error, cant connect {exc}'
    return ip


def parse_ip(user_input: str) -> Union[Tuple[int, int], None]:
    """
    Function for parsing ip and port from user input
    @param user_input: str, input from user
    @return: tuple, (ip, port)
    """
    ip_pattern = '^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    port_pattern = '(?<=:)[0-9]{1,6}'

    ip = re.findall(ip_pattern, user_input)
    port = re.findall(port_pattern, user_input)

    if len(ip) != 1 or len(port) != 1:
        return None

    return (ip[0], int(port[0]))
