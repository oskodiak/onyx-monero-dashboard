"""
Onyx Monero Daemon - State Management
Tracks mining state, logs, and system information
Onyx Digital Intelligence Development
"""

import logging
import psutil
import time
from collections import deque
from threading import Lock
from typing import Optional, List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class MiningMode(Enum):
    """Mining operation modes"""
    STOPPED = "stopped"
    BACKGROUND = "background"  # ~50% threads, low priority
    MONEY_HUNTER = "money_hunter"  # ~75-80% threads, high priority

class MinerState:
    """Thread-safe miner state management"""
    
    def __init__(self):
        self._lock = Lock()
        self._mode = MiningMode.STOPPED
        self._xmrig_pid: Optional[int] = None
        self._threads_active = 0
        self._total_threads = psutil.cpu_count(logical=True)
        self._log_buffer = deque(maxlen=50)  # Keep last 50 log lines
        self._last_error: Optional[str] = None
        self._start_time: Optional[float] = None
        self._hashrate: Optional[str] = None
        
        logger.info(f"Initialized miner state - {self._total_threads} CPU threads available")
    
    @property
    def mode(self) -> MiningMode:
        """Get current mining mode"""
        with self._lock:
            return self._mode
    
    @property
    def is_mining(self) -> bool:
        """Check if currently mining"""
        with self._lock:
            return self._mode != MiningMode.STOPPED and self._xmrig_pid is not None
    
    @property
    def xmrig_pid(self) -> Optional[int]:
        """Get xmrig process ID"""
        with self._lock:
            return self._xmrig_pid
    
    @property
    def threads_active(self) -> int:
        """Get active thread count"""
        with self._lock:
            return self._threads_active
    
    @property
    def total_threads(self) -> int:
        """Get total available threads"""
        return self._total_threads
    
    @property
    def hashrate(self) -> Optional[str]:
        """Get current hashrate"""
        with self._lock:
            return self._hashrate
    
    @property
    def uptime_seconds(self) -> Optional[int]:
        """Get mining uptime in seconds"""
        with self._lock:
            if self._start_time and self.is_mining:
                return int(time.time() - self._start_time)
            return None
    
    @property
    def last_error(self) -> Optional[str]:
        """Get last error message"""
        with self._lock:
            return self._last_error
    
    def start_mining(self, mode: MiningMode, pid: int, threads: int) -> bool:
        """Start mining with specified mode"""
        if mode == MiningMode.STOPPED:
            return False
            
        with self._lock:
            self._mode = mode
            self._xmrig_pid = pid
            self._threads_active = threads
            self._start_time = time.time()
            self._last_error = None
            self._hashrate = None
            
            self.add_log(f"Mining started: {mode.value} mode with {threads} threads (PID: {pid})")
            logger.info(f"Mining started: {mode.value} mode, {threads} threads, PID {pid}")
            return True
    
    def stop_mining(self, reason: str = "User requested") -> bool:
        """Stop mining"""
        with self._lock:
            if self._mode == MiningMode.STOPPED:
                return False
                
            old_mode = self._mode.value
            self._mode = MiningMode.STOPPED
            self._xmrig_pid = None
            self._threads_active = 0
            self._start_time = None
            self._hashrate = None
            
            self.add_log(f"Mining stopped: {reason}")
            logger.info(f"Mining stopped: {old_mode} -> stopped, reason: {reason}")
            return True
    
    def set_error(self, error: str):
        """Set error state"""
        with self._lock:
            self._last_error = error
            self.add_log(f"ERROR: {error}")
            logger.error(error)
    
    def clear_error(self):
        """Clear error state"""
        with self._lock:
            self._last_error = None
    
    def add_log(self, message: str):
        """Add log message to buffer"""
        timestamp = time.strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}"
        
        with self._lock:
            self._log_buffer.append(log_line)
        
        # Also log to Python logger
        logger.info(message)
    
    def get_log_tail(self, lines: int = 20) -> List[str]:
        """Get recent log messages"""
        with self._lock:
            return list(self._log_buffer)[-lines:]
    
    def update_hashrate(self, hashrate: str):
        """Update current hashrate"""
        with self._lock:
            self._hashrate = hashrate
    
    def get_status_dict(self) -> Dict[str, Any]:
        """Get complete status as dictionary"""
        with self._lock:
            uptime = None
            if self._start_time and self.is_mining:
                uptime = int(time.time() - self._start_time)
                
            return {
                "mode": self._mode.value,
                "is_mining": self.is_mining,
                "pid": self._xmrig_pid,
                "threads_active": self._threads_active,
                "total_threads": self._total_threads,
                "hashrate": self._hashrate,
                "uptime_seconds": uptime,
                "last_error": self._last_error,
                "log_tail": list(self._log_buffer)
            }
    
    def calculate_threads_for_mode(self, mode: MiningMode) -> tuple[int, int]:
        """Calculate threads and priority for mining mode"""
        if mode == MiningMode.BACKGROUND:
            threads = max(1, int(self._total_threads * 0.5))  # 50%
            priority = 1  # Low priority
        elif mode == MiningMode.MONEY_HUNTER:
            threads = max(1, int(self._total_threads * 0.8))  # 80%
            priority = 3  # High priority
        else:
            threads = 0
            priority = 0
            
        return threads, priority

class SystemInfo:
    """System information and monitoring"""
    
    @staticmethod
    def get_cpu_info() -> Dict[str, Any]:
        """Get CPU information"""
        try:
            cpu_freq = psutil.cpu_freq()
            return {
                "logical_cores": psutil.cpu_count(logical=True),
                "physical_cores": psutil.cpu_count(logical=False),
                "current_freq_mhz": int(cpu_freq.current) if cpu_freq else None,
                "max_freq_mhz": int(cpu_freq.max) if cpu_freq else None,
                "cpu_percent": psutil.cpu_percent(interval=1),
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
        except Exception as e:
            logger.error(f"Failed to get CPU info: {e}")
            return {"logical_cores": psutil.cpu_count(logical=True)}
    
    @staticmethod
    def get_memory_info() -> Dict[str, Any]:
        """Get memory information"""
        try:
            memory = psutil.virtual_memory()
            return {
                "total_gb": round(memory.total / (1024**3), 1),
                "available_gb": round(memory.available / (1024**3), 1),
                "used_percent": memory.percent
            }
        except Exception as e:
            logger.error(f"Failed to get memory info: {e}")
            return {}
    
    @staticmethod
    def get_thermal_info() -> Dict[str, Any]:
        """Get thermal information if available"""
        try:
            temps = psutil.sensors_temperatures()
            if not temps:
                return {}
                
            thermal_info = {}
            for name, entries in temps.items():
                if entries:
                    avg_temp = sum(entry.current for entry in entries) / len(entries)
                    thermal_info[name] = {
                        "current_c": round(avg_temp, 1),
                        "sensors": len(entries)
                    }
            
            return thermal_info
            
        except Exception as e:
            logger.debug(f"Thermal sensors not available: {e}")
            return {}
    
    @staticmethod
    def is_process_running(pid: int) -> bool:
        """Check if process is running"""
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False