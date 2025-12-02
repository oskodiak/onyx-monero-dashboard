#!/usr/bin/env python3
"""
Onyx Monero Mining Dashboard - Clean GUI
Simple, functional interface for mining control
"""

import sys
import json
import socket
import logging
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QWidget, QPushButton, QLabel, QTextEdit, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPalette, QColor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MiningController(QThread):
    """Background thread for daemon communication"""
    status_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.socket_path = Path.home() / ".onyx_monero" / "daemon.sock"
        self.running = True
        
    def send_command(self, cmd, **kwargs):
        """Send command to daemon"""
        request = {"cmd": cmd, **kwargs}
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(str(self.socket_path))
            sock.send(json.dumps(request).encode())
            response = sock.recv(4096)
            sock.close()
            return json.loads(response.decode())
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    def run(self):
        """Background status polling"""
        while self.running:
            try:
                response = self.send_command("ping")
                if response.get("ok"):
                    status = self.send_command("status")
                    if status.get("ok"):
                        self.status_updated.emit(status)
                    else:
                        self.error_occurred.emit("Status failed")
                else:
                    self.error_occurred.emit("Daemon not responding")
            except Exception as e:
                self.error_occurred.emit(f"Connection error: {e}")
            
            self.msleep(3000)  # Check every 3 seconds
    
    def stop(self):
        self.running = False
        self.quit()

class OnyxMiningGUI(QMainWindow):
    """Main mining control window"""
    
    def __init__(self):
        super().__init__()
        self.controller = MiningController()
        self.init_ui()
        self.setup_connections()
        self.controller.start()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Onyx Monero Mining Dashboard")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; color: #ffffff; }
            QPushButton { 
                background-color: #404040; 
                border: 2px solid #606060; 
                padding: 10px; 
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #505050; }
            QPushButton:pressed { background-color: #303030; }
            QLabel { color: #ffffff; font-size: 12px; }
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("ONYX MONERO MINING DASHBOARD")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #FF6600; margin: 10px;")
        layout.addWidget(title)
        
        # Status display
        self.status_label = QLabel("Status: Connecting...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; margin: 5px; padding: 10px; background-color: #404040; border-radius: 5px;")
        layout.addWidget(self.status_label)
        
        # Mining info
        self.mining_info = QLabel("Mode: Stopped | Threads: 0/72")
        self.mining_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mining_info.setStyleSheet("margin: 5px;")
        layout.addWidget(self.mining_info)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.background_btn = QPushButton("Start Background\n(50% CPU)")
        self.background_btn.clicked.connect(self.start_background)
        self.background_btn.setStyleSheet("QPushButton { background-color: #006400; }")
        button_layout.addWidget(self.background_btn)
        
        self.money_hunter_btn = QPushButton("Start Money Hunter\n(80% CPU)")
        self.money_hunter_btn.clicked.connect(self.start_money_hunter)
        self.money_hunter_btn.setStyleSheet("QPushButton { background-color: #FF4500; }")
        button_layout.addWidget(self.money_hunter_btn)
        
        self.stop_btn = QPushButton("STOP\nMining")
        self.stop_btn.clicked.connect(self.stop_mining)
        self.stop_btn.setStyleSheet("QPushButton { background-color: #8B0000; }")
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)
        
        # Config info
        config_frame = QFrame()
        config_frame.setStyleSheet("QFrame { background-color: #404040; border-radius: 5px; margin: 10px; padding: 10px; }")
        config_layout = QVBoxLayout(config_frame)
        
        config_title = QLabel("Mining Configuration")
        config_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        config_title.setStyleSheet("color: #FF6600;")
        config_layout.addWidget(config_title)
        
        try:
            config_path = Path.home() / ".onyx_monero" / "config.json"
            with open(config_path) as f:
                config = json.load(f)
            
            wallet = config.get("wallet_address", "Not configured")
            pool = config.get("pool_url", "Not configured")
            worker = config.get("worker_name", "Not configured")
            
            config_layout.addWidget(QLabel(f"Pool: {pool}"))
            config_layout.addWidget(QLabel(f"Worker: {worker}"))
            config_layout.addWidget(QLabel(f"Wallet: {wallet[:20]}...{wallet[-10:] if len(wallet) > 30 else wallet}"))
            
        except Exception as e:
            config_layout.addWidget(QLabel(f"Config error: {e}"))
        
        layout.addWidget(config_frame)
        
        # Footer
        footer = QLabel("Onyx Digital Intelligence Development")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #808080; font-size: 10px; margin: 10px;")
        layout.addWidget(footer)
        
    def setup_connections(self):
        """Setup signal connections"""
        self.controller.status_updated.connect(self.update_status)
        self.controller.error_occurred.connect(self.handle_error)
        
    def update_status(self, status):
        """Update GUI with status info"""
        mining_active = status.get("mining_active", False)
        current_mode = status.get("current_mode", "stopped")
        threads = status.get("mining_threads", 0)
        total_threads = status.get("total_threads", 72)
        
        if mining_active:
            self.status_label.setText(f"Status: Mining Active ({current_mode.title()})")
            self.status_label.setStyleSheet("font-size: 14px; margin: 5px; padding: 10px; background-color: #006400; border-radius: 5px; color: white;")
        else:
            self.status_label.setText("Status: Ready (Not Mining)")
            self.status_label.setStyleSheet("font-size: 14px; margin: 5px; padding: 10px; background-color: #404040; border-radius: 5px; color: white;")
        
        self.mining_info.setText(f"Mode: {current_mode.title()} | Threads: {threads}/{total_threads}")
        
    def handle_error(self, error):
        """Handle communication errors"""
        self.status_label.setText(f"Status: Error - {error}")
        self.status_label.setStyleSheet("font-size: 14px; margin: 5px; padding: 10px; background-color: #8B0000; border-radius: 5px; color: white;")
    
    def start_background(self):
        """Start background mining"""
        response = self.controller.send_command("start", mode="background")
        if response.get("ok"):
            QMessageBox.information(self, "Success", "Background mining started!")
        else:
            QMessageBox.critical(self, "Error", f"Failed to start: {response.get('error', 'Unknown error')}")
    
    def start_money_hunter(self):
        """Start money hunter mining"""
        response = self.controller.send_command("start", mode="money_hunter")
        if response.get("ok"):
            QMessageBox.information(self, "Success", "Money hunter mining started!")
        else:
            QMessageBox.critical(self, "Error", f"Failed to start: {response.get('error', 'Unknown error')}")
    
    def stop_mining(self):
        """Stop mining"""
        response = self.controller.send_command("stop")
        if response.get("ok"):
            QMessageBox.information(self, "Success", "Mining stopped!")
        else:
            QMessageBox.critical(self, "Error", f"Failed to stop: {response.get('error', 'Unknown error')}")
    
    def closeEvent(self, event):
        """Handle window close"""
        self.controller.stop()
        self.controller.wait()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    # Dark theme
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(43, 43, 43))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = OnyxMiningGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()