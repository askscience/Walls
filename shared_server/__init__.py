"""Shared server package for Walls applications.

Provides a centralized TCP server that multiple applications can use
for CLI command handling and inter-process communication.
"""

from .server import SharedServer, get_shared_server
from .client import send_command_to_app

__version__ = "1.0.0"

__all__ = ['SharedServer', 'get_shared_server', 'send_command_to_app']