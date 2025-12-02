"""
Onyx Monero Daemon - IPC Server
Unix socket server for daemon communication
Onyx Digital Intelligence Development
"""

import os
import json
import socket
import threading
import logging
import signal
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from .state import MinerState, MiningMode
from .config import ConfigManager, MiningConfig
from .controller import XMrigController

logger = logging.getLogger(__name__)

class IPCServer:
    """Unix domain socket IPC server"""
    
    def __init__(self, config_manager: ConfigManager, state: MinerState, controller: XMrigController):
        self.config_manager = config_manager
        self.state = state
        self.controller = controller
        self.socket_path = config_manager.get_socket_path()
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        self.client_threads = []
        
        # Command handlers
        self.handlers = {
            "status": self._handle_status,
            "start": self._handle_start,
            "stop": self._handle_stop,
            "config_get": self._handle_config_get,
            "config_set": self._handle_config_set,
            "system_info": self._handle_system_info,
            "ping": self._handle_ping
        }
    
    def start(self) -> bool:
        """Start IPC server"""
        try:
            # Remove existing socket file if it exists
            if self.socket_path.exists():
                self.socket_path.unlink()
                
            # Create server socket
            self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server_socket.bind(str(self.socket_path))
            
            # Set socket permissions (owner read/write only)
            os.chmod(self.socket_path, 0o600)
            
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"IPC server listening on {self.socket_path}")
            
            # Start accept thread
            accept_thread = threading.Thread(target=self._accept_connections, daemon=True)
            accept_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start IPC server: {e}")
            return False
    
    def stop(self):
        """Stop IPC server"""
        logger.info("Stopping IPC server")
        
        self.running = False
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                logger.error(f"Error closing server socket: {e}")
        
        # Clean up socket file
        try:
            if self.socket_path.exists():
                self.socket_path.unlink()
        except Exception as e:
            logger.error(f"Error removing socket file: {e}")
        
        # Wait for client threads to finish (with timeout)
        for thread in self.client_threads:
            if thread.is_alive():
                thread.join(timeout=1)
        
        logger.info("IPC server stopped")
    
    def _accept_connections(self):
        """Accept incoming connections"""
        while self.running:
            try:
                client_socket, _ = self.server_socket.accept()
                
                # Handle client in separate thread
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket,),
                    daemon=True
                )
                client_thread.start()
                self.client_threads.append(client_thread)
                
                # Clean up finished threads
                self.client_threads = [t for t in self.client_threads if t.is_alive()]
                
            except OSError:
                # Socket was closed
                if self.running:
                    logger.error("Server socket error")
                break
            except Exception as e:
                logger.error(f"Error accepting connection: {e}")
    
    def _handle_client(self, client_socket: socket.socket):
        """Handle individual client connection"""
        try:
            with client_socket:
                # Set receive timeout
                client_socket.settimeout(30)
                
                # Receive request
                data = client_socket.recv(4096)
                if not data:
                    return
                
                try:
                    request = json.loads(data.decode('utf-8'))
                except json.JSONDecodeError as e:
                    response = {"ok": False, "error": f"Invalid JSON: {e}"}
                    self._send_response(client_socket, response)
                    return
                
                # Process request
                response = self._process_request(request)
                self._send_response(client_socket, response)
                
        except socket.timeout:
            logger.debug("Client connection timed out")
        except Exception as e:
            logger.error(f"Error handling client: {e}")
    
    def _send_response(self, client_socket: socket.socket, response: Dict[str, Any]):
        """Send JSON response to client"""
        try:
            response_data = json.dumps(response).encode('utf-8')
            client_socket.sendall(response_data)
        except Exception as e:
            logger.error(f"Error sending response: {e}")
    
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process IPC request and return response"""
        if not isinstance(request, dict) or "cmd" not in request:
            return {"ok": False, "error": "Missing 'cmd' field"}
        
        cmd = request["cmd"]
        if cmd not in self.handlers:
            return {"ok": False, "error": f"Unknown command: {cmd}"}
        
        try:
            return self.handlers[cmd](request)
        except Exception as e:
            logger.error(f"Error handling command '{cmd}': {e}")
            return {"ok": False, "error": f"Command failed: {e}"}
    
    def _handle_status(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status command - minimal response"""
        try:
            # Simple status without locks
            return {
                "ok": True,
                "mining_active": self.state._mode.value != "stopped",
                "current_mode": self.state._mode.value,
                "mining_threads": self.state._threads_active,
                "total_threads": self.state._total_threads
            }
        except Exception:
            return {
                "ok": True,
                "mining_active": False,
                "current_mode": "unknown",
                "mining_threads": 0,
                "total_threads": 72
            }
    
    def _handle_start(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle start command"""
        mode_str = request.get("mode", "").lower()
        
        # Validate mode
        try:
            if mode_str == "background":
                mode = MiningMode.BACKGROUND
            elif mode_str == "money_hunter":
                mode = MiningMode.MONEY_HUNTER
            else:
                return {"ok": False, "error": f"Invalid mode: {mode_str}. Use 'background' or 'money_hunter'"}
        except Exception:
            return {"ok": False, "error": f"Invalid mode: {mode_str}"}
        
        # Load current config
        config = self.config_manager.load_config()
        
        # Validate configuration
        valid, error = config.is_valid()
        if not valid:
            return {"ok": False, "error": f"Configuration error: {error}"}
        
        # Start mining in thread to prevent blocking IPC response
        import threading
        def start_mining_async():
            try:
                success = self.controller.start_mining(mode, config)
                if not success:
                    logger.error(f"Failed to start {mode.value} mining")
            except Exception as e:
                logger.error(f"Error starting mining: {e}")
        
        thread = threading.Thread(target=start_mining_async, daemon=True)
        thread.start()
        
        return {"ok": True, "message": f"Starting {mode.value} mining..."}
    
    def _handle_stop(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle stop command"""
        success = self.controller.stop_mining("User requested via IPC")
        if success:
            return {"ok": True, "message": "Mining stopped"}
        else:
            error = self.state.last_error or "Unknown error"
            return {"ok": False, "error": f"Failed to stop mining: {error}"}
    
    def _handle_config_get(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle config_get command"""
        config = self.config_manager.load_config()
        return {
            "ok": True,
            "config": {
                "wallet_address": config.wallet_address,
                "pool_url": config.pool_url,
                "worker_name": config.worker_name,
                "use_ssl": config.use_ssl,
                "profile_name": config.profile_name
            }
        }
    
    def _handle_config_set(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle config_set command"""
        try:
            # Get current config as base
            current_config = self.config_manager.load_config()
            
            # Update fields if provided
            if "wallet_address" in request:
                current_config.wallet_address = request["wallet_address"]
            if "pool_url" in request:
                current_config.pool_url = request["pool_url"]
            if "worker_name" in request:
                current_config.worker_name = request["worker_name"]
            if "use_ssl" in request:
                current_config.use_ssl = bool(request["use_ssl"])
            if "profile_name" in request:
                current_config.profile_name = request["profile_name"]
            
            # Validate new config
            valid, error = current_config.is_valid()
            if not valid:
                return {"ok": False, "error": f"Invalid configuration: {error}"}
            
            # Save config
            success = self.config_manager.save_config(current_config)
            if success:
                return {"ok": True, "message": "Configuration updated"}
            else:
                return {"ok": False, "error": "Failed to save configuration"}
                
        except Exception as e:
            return {"ok": False, "error": f"Configuration update failed: {e}"}
    
    def _handle_system_info(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system_info command"""
        from .state import SystemInfo
        
        return {
            "ok": True,
            "cpu_info": SystemInfo.get_cpu_info(),
            "memory_info": SystemInfo.get_memory_info(),
            "thermal_info": SystemInfo.get_thermal_info()
        }
    
    def _handle_ping(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping command"""
        return {
            "ok": True,
            "message": "pong",
            "daemon_version": "1.0.0"
        }

class DaemonServer:
    """Main daemon server orchestrator"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.state = MinerState()
        self.controller = XMrigController(self.state, self.config_manager)
        self.ipc_server = IPCServer(self.config_manager, self.state, self.controller)
        self.shutdown_event = threading.Event()
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown_event.set()
    
    def start(self) -> bool:
        """Start daemon server"""
        try:
            logger.info("Starting Onyx Monero Daemon")
            
            # Ensure configuration exists
            self.config_manager.create_default_config_if_missing()
            
            # Stop any existing mining (cleanup from previous runs)
            if self.controller.is_mining():
                self.controller.stop_mining("Daemon restart cleanup")
            
            # Start IPC server
            if not self.ipc_server.start():
                logger.error("Failed to start IPC server")
                return False
            
            logger.info("Onyx Monero Daemon started successfully")
            logger.info("Daemon is running but not mining - waiting for commands")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start daemon: {e}")
            return False
    
    def run(self):
        """Run daemon main loop"""
        try:
            # Wait for shutdown signal
            self.shutdown_event.wait()
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown daemon"""
        logger.info("Shutting down Onyx Monero Daemon")
        
        try:
            # Stop mining
            self.controller.shutdown()
            
            # Stop IPC server
            self.ipc_server.stop()
            
            logger.info("Daemon shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

def setup_logging():
    """Setup daemon logging"""
    log_dir = Path.home() / ".onyx_monero"
    log_dir.mkdir(exist_ok=True, mode=0o700)
    
    log_file = log_dir / "daemon.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Set log file permissions
    if log_file.exists():
        os.chmod(log_file, 0o600)