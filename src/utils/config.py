import yaml
import os
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_file: str = 'config/config.yaml'):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.load_config()
        
    def load_config(self) -> None:
        """Load configuration from YAML file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = yaml.safe_load(f)
            else:
                self.config = self.get_default_config()
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self.get_default_config()
            
    def save_config(self) -> None:
        """Save configuration to YAML file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'email': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'from_address': 'event-manager@localhost'
            },
            'event_viewer': {
                'refresh_interval': 30,
                'max_events': 1000,
                'default_log_type': 'System'
            },
            'event_manager': {
                'history_retention': 86400,
                'max_rules': 100
            },
            'logging': {
                'level': 'INFO',
                'file_retention_days': 30,
                'max_file_size_mb': 10
            },
            'ui': {
                'theme': 'default',
                'language': 'en',
                'show_system_tray': True,
                'minimize_to_tray': True
            }
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
                
        return value
        
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key"""
        keys = key.split('.')
        current = self.config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
            
        current[keys[-1]] = value
        self.save_config()
        
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        for key, value in updates.items():
            self.set(key, value)
            
    def reset(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.get_default_config()
        self.save_config() 