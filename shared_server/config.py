"""Configuration management for the shared server system."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile


class ServerConfig:
    """Configuration manager for the shared server."""
    
    def __init__(self, app_config_file: Optional[Path] = None, mcp_config_file: Optional[Path] = None):
        if app_config_file is None:
            config_dir = Path(tempfile.gettempdir()) / "walls_shared_server"
            config_dir.mkdir(exist_ok=True)
            app_config_file = config_dir / "APP_config.json"
            
        if mcp_config_file is None:
            config_dir = Path(tempfile.gettempdir()) / "walls_shared_server"
            config_dir.mkdir(exist_ok=True)
            mcp_config_file = config_dir / "MCP_config.json"
            
        self.app_config_file = app_config_file
        self.mcp_config_file = mcp_config_file
        self.app_config = self._load_app_config()
        self.mcp_config = self._load_mcp_config()
        
    def _load_app_config(self) -> Dict[str, Any]:
        """Load application configuration from JSON file."""
        # Load from APP_config.json in shared_server directory
        app_config_json_path = Path(__file__).parent / "APP_config.json"
        if app_config_json_path.exists():
            try:
                with open(app_config_json_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                raise RuntimeError(f"Failed to load APP_config.json: {e}")
        else:
            raise RuntimeError(f"APP_config.json not found at {app_config_json_path}")
        
    def _load_mcp_config(self) -> Dict[str, Any]:
        """Load MCP configuration from JSON file."""
        # Load from MCP_config.json in shared_server directory
        mcp_config_json_path = Path(__file__).parent / "MCP_config.json"
        if mcp_config_json_path.exists():
            try:
                with open(mcp_config_json_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                raise RuntimeError(f"Failed to load MCP_config.json: {e}")
        else:
            raise RuntimeError(f"MCP_config.json not found at {mcp_config_json_path}")
        
    def save(self):
        """Save both configurations to their respective files."""
        self.save_app_config()
        self.save_mcp_config()
        
    def save_app_config(self):
        """Save application configuration to file."""
        try:
            with open(self.app_config_file, 'w') as f:
                json.dump(self.app_config, f, indent=2)
        except IOError as e:
            print(f"Error saving app config: {e}")
            
    def save_mcp_config(self):
        """Save MCP configuration to JSON file."""
        mcp_config_json_path = Path(__file__).parent / "MCP_config.json"
        try:
            with open(mcp_config_json_path, 'w') as f:
                json.dump(self.mcp_config, f, indent=2)
        except IOError as e:
            print(f"Error saving MCP config: {e}")
    
    def save_config(self):
        """Alias for save method for backward compatibility."""
        self.save()
            
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration."""
        return self.app_config.get("server", {})
        
    def get_app_config(self, app_name: str) -> Dict[str, Any]:
        """Get configuration for a specific app."""
        return self.app_config.get("apps", {}).get(app_name, {})
        
    def set_app_config(self, app_name: str, config: Dict[str, Any]):
        """Set configuration for a specific app."""
        if "apps" not in self.app_config:
            self.app_config["apps"] = {}
        self.app_config["apps"][app_name] = config
        self.save_app_config()
    
    def get_mcp_servers(self) -> Dict[str, Any]:
        """Get all MCP server configurations."""
        return self.mcp_config.get("mcp_servers", {})
    
    def get_mcp_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific MCP server."""
        return self.mcp_config.get("mcp_servers", {}).get(server_name)
    
    def set_mcp_server_config(self, server_name: str, key: str, value: Any) -> None:
        """Set a specific configuration value for an MCP server."""
        if "mcp_servers" not in self.mcp_config:
            self.mcp_config["mcp_servers"] = {}
        if server_name not in self.mcp_config["mcp_servers"]:
            self.mcp_config["mcp_servers"][server_name] = {}
        
        self.mcp_config["mcp_servers"][server_name][key] = value
        self.save_mcp_config()
    
    def is_mcp_server_enabled(self, server_name: str) -> bool:
        """Check if an MCP server is enabled."""
        server_config = self.get_mcp_server_config(server_name)
        return server_config.get("enabled", False) if server_config else False
    
    def enable_mcp_server(self, server_name: str) -> None:
        """Enable an MCP server."""
        self.set_mcp_server_config(server_name, "enabled", True)
    
    def disable_mcp_server(self, server_name: str) -> None:
        """Disable an MCP server."""
        self.set_mcp_server_config(server_name, "enabled", False)
    
    def get_mcp_server_port(self, server_name: str) -> Optional[int]:
        """Get the port for an MCP server."""
        server_config = self.get_mcp_server_config(server_name)
        return server_config.get("port") if server_config else None
    
    def set_mcp_server_process_id(self, server_name: str, process_id: Optional[int]) -> None:
        """Set the process ID for a running MCP server."""
        self.set_mcp_server_config(server_name, "process_id", process_id)
        
    def get_app_port(self, app_name: str) -> Optional[int]:
        """Get the configured port for an app."""
        app_config = self.get_app_config(app_name)
        return app_config.get("port")
        
    def set_app_port(self, app_name: str, port: int):
        """Set the port for an app."""
        if "apps" not in self.app_config:
            self.app_config["apps"] = {}
        if app_name not in self.app_config["apps"]:
            self.app_config["apps"][app_name] = {}
        self.app_config["apps"][app_name]["port"] = port
        self.save_app_config()

    def set_app_description(self, app_name: str, description: str):
        """Set the description for an app."""
        if "apps" not in self.app_config:
            self.app_config["apps"] = {}
        if app_name not in self.app_config["apps"]:
            self.app_config["apps"][app_name] = {}
        self.app_config["apps"][app_name]["description"] = description
        self.save_app_config()

        
    def is_app_enabled(self, app_name: str) -> bool:
        """Check if an app is enabled."""
        app_config = self.get_app_config(app_name)
        return app_config.get("enabled", True)
        
    def enable_app(self, app_name: str, enabled: bool = True):
        """Enable or disable an app."""
        if "apps" not in self.app_config:
            self.app_config["apps"] = {}
        if app_name not in self.app_config["apps"]:
            self.app_config["apps"][app_name] = {}
        self.app_config["apps"][app_name]["enabled"] = enabled
        self.save_app_config()
        
    def get_base_port(self) -> int:
        """Get the base port for the server."""
        return self.get_server_config().get("base_port", 9000)
        
    def get_max_apps(self) -> int:
        """Get the maximum number of apps."""
        return self.get_server_config().get("max_apps", 10)
        
    def get_timeout(self) -> float:
        """Get the connection timeout."""
        return self.get_server_config().get("timeout", 5.0)


# Global config instance
_config: Optional[ServerConfig] = None


def get_config() -> ServerConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        # Use only the JSON files in the shared_server directory
        _config = ServerConfig()
    return _config