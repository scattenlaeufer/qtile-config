import importlib
import socket
from libqtile.log_utils import logger

hostname: str = socket.gethostname().replace('.', '_').replace('-', '_')

try:
    cfg = importlib.import_module(f'hosts.{hostname}')
    logger.info(f'hosts: loaded config for {hostname!r}')
except ModuleNotFoundError:
    from hosts import default as cfg
    logger.warning(f'hosts: no config for {hostname!r}, using default')
