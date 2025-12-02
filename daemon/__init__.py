"""
Onyx Monero Daemon Package
Professional xmrig mining control daemon
Onyx Digital Intelligence Development
"""

from .config import ConfigManager, MiningConfig
from .state import MinerState, MiningMode, SystemInfo
from .controller import XMrigController
from .server import DaemonServer, IPCServer, setup_logging

__version__ = "1.0.0"
__all__ = [
    'ConfigManager',
    'MiningConfig', 
    'MinerState',
    'MiningMode',
    'SystemInfo',
    'XMrigController',
    'DaemonServer',
    'IPCServer',
    'setup_logging'
]