import importlib
import socket

_hostname = socket.gethostname().replace(".", "_").replace("-", "_")
try:
    cfg = importlib.import_module(f"hosts.{_hostname}")
except ModuleNotFoundError:
    from hosts import default as cfg
