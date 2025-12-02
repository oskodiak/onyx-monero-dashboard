#!/usr/bin/env python3
"""
Onyx Monero Mining Dashboard GUI
Professional interface for xmrig control
Onyx Digital Intelligence Development
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

# Add GUI package to path
gui_path = Path(__file__).parent / "gui"
sys.path.insert(0, str(gui_path))

from gui import OnyxTheme, OnyxMinerMainWindow

def setup_logging():
    """Setup GUI logging"""
    log_dir = Path.home() / ".onyx_monero"
    log_dir.mkdir(exist_ok=True, mode=0o700)
    
    log_file = log_dir / "gui.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def check_requirements():
    """Check if system requirements are met"""
    try:
        # Check PyQt6
        from PyQt6.QtWidgets import QApplication
        
        # Check psutil (used by daemon)
        import psutil
        
        return True, ""
        
    except ImportError as e:
        return False, f"Missing dependency: {e}"

def main():
    """Main GUI entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check requirements
    requirements_ok, error_msg = check_requirements()
    if not requirements_ok:
        print(f"Error: {error_msg}")
        print("\nOn NixOS, install with:")
        print("nix-shell -p python3Packages.pyqt6 python3Packages.psutil")
        sys.exit(1)
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Onyx Monero Mining Dashboard")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Onyx Digital Intelligence Development")
    
    # Apply Onyx Arctic Terminal theme
    OnyxTheme.apply_to_app(app)
    
    logger.info("=" * 60)
    logger.info("Onyx Monero Mining Dashboard - Starting GUI")
    logger.info("Professional XMrig Control Interface")
    logger.info("Onyx Digital Intelligence Development")
    logger.info("=" * 60)
    
    try:
        # Create and show main window
        window = OnyxMinerMainWindow()
        window.show()
        
        # Check daemon connectivity on startup
        from gui.ipc_client import IPCClient
        test_client = IPCClient()
        test_client.stop_polling()  # Don't need polling for test
        
        if not test_client.ping_daemon():
            # Show helpful message if daemon is not running
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Daemon Not Running")
            msg_box.setText(
                "The Onyx Monero daemon is not running.\n\n"
                "To start the daemon:\n"
                "• systemctl start onyx-monero-daemon\n"
                "• Or run: ./onyx_miner_daemon.py\n\n"
                "The GUI will automatically connect when the daemon starts."
            )
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStyleSheet(OnyxTheme.get_dialog_style())
            msg_box.exec()
        
        # Run application
        logger.info("GUI started successfully")
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"GUI error: {e}")
        
        # Show error dialog if possible
        try:
            error_box = QMessageBox()
            error_box.setWindowTitle("Application Error")
            error_box.setText(f"An error occurred:\n\n{e}")
            error_box.setIcon(QMessageBox.Icon.Critical)
            error_box.setStyleSheet(OnyxTheme.get_dialog_style())
            error_box.exec()
        except:
            pass
        
        sys.exit(1)

if __name__ == "__main__":
    main()