"""Tool schemas for Browser MCP server."""

TOOL_SCHEMAS = {
    # Navigation tools
    "open_url": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to open in the browser"
            }
        },
        "required": ["url"]
    },
    
    "navigate_back": {
        "type": "object",
        "properties": {},
        "description": "Navigate back in browser history"
    },
    
    "navigate_forward": {
        "type": "object",
        "properties": {},
        "description": "Navigate forward in browser history"
    },
    
    "reload_page": {
        "type": "object",
        "properties": {},
        "description": "Reload the current page"
    },
    
    # Bookmark tools
    "add_bookmark": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to bookmark (optional, uses current page if not provided)"
            },
            "name": {
                "type": "string",
                "description": "The name for the bookmark (optional, uses URL if not provided)"
            }
        }
    },
    
    "get_bookmarks": {
        "type": "object",
        "properties": {},
        "description": "Get all bookmarks as JSON"
    },
    
    # Page interaction tools
    "click_element": {
        "type": "object",
        "properties": {
            "selector": {
                "type": "string",
                "description": "CSS selector for the element to click"
            }
        },
        "required": ["selector"]
    },
    
    "click_text": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The visible text of the link/button to click"
            }
        },
        "required": ["text"]
    },
    
    "get_page_html": {
        "type": "object",
        "properties": {},
        "description": "Get the current page HTML content"
    },
    
    "summarize_page": {
        "type": "object",
        "properties": {},
        "description": "Get a JSON summary of the current page with title, content, and links"
    },
    
    "fill_form": {
        "type": "object",
        "properties": {
            "form_data": {
                "type": "object",
                "description": "Form field data as key-value pairs"
            }
        },
        "required": ["form_data"]
    },
    
    "get_page_content": {
        "type": "object",
        "properties": {
            "format": {
                "type": "string",
                "description": "Output format: 'text' or 'html'",
                "default": "text"
            }
        }
    },
    
    "take_screenshot": {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Optional filename for the screenshot"
            }
        }
    },
    
    "enable_adblock": {
        "type": "object",
        "properties": {},
        "description": "Enable ad blocking for the current session"
    },
    
    "disable_adblock": {
        "type": "object",
        "properties": {},
        "description": "Disable ad blocking for the current session"
    },
    
    "get_adblock_status": {
        "type": "object",
        "properties": {},
        "description": "Get current ad blocking status"
    },
    
    # Adblock tools
    "adblock_enable": {
        "type": "object",
        "properties": {},
        "description": "Enable adblock functionality"
    },
    
    "adblock_disable": {
        "type": "object",
        "properties": {},
        "description": "Disable adblock functionality"
    },
    
    "adblock_toggle": {
        "type": "object",
        "properties": {},
        "description": "Toggle adblock on/off"
    },
    
    "adblock_status": {
        "type": "object",
        "properties": {},
        "description": "Get current adblock status"
    },
    
    "adblock_load_rules": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the adblock rules file or directory"
            },
            "is_directory": {
                "type": "boolean",
                "description": "Whether the path is a directory (loads all .txt files) or a single file",
                "default": False
            }
        },
        "required": ["path"]
    },
    
    "adblock_fetch_easylist": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to download EasyList rules from (optional, uses default if not provided)"
            }
        }
    }
}