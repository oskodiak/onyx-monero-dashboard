# Onyx Monero Mining Dashboard

**Professional XMrig mining controller with intelligent resource management for Linux/NixOS systems.**

*Developed by Onyx Digital Intelligence Development*

## Overview

The Onyx Monero Mining Dashboard provides enterprise-grade control over XMrig mining operations with a focus on system stability, user experience, and professional deployment. Features intelligent CPU load balancing, background daemon architecture, and a modern PyQt6 interface.

## Key Features

### 🎛️ **Intelligent Mining Modes**
- **Background Mode**: 50% CPU utilization with low process priority - designed for mining during work hours without impacting productivity
- **Money Hunter Mode**: 80% CPU utilization with optimized priority - maximum earning potential during idle periods
- **Clean Stop**: Ensures proper XMrig process termination and system cleanup

### 🏗️ **Professional Architecture**
- **Daemon Service**: Background service with systemd integration and automatic startup
- **IPC Communication**: Unix socket-based communication between GUI and daemon
- **Thread Safety**: Robust state management with proper locking mechanisms
- **Error Handling**: Comprehensive error handling and recovery mechanisms

### 🖥️ **Modern Interface**
- **PyQt6 GUI**: Clean, responsive interface with real-time status updates
- **System Tray**: Runs in background with system tray integration
- **Professional Styling**: Dark theme optimized for extended use
- **Configuration Display**: Live wallet and pool configuration visibility

### 🔧 **Enterprise Deployment**
- **Single Command Install**: Automated installation with dependency verification
- **NixOS Integration**: Native support for NixOS declarative package management  
- **User Service**: Runs as user service (not system-wide) for security
- **Desktop Integration**: Full desktop environment integration with application menu entries

## Quick Installation

### Prerequisites
- **NixOS**: Add to your `configuration.nix`:
```nix
(python3.withPackages (ps: with ps; [
  pyqt6 psutil tkinter requests bcrypt pysocks
  # ... other packages as needed
]))
xmrig
```

### Installation
```bash
git clone https://github.com/oskodiak/onyx-monero-dashboard.git
cd onyx-monero-dashboard
chmod +x install.sh
./install.sh
```

## Usage

### GUI Control
Launch from applications menu: **"Onyx Monero Mining Dashboard"**

Or from terminal:
```bash
onyx-monero-dashboard
```

### Daemon Management
```bash
# Check status
systemctl --user status onyx-monero-daemon

# Start/stop daemon
systemctl --user start onyx-monero-daemon
systemctl --user stop onyx-monero-daemon

# View logs
journalctl --user -u onyx-monero-daemon -f
```

### Configuration
Edit mining configuration:
```bash
nano ~/.onyx_monero/config.json
```

## Architecture

### System Components

```
┌─────────────────┐    Unix Socket    ┌─────────────────┐
│   PyQt6 GUI     │ ←──────────────→  │   Daemon        │
│                 │                   │   Service       │
│ • Controls      │                   │                 │
│ • Status        │                   │ • XMrig Control │
│ • Configuration │                   │ • State Mgmt    │
└─────────────────┘                   │ • IPC Server    │
                                      └─────────────────┘
                                              │
                                              ▼
                                      ┌─────────────────┐
                                      │     XMrig       │
                                      │   Process       │
                                      └─────────────────┘
```

### File Structure
```
onyx-monero-dashboard/
├── daemon/                 # Daemon package
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── controller.py      # XMrig process control
│   ├── server.py          # IPC server
│   └── state.py           # State management
├── gui/                   # GUI package  
│   ├── __init__.py
│   ├── ipc_client.py      # IPC client
│   ├── main_window.py     # Main window
│   └── theme.py           # UI theming
├── onyx_miner_daemon.py   # Daemon entry point
├── onyx_gui_clean.py      # Clean GUI implementation
├── install.sh             # Installation script
└── README.md              # This file
```

### Configuration Files
- `~/.onyx_monero/config.json` - Mining configuration
- `~/.onyx_monero/daemon.sock` - IPC socket
- `~/.onyx_monero/daemon.log` - Daemon logs
- `~/.onyx_monero/xmrig.log` - Mining logs

## Mining Configuration

Default configuration supports SupportXMR pool:
```json
{
    "wallet_address": "YOUR_WALLET_ADDRESS",
    "pool_url": "pool.supportxmr.com:443",
    "worker_name": "onyx-miner",
    "use_ssl": true,
    "profile_name": "Default Profile"
}
```

## Technical Specifications

### CPU Thread Management
- **Background Mode**: 50% of available threads with nice priority +10
- **Money Hunter Mode**: 80% of available threads with nice priority 0
- **Automatic Detection**: System CPU core count automatically detected
- **Resource Limits**: Daemon memory limited to 512MB via systemd

### Security Features
- **User Service**: Runs under user context, not system-wide
- **Process Isolation**: XMrig runs in separate process with monitoring
- **Socket Permissions**: Unix socket with user-only access (700)
- **No Privileged Access**: No sudo or root privileges required

### Performance Monitoring
- **Real-time Status**: Live mining status and thread utilization
- **System Information**: CPU, memory, and thermal monitoring
- **Hashrate Tracking**: Performance metrics and uptime statistics
- **Error Tracking**: Comprehensive error logging and reporting

## Development

### Dependencies
- **Python 3.12+** with packages:
  - PyQt6 (GUI framework)
  - psutil (system monitoring)
  - Standard library (json, socket, threading, etc.)
- **XMrig** (mining software)
- **systemd** (service management)

### Testing
```bash
# Test daemon communication
python3 -c "import socket, json; sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); sock.connect('/home/$USER/.onyx_monero/daemon.sock'); sock.send(json.dumps({'cmd': 'ping'}).encode()); print(sock.recv(1024).decode())"

# Check service status
systemctl --user status onyx-monero-daemon
```

## Deployment Notes

### For Job Interviews / Professional Use
- **Clean Architecture**: Demonstrates understanding of daemon services, IPC, and GUI frameworks
- **Production Ready**: Includes proper error handling, logging, and service management
- **NixOS Integration**: Shows modern Linux distribution knowledge
- **Security Conscious**: User-space deployment without privilege escalation
- **Professional Presentation**: Clean code, documentation, and deployment automation

### Scaling Considerations
- **Multi-user**: Can be deployed per-user on shared systems
- **Configuration Management**: JSON-based configuration for easy automation
- **Monitoring Integration**: Structured logging compatible with log aggregation systems
- **Resource Limits**: Built-in memory and CPU limits for production deployment

## License

Proprietary software developed by Onyx Digital Intelligence Development.

## Support

For enterprise deployment or customization inquiries, contact Onyx Digital Intelligence Development.

---

*Professional Monero mining control for modern Linux environments.*