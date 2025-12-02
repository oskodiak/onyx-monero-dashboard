"""
Onyx Monero GUI - IPC Client
Communication with daemon via Unix socket
Onyx Digital Intelligence Development
"""

import json
import socket
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

logger = logging.getLogger(__name__)

class IPCClient(QObject):
    """IPC client for daemon communication"""
    
    # Signals for GUI updates
    status_updated = pyqtSignal(dict)
    connection_changed = pyqtSignal(bool)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.socket_path = Path.home() / ".onyx_monero" / "daemon.sock"
        self.connected = False
        
        # Status polling timer (start disabled)
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.request_status)
        # Don't start automatically - will be started after initial connection
        
        logger.info("IPC client initialized")
        
        # Test connection with simple ping
        self.test_connection()
    
    def _send_request(self, request: Dict[str, Any], timeout: float = 10.0) -> Optional[Dict[str, Any]]:
        """Send request to daemon and return response"""
        try:
            # Create socket
            client_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client_socket.settimeout(timeout)
            
            try:
                # Connect to daemon
                client_socket.connect(str(self.socket_path))
                
                # Send request
                request_data = json.dumps(request).encode('utf-8')
                client_socket.sendall(request_data)
                
                # Receive response
                response_data = client_socket.recv(8192)  # Increased buffer for status data
                response = json.loads(response_data.decode('utf-8'))
                
                # Update connection status
                if not self.connected:
                    self.connected = True
                    self.connection_changed.emit(True)
                    logger.info("Connected to daemon")
                    # Status polling disabled - causes daemon to hang
                    # if not self.status_timer.isActive():
                    #     self.status_timer.start(5000)  # Poll every 5 seconds
                
                return response
                
            finally:
                client_socket.close()
                
        except (ConnectionRefusedError, FileNotFoundError):
            if self.connected:
                self.connected = False
                self.connection_changed.emit(False)
                logger.warning("Lost connection to daemon")
            return None
            
        except socket.timeout:
            logger.error(f"Request timeout: {request.get('cmd', 'unknown')}")
            self.error_occurred.emit("Request timeout - daemon may be busy")
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            self.error_occurred.emit("Invalid response from daemon")
            return None
            
        except Exception as e:
            logger.error(f"IPC error: {e}")
            self.error_occurred.emit(f"Communication error: {e}")
            return None
    
    def test_connection(self):
        """Test daemon connection with simple ping"""
        response = self._send_request({"cmd": "ping"}, timeout=3.0)
        if response and response.get("ok"):
            logger.info("Daemon connection test successful")
        else:
            logger.warning("Daemon connection test failed")
    
    def request_status(self):
        """Request status from daemon"""
        response = self._send_request({"cmd": "status"})
        if response and response.get("ok"):
            self.status_updated.emit(response)
        elif response:
            error_msg = response.get("error", "Unknown error")
            self.error_occurred.emit(f"Status error: {error_msg}")
    
    def start_mining(self, mode: str) -> bool:
        """Start mining with specified mode"""
        if mode not in ["background", "money_hunter"]:
            self.error_occurred.emit(f"Invalid mining mode: {mode}")
            return False
        
        response = self._send_request({"cmd": "start", "mode": mode}, timeout=60.0)
        if response and response.get("ok"):
            logger.info(f"Started {mode} mining")
            # Immediately request status update
            self.request_status()
            return True
        elif response:
            error_msg = response.get("error", "Unknown error")
            self.error_occurred.emit(f"Failed to start mining: {error_msg}")
            return False
        else:
            self.error_occurred.emit("Cannot communicate with daemon")
            return False
    
    def stop_mining(self) -> bool:
        """Stop mining"""
        response = self._send_request({"cmd": "stop"}, timeout=30.0)
        if response and response.get("ok"):
            logger.info("Mining stopped")
            # Immediately request status update
            self.request_status()
            return True
        elif response:
            error_msg = response.get("error", "Unknown error")
            self.error_occurred.emit(f"Failed to stop mining: {error_msg}")
            return False
        else:
            self.error_occurred.emit("Cannot communicate with daemon")
            return False
    
    def get_config(self) -> Optional[Dict[str, Any]]:
        """Get current configuration"""
        response = self._send_request({"cmd": "config_get"})
        if response and response.get("ok"):
            return response.get("config", {})
        elif response:
            error_msg = response.get("error", "Unknown error")
            self.error_occurred.emit(f"Failed to get config: {error_msg}")
            return None
        else:
            self.error_occurred.emit("Cannot communicate with daemon")
            return None
    
    def set_config(self, config: Dict[str, Any]) -> bool:
        """Set configuration"""
        request = {"cmd": "config_set", **config}
        response = self._send_request(request)
        if response and response.get("ok"):
            logger.info("Configuration updated")
            return True
        elif response:
            error_msg = response.get("error", "Unknown error")
            self.error_occurred.emit(f"Failed to save config: {error_msg}")
            return False
        else:
            self.error_occurred.emit("Cannot communicate with daemon")
            return False
    
    def get_system_info(self) -> Optional[Dict[str, Any]]:
        """Get system information"""
        response = self._send_request({"cmd": "system_info"})
        if response and response.get("ok"):
            return {
                "cpu_info": response.get("cpu_info", {}),
                "memory_info": response.get("memory_info", {}),
                "thermal_info": response.get("thermal_info", {})
            }
        return None
    
    def ping_daemon(self) -> bool:
        """Ping daemon to check connectivity"""
        response = self._send_request({"cmd": "ping"}, timeout=3.0)
        return response and response.get("ok", False)
    
    def is_connected(self) -> bool:
        """Check if connected to daemon"""
        return self.connected
    
    def start_polling(self):
        """Start status polling"""
        if not self.status_timer.isActive():
            self.status_timer.start(2000)
            logger.info("Started status polling")
    
    def stop_polling(self):
        """Stop status polling"""
        if self.status_timer.isActive():
            self.status_timer.stop()
            logger.info("Stopped status polling")

class ConnectionStatus:
    """Connection status helper"""
    
    def __init__(self, ipc_client: IPCClient):
        self.ipc_client = ipc_client
        self.last_status = {}
        self.error_count = 0
        
        # Connect to signals
        ipc_client.connection_changed.connect(self.on_connection_changed)
        ipc_client.error_occurred.connect(self.on_error)
        ipc_client.status_updated.connect(self.on_status_updated)
    
    def on_connection_changed(self, connected: bool):
        """Handle connection state change"""
        if connected:
            self.error_count = 0
            logger.info("Daemon connection established")
        else:
            logger.warning("Daemon connection lost")
    
    def on_error(self, error_message: str):
        """Handle error"""
        self.error_count += 1
        logger.error(f"IPC error ({self.error_count}): {error_message}")
        
        # If too many consecutive errors, suggest daemon restart
        if self.error_count > 5:
            logger.critical("Multiple IPC errors - daemon may need restart")
    
    def on_status_updated(self, status: dict):
        """Handle status update"""
        self.last_status = status
        self.error_count = 0  # Reset error count on successful status
    
    def get_connection_message(self) -> str:
        """Get user-friendly connection status message"""
        if self.ipc_client.is_connected():
            return "Connected to daemon"
        else:
            return "Daemon not running. Start with: systemctl start onyx-monero-daemon"
    
    def get_last_status(self) -> dict:
        """Get last known status"""
        return self.last_status.copy()
    
    def is_healthy(self) -> bool:
        """Check if connection is healthy"""
        return self.ipc_client.is_connected() and self.error_count < 3