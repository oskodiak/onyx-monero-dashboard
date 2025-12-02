"""
Onyx Monero GUI Package
Professional mining dashboard interface
Onyx Digital Intelligence Development
"""

from .theme import OnyxTheme, FontManager
from .ipc_client import IPCClient, ConnectionStatus
from .main_window import OnyxMinerMainWindow

__version__ = "1.0.0"
__all__ = [
    'OnyxTheme',
    'FontManager', 
    'IPCClient',
    'ConnectionStatus',
    'OnyxMinerMainWindow'
]