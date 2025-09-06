"""Handlers package for Browser MCP server."""

from handlers.navigation_handler import NavigationHandler
from handlers.bookmark_handler import BookmarkHandler
from handlers.page_handler import PageHandler
from handlers.adblock_handler import AdblockHandler

__all__ = ["NavigationHandler", "BookmarkHandler", "PageHandler", "AdblockHandler"]