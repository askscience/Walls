"""Configuration Manager for handling JSON config files."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from PySide6.QtCore import QObject, Signal


class ConfigManager(QObject):
    """Manages loading and saving of configuration files."""
    
    config_changed = Signal(str, dict)  # config_name, config_data
    
    def __init__(self, base_path: str = None):
        super().__init__()
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self._configs = {}
        self._config_paths = {
            'app': self.base_path / 'shared_server' / 'APP_config.json',
            'mcp': self.base_path / 'shared_server' / 'MCP_config.json',
            'rag': self.base_path / 'rag' / 'config.json',
            'voice': self.base_path / 'ai_interface' / 'voice_mode' / 'config' / 'voice_config.json'
        }
    
    def load_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Load a configuration file."""
        if config_name not in self._config_paths:
            raise ValueError(f"Unknown config: {config_name}")
        
        config_path = self._config_paths[config_name]
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                self._configs[config_name] = config_data
                return config_data
            else:
                print(f"Config file not found: {config_path}")
                return None
        except Exception as e:
            print(f"Error loading config {config_name}: {e}")
            return None
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """Save a configuration file."""
        if config_name not in self._config_paths:
            raise ValueError(f"Unknown config: {config_name}")
        
        config_path = self._config_paths[config_name]
        
        try:
            # Create directory if it doesn't exist
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save with proper formatting
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self._configs[config_name] = config_data
            self.config_changed.emit(config_name, config_data)
            return True
        except Exception as e:
            print(f"Error saving config {config_name}: {e}")
            return False
    
    def get_config(self, config_name: str) -> Optional[Dict[str, Any]]:
        """Get cached config data or load if not cached."""
        if config_name in self._configs:
            return self._configs[config_name]
        return self.load_config(config_name)
    
    def load_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load all configuration files."""
        configs = {}
        for config_name in self._config_paths.keys():
            config_data = self.load_config(config_name)
            if config_data is not None:
                configs[config_name] = config_data
        return configs
    
    def validate_config(self, config_name: str, config_data: Dict[str, Any]) -> tuple[bool, str]:
        """Basic validation for config data."""
        try:
            # Basic JSON serialization test
            json.dumps(config_data)
            
            # Config-specific validation
            if config_name == 'app':
                required_keys = ['server', 'apps', 'logging', 'security']
                for key in required_keys:
                    if key not in config_data:
                        return False, f"Missing required key: {key}"
            
            elif config_name == 'mcp':
                required_keys = ['mcp_servers', 'logging']
                for key in required_keys:
                    if key not in config_data:
                        return False, f"Missing required key: {key}"
            
            elif config_name == 'rag':
                required_keys = ['data_dir', 'chroma_db_path', 'ollama_embedding_model']
                for key in required_keys:
                    if key not in config_data:
                        return False, f"Missing required key: {key}"
            
            elif config_name == 'voice':
                required_keys = ['audio', 'recognition']
                for key in required_keys:
                    if key not in config_data:
                        return False, f"Missing required key: {key}"
            
            return True, "Valid"
        
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def backup_config(self, config_name: str) -> bool:
        """Create a backup of the current config file."""
        if config_name not in self._config_paths:
            return False
        
        config_path = self._config_paths[config_name]
        if not config_path.exists():
            return False
        
        try:
            backup_path = config_path.with_suffix('.json.backup')
            import shutil
            shutil.copy2(config_path, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup for {config_name}: {e}")
            return False