"""Handlers package for Word Editor MCP server."""

from .text_handler import TextHandler
from .file_handler import FileHandler
from .cli_handler import CLIHandler

__all__ = ["TextHandler", "FileHandler", "CLIHandler"]