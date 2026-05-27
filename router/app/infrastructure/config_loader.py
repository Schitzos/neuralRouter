"""
Configuration loader for Schitzo Neural Router
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigLoader:
    """Loads configuration from YAML and environment variables"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config.yaml"
        self.config: Dict[str, Any] = {}
        
    def load(self) -> Dict[str, Any]:
        """Load configuration from YAML file and environment variables"""
        # Load .env file
        load_dotenv()
        
        # Load YAML config
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        
        # Apply environment variable overrides
        self._apply_env_overrides()
        
        return self.config
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides to config"""
        env_mappings = {
            'SCHITZO_PORT': ('server', 'port'),
            'SCHITZO_AUTH_TOKEN': ('server', 'auth_token'),
            'SCHITZO_LOG_LEVEL': ('logging', 'level'),
            'LANGFUSE_PUBLIC_KEY': ('observability', 'langfuse', 'public_key'),
            'LANGFUSE_SECRET_KEY': ('observability', 'langfuse', 'secret_key'),
            'LANGFUSE_HOST': ('observability', 'langfuse', 'host'),
            'OLLAMA_BASE_URL': ('classifier', 'ollama_url'),
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_value(self.config, config_path, value)
    
    def _set_nested_value(self, config: Dict[str, Any], path: tuple, value: Any):
        """Set a nested value in the config dictionary"""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert port to int if needed
        if path[-1] == 'port' and isinstance(value, str):
            value = int(value)
            
        current[path[-1]] = value


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration - convenience function"""
    loader = ConfigLoader(config_path)
    return loader.load()