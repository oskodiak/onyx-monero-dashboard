"""
Onyx Monero Daemon - XMrig Process Controller
Manages xmrig process lifecycle, monitoring, and cleanup
Onyx Digital Intelligence Development
"""

import os
import json
import signal
import subprocess
import threading
import time
import logging
from pathlib import Path
from typing import Optional, Callable
from .state import MinerState, MiningMode, SystemInfo
from .config import ConfigManager, MiningConfig

logger = logging.getLogger(__name__)

class XMrigController:
    """XMrig process management and monitoring"""
    
    def __init__(self, state: MinerState, config_manager: ConfigManager):
        self.state = state
        self.config_manager = config_manager
        self.xmrig_process: Optional[subprocess.Popen] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_monitoring = threading.Event()
        
        # Ensure xmrig is available
        if not self._check_xmrig_available():
            self.state.set_error("XMrig not found in PATH")
    
    def _check_xmrig_available(self) -> bool:
        """Check if xmrig is available in PATH"""
        try:
            result = subprocess.run(
                ["xmrig", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0] if result.stdout else "unknown"
                logger.info(f"XMrig available: {version_line}")
                return True
            else:
                logger.error("XMrig version check failed")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"XMrig not available: {e}")
            return False
    
    def start_mining(self, mode: MiningMode, config: MiningConfig) -> bool:
        """Start mining with specified mode"""
        if mode == MiningMode.STOPPED:
            logger.error("Cannot start mining in STOPPED mode")
            return False
        
        # Stop any existing mining (quick stop for mode switches)
        if self.is_mining():
            self._quick_stop_mining("Starting new mode")
        
        # Calculate threads and priority
        threads, priority = self.state.calculate_threads_for_mode(mode)
        
        # Validate configuration
        valid, error = config.is_valid()
        if not valid:
            self.state.set_error(f"Invalid configuration: {error}")
            return False
        
        # Generate xmrig config
        xmrig_config = self.config_manager.generate_xmrig_config(config, threads, priority)
        config_path = self.config_manager.get_xmrig_config_path()
        
        try:
            # Write xmrig config file
            with open(config_path, 'w') as f:
                json.dump(xmrig_config, f, indent=2)
            os.chmod(config_path, 0o600)  # Secure permissions
            
            # Start xmrig process
            cmd = ["xmrig", "--config", str(config_path)]
            
            self.xmrig_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Update state
            self.state.start_mining(mode, self.xmrig_process.pid, threads)
            
            # Start monitoring thread
            self.stop_monitoring.clear()
            self.monitor_thread = threading.Thread(
                target=self._monitor_xmrig,
                daemon=True
            )
            self.monitor_thread.start()
            
            logger.info(f"Started xmrig: PID {self.xmrig_process.pid}, {threads} threads, {mode.value} mode")
            return True
            
        except Exception as e:
            self.state.set_error(f"Failed to start xmrig: {e}")
            logger.error(f"Failed to start xmrig: {e}")
            return False
    
    def _quick_stop_mining(self, reason: str = "Quick stop") -> bool:
        """Quick stop mining process without waiting for graceful shutdown"""
        if not self.is_mining():
            return True
        
        logger.info(f"Quick stopping mining: {reason}")
        
        try:
            # Signal monitoring thread to stop
            self.stop_monitoring.set()
            
            # Force kill xmrig process immediately
            if self.xmrig_process:
                pid = self.xmrig_process.pid
                
                try:
                    # Force kill immediately for quick mode switch
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
                    logger.info(f"XMrig PID {pid} force killed for quick restart")
                        
                except ProcessLookupError:
                    # Process already dead
                    logger.info(f"XMrig PID {pid} already terminated")
                
                self.xmrig_process = None
            
            # Wait for monitor thread to finish (short timeout for quick stop)
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=0.5)
            
            # Update state
            self.state.stop_mining(reason)
            
            logger.info("Mining quick stopped successfully")
            return True
            
        except Exception as e:
            error_msg = f"Error quick stopping mining: {e}"
            logger.error(error_msg)
            self.state.set_error(error_msg)
            return False

    def stop_mining(self, reason: str = "User requested") -> bool:
        """Stop mining and cleanup"""
        if not self.is_mining():
            return True
        
        try:
            # Signal monitoring thread to stop
            self.stop_monitoring.set()
            
            # Terminate xmrig process
            if self.xmrig_process:
                pid = self.xmrig_process.pid
                
                try:
                    # Try graceful shutdown first
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
                    
                    # Wait for graceful shutdown
                    try:
                        self.xmrig_process.wait(timeout=5)
                        logger.info(f"XMrig PID {pid} terminated gracefully")
                    except subprocess.TimeoutExpired:
                        # Force kill if needed
                        logger.warning(f"XMrig PID {pid} did not respond to SIGTERM, force killing")
                        os.killpg(os.getpgid(pid), signal.SIGKILL)
                        self.xmrig_process.wait(timeout=2)
                        
                except ProcessLookupError:
                    # Process already dead
                    logger.info(f"XMrig PID {pid} already terminated")
                
                self.xmrig_process = None
            
            # Cleanup any orphaned xmrig processes
            self._cleanup_orphaned_processes()
            
            # Wait for monitor thread to finish
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=2)
            
            # Update state
            self.state.stop_mining(reason)
            
            # Clean up config file
            config_path = self.config_manager.get_xmrig_config_path()
            if config_path.exists():
                config_path.unlink()
            
            logger.info(f"Mining stopped successfully: {reason}")
            return True
            
        except Exception as e:
            error_msg = f"Error stopping mining: {e}"
            self.state.set_error(error_msg)
            logger.error(error_msg)
            return False
    
    def is_mining(self) -> bool:
        """Check if mining is currently active"""
        if not self.xmrig_process:
            return False
        
        # Check if process is still running
        poll_result = self.xmrig_process.poll()
        if poll_result is not None:
            # Process has terminated
            logger.info(f"XMrig process terminated with exit code {poll_result}")
            self.xmrig_process = None
            self.state.stop_mining("Process terminated unexpectedly")
            return False
        
        return True
    
    def get_mining_status(self) -> dict:
        """Get detailed mining status"""
        status = self.state.get_status_dict()
        
        # Add basic system info (thermal disabled due to hanging)
        try:
            status.update({
                "cpu_info": SystemInfo.get_cpu_info(),
                "memory_info": SystemInfo.get_memory_info()
                # "thermal_info": SystemInfo.get_thermal_info()  # Disabled - causes hanging
            })
        except Exception as e:
            logger.warning(f"System info unavailable: {e}")
        
        return status
    
    def _monitor_xmrig(self):
        """Monitor xmrig process output and status"""
        if not self.xmrig_process or not self.xmrig_process.stdout:
            return
        
        logger.info("Started xmrig monitoring thread")
        
        try:
            while not self.stop_monitoring.is_set() and self.xmrig_process:
                # Check if process is still alive
                if self.xmrig_process.poll() is not None:
                    self.state.stop_mining("Process terminated unexpectedly")
                    break
                
                # Read output with timeout
                try:
                    # Use select/poll for non-blocking read with timeout
                    import select
                    if select.select([self.xmrig_process.stdout], [], [], 1):
                        line = self.xmrig_process.stdout.readline()
                        if line:
                            line = line.strip()
                            if line:
                                self._process_xmrig_output(line)
                    
                except Exception as e:
                    logger.error(f"Error reading xmrig output: {e}")
                    break
                
                # Brief sleep to prevent excessive CPU usage
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"XMrig monitoring error: {e}")
            self.state.set_error(f"Monitoring error: {e}")
        
        logger.info("XMrig monitoring thread stopped")
    
    def _process_xmrig_output(self, line: str):
        """Process xmrig output line and extract information"""
        # Add to log buffer
        self.state.add_log(line)
        
        # Extract hashrate if present
        if "speed" in line.lower() and "h/s" in line.lower():
            try:
                # Parse hashrate from typical xmrig output
                # Example: "speed 10s/60s/15m 1234.5 1245.6 1250.0 H/s max 1300.0 H/s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if "h/s" in part.lower() and i > 0:
                        # Try to find the hashrate value before "H/s"
                        potential_hashrate = parts[i-1]
                        try:
                            float(potential_hashrate)  # Validate it's a number
                            self.state.update_hashrate(f"{potential_hashrate} H/s")
                            break
                        except ValueError:
                            continue
            except Exception as e:
                logger.debug(f"Failed to parse hashrate from: {line}")
        
        # Check for errors
        if any(keyword in line.lower() for keyword in ["error", "failed", "cannot", "unable"]):
            if "error" in line.lower():
                self.state.set_error(f"XMrig error: {line}")
    
    def _cleanup_orphaned_processes(self):
        """Clean up any orphaned xmrig processes"""
        try:
            # Use pkill to clean up any remaining xmrig processes
            subprocess.run(
                ["pkill", "-f", "xmrig"],
                capture_output=True,
                timeout=5
            )
        except Exception as e:
            logger.debug(f"Could not clean up orphaned processes: {e}")
    
    def shutdown(self):
        """Shutdown controller and cleanup resources"""
        logger.info("Shutting down XMrig controller")
        
        if self.is_mining():
            self.stop_mining("Daemon shutdown")
        
        # Clean up any remaining processes
        self._cleanup_orphaned_processes()
        
        logger.info("XMrig controller shutdown complete")