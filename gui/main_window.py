"""
Onyx Monero GUI - Main Window
Professional mining control interface with Arctic Terminal theme
Onyx Digital Intelligence Development
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                            QPushButton, QLabel, QGroupBox, QTextEdit, QFrame,
                            QMessageBox, QProgressBar, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont, QIcon

from .theme import OnyxTheme, FontManager
from .ipc_client import IPCClient, ConnectionStatus

logger = logging.getLogger(__name__)

class StatusPanel(QGroupBox):
    """Mining status display panel"""
    
    def __init__(self):
        super().__init__("Mining Status")
        self.setStyleSheet(OnyxTheme.get_panel_style())
        self.init_ui()
    
    def init_ui(self):
        """Initialize status panel UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 20, 16, 16)
        
        # Mode and connection status
        status_row = QHBoxLayout()
        
        self.mode_label = QLabel("Mode: Stopped")
        self.mode_label.setFont(FontManager.get_primary_font(14, 600))
        self.mode_label.setStyleSheet(OnyxTheme.get_status_label_style())
        
        self.connection_label = QLabel("Daemon: Disconnected")
        self.connection_label.setFont(FontManager.get_primary_font(12))
        self.connection_label.setStyleSheet(OnyxTheme.get_status_label_style("error"))
        
        status_row.addWidget(self.mode_label, 2)
        status_row.addWidget(self.connection_label, 1)
        layout.addLayout(status_row)
        
        # Mining details
        details_layout = QHBoxLayout()
        
        # Left column
        left_col = QVBoxLayout()
        self.threads_label = QLabel("Threads: 0 / 0")
        self.threads_label.setFont(FontManager.get_primary_font(12))
        self.threads_label.setStyleSheet(f"color: {OnyxTheme.TEXT_SECONDARY};")
        
        self.hashrate_label = QLabel("Hashrate: N/A")
        self.hashrate_label.setFont(FontManager.get_primary_font(12))
        self.hashrate_label.setStyleSheet(f"color: {OnyxTheme.TEXT_SECONDARY};")
        
        left_col.addWidget(self.threads_label)
        left_col.addWidget(self.hashrate_label)
        
        # Right column
        right_col = QVBoxLayout()
        self.uptime_label = QLabel("Uptime: N/A")
        self.uptime_label.setFont(FontManager.get_primary_font(12))
        self.uptime_label.setStyleSheet(f"color: {OnyxTheme.TEXT_SECONDARY};")
        
        self.pool_label = QLabel("Pool: Not configured")
        self.pool_label.setFont(FontManager.get_primary_font(12))
        self.pool_label.setStyleSheet(f"color: {OnyxTheme.TEXT_SECONDARY};")
        
        right_col.addWidget(self.uptime_label)
        right_col.addWidget(self.pool_label)
        
        details_layout.addLayout(left_col)
        details_layout.addLayout(right_col)
        layout.addLayout(details_layout)
    
    def update_status(self, status: dict):
        """Update status panel with new data"""
        # Mode status
        mode = status.get("mode", "stopped").title()
        is_mining = status.get("is_mining", False)
        
        self.mode_label.setText(f"Mode: {mode}")
        if is_mining:
            self.mode_label.setStyleSheet(OnyxTheme.get_status_label_style("active"))
        else:
            self.mode_label.setStyleSheet(OnyxTheme.get_status_label_style())
        
        # Threading info
        threads_active = status.get("threads_active", 0)
        total_threads = status.get("total_threads", 0)
        self.threads_label.setText(f"Threads: {threads_active} / {total_threads}")
        
        # Hashrate
        hashrate = status.get("hashrate")
        if hashrate:
            self.hashrate_label.setText(f"Hashrate: {hashrate}")
        else:
            self.hashrate_label.setText("Hashrate: N/A")
        
        # Uptime
        uptime_seconds = status.get("uptime_seconds")
        if uptime_seconds and is_mining:
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            seconds = uptime_seconds % 60
            if hours > 0:
                uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                uptime_str = f"{minutes:02d}:{seconds:02d}"
            self.uptime_label.setText(f"Uptime: {uptime_str}")
        else:
            self.uptime_label.setText("Uptime: N/A")
    
    def update_connection_status(self, connected: bool, config: dict = None):
        """Update connection status"""
        if connected:
            self.connection_label.setText("Daemon: Connected")
            self.connection_label.setStyleSheet(OnyxTheme.get_status_label_style("active"))
            
            # Update pool info if config available
            if config:
                pool = config.get("pool_url", "Not configured")
                self.pool_label.setText(f"Pool: {pool}")
        else:
            self.connection_label.setText("Daemon: Disconnected")
            self.connection_label.setStyleSheet(OnyxTheme.get_status_label_style("error"))
            self.pool_label.setText("Pool: Not configured")

class ControlPanel(QGroupBox):
    """Mining control buttons panel"""
    
    def __init__(self):
        super().__init__("Mining Controls")
        self.setStyleSheet(OnyxTheme.get_panel_style())
        
        # State tracking
        self.current_mode = "stopped"
        self.daemon_connected = False
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize control panel UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 20, 16, 16)
        
        # Background mining button
        self.background_button = QPushButton("Background Mining")
        self.background_button.setStyleSheet(OnyxTheme.get_button_style("success"))
        self.background_button.setFont(FontManager.get_primary_font(13, 600))
        self.background_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.background_button.setMinimumHeight(48)
        
        # Money hunter button
        self.money_hunter_button = QPushButton("Money Hunter")
        self.money_hunter_button.setStyleSheet(OnyxTheme.get_button_style("primary"))
        self.money_hunter_button.setFont(FontManager.get_primary_font(13, 600))
        self.money_hunter_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.money_hunter_button.setMinimumHeight(52)
        
        # Stop button
        self.stop_button = QPushButton("Stop Mining")
        self.stop_button.setStyleSheet(OnyxTheme.get_button_style("danger"))
        self.stop_button.setFont(FontManager.get_primary_font(13, 600))
        self.stop_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.stop_button.setMinimumHeight(48)
        
        layout.addWidget(self.background_button)
        layout.addWidget(self.money_hunter_button)
        layout.addWidget(self.stop_button)
        
        self.update_button_states()
    
    def update_status(self, status: dict):
        """Update control panel based on status"""
        mode = status.get("mode", "stopped")
        self.current_mode = mode
        self.update_button_states()
    
    def update_connection_status(self, connected: bool):
        """Update connection status"""
        self.daemon_connected = connected
        self.update_button_states()
    
    def update_button_states(self):
        """Update button enabled/disabled states"""
        # Disable all if not connected
        if not self.daemon_connected:
            self.background_button.setEnabled(False)
            self.money_hunter_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            return
        
        # Enable based on current mode
        is_stopped = self.current_mode == "stopped"
        is_background = self.current_mode == "background"
        is_money_hunter = self.current_mode == "money_hunter"
        
        self.background_button.setEnabled(not is_background)
        self.money_hunter_button.setEnabled(not is_money_hunter)
        self.stop_button.setEnabled(not is_stopped)

class LogPanel(QGroupBox):
    """Mining log display panel"""
    
    def __init__(self):
        super().__init__("Status Log")
        self.setStyleSheet(OnyxTheme.get_panel_style())
        self.init_ui()
    
    def init_ui(self):
        """Initialize log panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        
        self.log_text = QTextEdit()
        self.log_text.setStyleSheet(OnyxTheme.get_log_panel_style())
        self.log_text.setFont(FontManager.get_monospace_font(10))
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(180)
        self.log_text.setMinimumHeight(150)
        
        layout.addWidget(self.log_text)
        
        # Add initial message
        self.add_log_message("Onyx Monero Mining Dashboard - Ready")
    
    def update_log(self, log_lines: list):
        """Update log display with new lines"""
        if not log_lines:
            return
        
        # Get last few lines to avoid overwhelming the display
        recent_lines = log_lines[-20:]
        
        # Clear and set new content
        self.log_text.clear()
        for line in recent_lines:
            self.log_text.append(line)
        
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def add_log_message(self, message: str):
        """Add a single log message"""
        self.log_text.append(message)
        
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

class OnyxMinerMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Onyx Monero Mining Dashboard")
        self.setFixedSize(700, 650)
        
        # Apply theme
        self.setStyleSheet(OnyxTheme.get_main_window_style())
        
        # Initialize IPC client
        self.ipc_client = IPCClient()
        self.connection_status = ConnectionStatus(self.ipc_client)
        
        # Connect signals
        self.ipc_client.status_updated.connect(self.on_status_updated)
        self.ipc_client.connection_changed.connect(self.on_connection_changed)
        self.ipc_client.error_occurred.connect(self.on_error)
        
        # Current config cache
        self.current_config = {}
        
        self.init_ui()
        
        # Load initial config
        QTimer.singleShot(1000, self.load_config)
    
    def init_ui(self):
        """Initialize main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("Onyx Monero Mining Dashboard")
        header_label.setFont(FontManager.get_title_font(18))
        header_label.setStyleSheet(f"""
            QLabel {{
                color: {OnyxTheme.PRIMARY_ACCENT};
                padding: 8px 0;
                border-bottom: 2px solid {OnyxTheme.BORDER_SUBTLE};
                margin-bottom: 8px;
            }}
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Status panel
        self.status_panel = StatusPanel()
        layout.addWidget(self.status_panel)
        
        # Control panel
        self.control_panel = ControlPanel()
        layout.addWidget(self.control_panel)
        
        # Connect control signals
        self.control_panel.background_button.clicked.connect(self.start_background_mining)
        self.control_panel.money_hunter_button.clicked.connect(self.start_money_hunter_mining)
        self.control_panel.stop_button.clicked.connect(self.stop_mining)
        
        # Log panel
        self.log_panel = LogPanel()
        layout.addWidget(self.log_panel)
    
    def load_config(self):
        """Load configuration from daemon"""
        config = self.ipc_client.get_config()
        if config:
            self.current_config = config
            self.status_panel.update_connection_status(True, config)
    
    @pyqtSlot(dict)
    def on_status_updated(self, status: dict):
        """Handle status update from daemon"""
        self.status_panel.update_status(status)
        self.control_panel.update_status(status)
        
        # Update log
        log_lines = status.get("log_tail", [])
        if log_lines:
            self.log_panel.update_log(log_lines)
        
        # Check for errors
        error = status.get("last_error")
        if error:
            self.log_panel.add_log_message(f"ERROR: {error}")
    
    @pyqtSlot(bool)
    def on_connection_changed(self, connected: bool):
        """Handle connection status change"""
        self.status_panel.update_connection_status(connected, self.current_config if connected else None)
        self.control_panel.update_connection_status(connected)
        
        if connected:
            self.log_panel.add_log_message("Connected to daemon")
            # Reload config when connected
            QTimer.singleShot(500, self.load_config)
        else:
            self.log_panel.add_log_message("Lost connection to daemon")
    
    @pyqtSlot(str)
    def on_error(self, error_message: str):
        """Handle error message"""
        self.log_panel.add_log_message(f"ERROR: {error_message}")
    
    def start_background_mining(self):
        """Start background mining"""
        self.start_mining("background")
    
    def start_money_hunter_mining(self):
        """Start money hunter mining"""
        self.start_mining("money_hunter")
    
    def start_mining(self, mode: str):
        """Start mining with specified mode"""
        if not self.ipc_client.is_connected():
            self.show_error("Cannot start mining", "Daemon is not connected")
            return
        
        # Check if config is valid
        if not self.current_config or self.current_config.get("wallet_address") == "YOUR_WALLET_ADDRESS_HERE":
            self.show_error("Configuration Required", 
                          "Please configure your wallet address first.\n"
                          "The daemon needs a valid Monero wallet address to mine.")
            return
        
        mode_name = "Background" if mode == "background" else "Money Hunter"
        self.log_panel.add_log_message(f"Starting {mode_name} mining...")
        
        success = self.ipc_client.start_mining(mode)
        if not success:
            self.log_panel.add_log_message(f"Failed to start {mode_name} mining")
    
    def stop_mining(self):
        """Stop mining"""
        if not self.ipc_client.is_connected():
            self.show_error("Cannot stop mining", "Daemon is not connected")
            return
        
        self.log_panel.add_log_message("Stopping mining...")
        
        success = self.ipc_client.stop_mining()
        if not success:
            self.log_panel.add_log_message("Failed to stop mining")
    
    def show_error(self, title: str, message: str):
        """Show error dialog"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStyleSheet(OnyxTheme.get_dialog_style())
        msg_box.exec()
    
    def closeEvent(self, event):
        """Handle window close"""
        try:
            # Stop polling when window closes
            self.ipc_client.stop_polling()
            
            # Disconnect all signals to prevent orphaned connections
            self.ipc_client.status_updated.disconnect()
            self.ipc_client.connection_changed.disconnect()
            self.ipc_client.error_occurred.disconnect()
            
            # Accept the close event
            event.accept()
        except Exception as e:
            # Force close if cleanup fails
            logger.warning(f"Error during close cleanup: {e}")
            event.accept()