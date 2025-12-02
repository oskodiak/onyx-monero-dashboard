"""
Onyx Monero Daemon - Configuration Management
Handles wallet, pool, and worker configuration persistence
Onyx Digital Intelligence Development
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class MiningConfig:
    """Mining configuration structure"""
    wallet_address: str = "YOUR_WALLET_ADDRESS_HERE"
    pool_url: str = "pool.supportxmr.com:443"
    worker_name: str = "onyx-miner"
    use_ssl: bool = True
    profile_name: str = "Default Profile"
    
    def is_valid(self) -> tuple[bool, str]:
        """Validate configuration"""
        if not self.wallet_address or self.wallet_address == "YOUR_WALLET_ADDRESS_HERE":
            return False, "Wallet address must be configured"
        
        if not self.pool_url:
            return False, "Pool URL is required"
            
        if ":" not in self.pool_url:
            return False, "Pool URL must include port (e.g., pool.example.com:443)"
            
        if not self.worker_name:
            return False, "Worker name is required"
            
        return True, ""

class ConfigManager:
    """Configuration file management"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".onyx_monero"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True, mode=0o700)
        
    def load_config(self) -> MiningConfig:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    
                config = MiningConfig(**data)
                logger.info(f"Loaded configuration: {config.profile_name}")
                return config
            else:
                logger.info("No config file found, using defaults")
                return MiningConfig()
                
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return MiningConfig()
    
    def save_config(self, config: MiningConfig) -> bool:
        """Save configuration to file"""
        try:
            # Validate before saving
            valid, error = config.is_valid()
            if not valid:
                logger.error(f"Invalid config: {error}")
                return False
            
            # Ensure config directory exists
            self.config_dir.mkdir(exist_ok=True, mode=0o700)
            
            # Write config file with secure permissions
            with open(self.config_file, 'w') as f:
                json.dump(asdict(config), f, indent=2)
            
            # Set secure permissions (only owner can read/write)
            os.chmod(self.config_file, 0o600)
            
            logger.info(f"Configuration saved: {config.profile_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def get_xmrig_config_path(self) -> Path:
        """Get path for xmrig configuration"""
        return self.config_dir / "xmrig-runtime.json"
    
    def get_socket_path(self) -> Path:
        """Get daemon socket path"""
        return self.config_dir / "daemon.sock"
    
    def generate_xmrig_config(self, config: MiningConfig, threads: int, priority: int) -> dict:
        """Generate xmrig configuration"""
        return {
            "autosave": True,
            "cpu": {
                "enabled": True,
                "huge-pages": True,
                "hw-aes": None,
                "priority": priority,
                "max-threads-hint": threads
            },
            "pools": [
                {
                    "url": config.pool_url,
                    "user": config.wallet_address,
                    "pass": config.worker_name,
                    "keepalive": True,
                    "tls": config.use_ssl
                }
            ],
            "version": "6.21.0",
            "background": False,
            "colors": True,
            "donate-level": 1,
            "log-file": str(self.config_dir / "xmrig.log"),
            "api": {
                "id": None,
                "worker-id": config.worker_name
            }
        }
    
    def create_default_config_if_missing(self) -> MiningConfig:
        """Create default config file if it doesn't exist"""
        if not self.config_file.exists():
            default_config = MiningConfig()
            self.save_config(default_config)
            logger.info("Created default configuration file")
        
        return self.load_config()