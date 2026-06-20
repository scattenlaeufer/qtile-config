import importlib
import socket
from libqtile.log_utils import logger

_hostname = socket.gethostname().replace('.', '_').replace('-', '_')

try:
    cfg = importlib.import_module(f'hosts.{_hostname}')
    logger.info(f'hosts: loaded config for {_hostname!r}')
except ModuleNotFoundError:
    from hosts import default as cfg
    logger.warning(f'hosts: no config for {_hostname!r}, using default')
