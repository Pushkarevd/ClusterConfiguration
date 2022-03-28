import socket


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


