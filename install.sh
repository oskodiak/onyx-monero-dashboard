#!/usr/bin/env bash
# Onyx Monero Mining Dashboard - Professional Installation
# Installs daemon, GUI, and systemd service
# Onyx Digital Intelligence Development

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_PREFIX="/usr/local"
SERVICE_DIR="/etc/systemd/system"
DESKTOP_DIR="/usr/share/applications"
USER_NAME="onyx-miner"
GROUP_NAME="onyx-miner"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        log_info "Run as your normal user - it will use sudo when needed"
        exit 1
    fi
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check for required commands
    local deps=("python3" "systemctl" "useradd" "groupadd")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "Required command '$dep' not found"
            exit 1
        fi
    done
    
    # Check Python packages
    log_info "Checking Python dependencies..."
    if ! python3 -c "import PyQt6" 2>/dev/null; then
        log_error "PyQt6 not available"
        log_info "On NixOS: nix-shell -p python3Packages.pyqt6 python3Packages.psutil"
        log_info "On Ubuntu/Debian: apt install python3-pyqt6 python3-psutil"
        exit 1
    fi
    
    if ! python3 -c "import psutil" 2>/dev/null; then
        log_error "psutil not available"
        log_info "On NixOS: nix-shell -p python3Packages.psutil"
        log_info "On Ubuntu/Debian: apt install python3-psutil"
        exit 1
    fi
    
    # Check for xmrig
    if ! command -v xmrig &> /dev/null; then
        log_warning "XMrig not found in PATH"
        log_info "Install XMrig before running the daemon"
        log_info "On NixOS: nix-shell -p xmrig"
        log_info "On Ubuntu/Debian: apt install xmrig"
    fi
    
    log_success "Dependencies check passed"
}

create_user() {
    log_info "Creating system user and group..."
    
    # Create group
    if ! getent group "$GROUP_NAME" >/dev/null 2>&1; then
        sudo groupadd --system "$GROUP_NAME"
        log_success "Created group: $GROUP_NAME"
    else
        log_info "Group already exists: $GROUP_NAME"
    fi
    
    # Create user
    if ! id "$USER_NAME" >/dev/null 2>&1; then
        sudo useradd --system --gid "$GROUP_NAME" --create-home --home-dir "/home/$USER_NAME" \
                     --shell /usr/sbin/nologin --comment "Onyx Monero Mining Daemon" "$USER_NAME"
        log_success "Created user: $USER_NAME"
    else
        log_info "User already exists: $USER_NAME"
    fi
    
    # Set up home directory permissions
    sudo mkdir -p "/home/$USER_NAME/.onyx_monero"
    sudo chown -R "$USER_NAME:$GROUP_NAME" "/home/$USER_NAME"
    sudo chmod 700 "/home/$USER_NAME/.onyx_monero"
}

install_daemon() {
    log_info "Installing daemon..."
    
    # Copy daemon files
    sudo mkdir -p "$INSTALL_PREFIX/lib/onyx-monero"
    sudo cp -r "$SCRIPT_DIR/daemon" "$INSTALL_PREFIX/lib/onyx-monero/"
    sudo cp "$SCRIPT_DIR/onyx_miner_daemon.py" "$INSTALL_PREFIX/bin/"
    sudo chmod +x "$INSTALL_PREFIX/bin/onyx_miner_daemon.py"
    
    # Fix daemon script path
    sudo sed -i "s|daemon_path = Path(__file__).parent / \"daemon\"|daemon_path = Path(\"$INSTALL_PREFIX/lib/onyx-monero\")|" \
        "$INSTALL_PREFIX/bin/onyx_miner_daemon.py"
    
    log_success "Daemon installed to $INSTALL_PREFIX/bin/onyx_miner_daemon.py"
}

install_gui() {
    log_info "Installing GUI..."
    
    # Copy GUI files
    sudo cp -r "$SCRIPT_DIR/gui" "$INSTALL_PREFIX/lib/onyx-monero/"
    sudo cp "$SCRIPT_DIR/onyx_miner_gui.py" "$INSTALL_PREFIX/bin/"
    sudo chmod +x "$INSTALL_PREFIX/bin/onyx_miner_gui.py"
    
    # Fix GUI script path
    sudo sed -i "s|gui_path = Path(__file__).parent / \"gui\"|gui_path = Path(\"$INSTALL_PREFIX/lib/onyx-monero\")|" \
        "$INSTALL_PREFIX/bin/onyx_miner_gui.py"
    
    # Create desktop entry
    sudo tee "$DESKTOP_DIR/onyx-monero-dashboard.desktop" > /dev/null << EOF
[Desktop Entry]
Name=Onyx Monero Mining Dashboard
Comment=Professional Monero mining control interface
Exec=$INSTALL_PREFIX/bin/onyx_miner_gui.py
Icon=onyx-monero-dashboard
Terminal=false
Type=Application
Categories=System;Network;
Keywords=mining;monero;xmr;cryptocurrency;onyx;
StartupNotify=true
EOF
    
    sudo chmod +x "$DESKTOP_DIR/onyx-monero-dashboard.desktop"
    
    log_success "GUI installed to $INSTALL_PREFIX/bin/onyx_miner_gui.py"
}

install_systemd_service() {
    log_info "Installing systemd service..."
    
    # Copy and customize service file
    sudo cp "$SCRIPT_DIR/onyx-monero-daemon.service" "$SERVICE_DIR/"
    sudo sed -i "s|ExecStart=/usr/local/bin/onyx_miner_daemon.py|ExecStart=$INSTALL_PREFIX/bin/onyx_miner_daemon.py|" \
        "$SERVICE_DIR/onyx-monero-daemon.service"
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    log_success "Systemd service installed"
    log_info "Service can be managed with:"
    log_info "  sudo systemctl enable onyx-monero-daemon    # Enable on boot"
    log_info "  sudo systemctl start onyx-monero-daemon     # Start now"
    log_info "  sudo systemctl status onyx-monero-daemon    # Check status"
}

create_default_config() {
    log_info "Creating default configuration..."
    
    # Create config as daemon user
    sudo -u "$USER_NAME" python3 -c "
import sys
sys.path.insert(0, '$INSTALL_PREFIX/lib/onyx-monero')
from daemon.config import ConfigManager
config_manager = ConfigManager()
config_manager.create_default_config_if_missing()
print('Default configuration created')
"
    
    log_success "Default configuration created in /home/$USER_NAME/.onyx_monero/"
}

show_usage_info() {
    log_success "Installation completed successfully!"
    echo
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "                        Onyx Monero Mining Dashboard - Ready"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    log_info "🚀 GETTING STARTED:"
    echo
    log_info "1. Configure your wallet address:"
    log_info "   sudo nano /home/$USER_NAME/.onyx_monero/config.json"
    echo
    log_info "2. Start the daemon:"
    log_info "   sudo systemctl start onyx-monero-daemon"
    echo
    log_info "3. Launch the GUI:"
    log_info "   onyx_miner_gui.py"
    log_info "   (Or find 'Onyx Monero Mining Dashboard' in your applications menu)"
    echo
    log_info "🔧 DAEMON MANAGEMENT:"
    log_info "   sudo systemctl enable onyx-monero-daemon    # Enable on boot"
    log_info "   sudo systemctl start onyx-monero-daemon     # Start daemon"
    log_info "   sudo systemctl stop onyx-monero-daemon      # Stop daemon"
    log_info "   sudo systemctl status onyx-monero-daemon    # Check status"
    log_info "   journalctl -u onyx-monero-daemon -f         # View logs"
    echo
    log_info "📋 CONFIGURATION:"
    log_info "   Config file: /home/$USER_NAME/.onyx_monero/config.json"
    log_info "   Log files:   /home/$USER_NAME/.onyx_monero/daemon.log"
    log_info "   Socket:      /home/$USER_NAME/.onyx_monero/daemon.sock"
    echo
    log_warning "⚠️  IMPORTANT NOTES:"
    log_warning "   • The daemon can run on boot but NEVER auto-starts mining"
    log_warning "   • Mining only starts when you explicitly click buttons in GUI"
    log_warning "   • Configure your wallet address before starting mining"
    log_warning "   • Ensure XMrig is installed: nix-shell -p xmrig"
    echo
    log_success "Professional Monero mining control is now ready!"
    echo
}

main() {
    echo
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "                     Onyx Monero Mining Dashboard Installer"
    log_info "                        Professional XMrig Control Suite"
    log_info "                       Onyx Digital Intelligence Development"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo
    
    check_root
    check_dependencies
    create_user
    install_daemon
    install_gui
    install_systemd_service
    create_default_config
    show_usage_info
}

# Run main function
main "$@"