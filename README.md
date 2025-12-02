# Onyx Monero Mining Dashboard

**Professional XMrig Mining Control with Arctic Terminal Interface**

*Developed by Onyx Digital Intelligence Development*

## Overview

The Onyx Monero Mining Dashboard is a **professional-grade mining control system** featuring a background daemon for process management and a sleek GUI client with the Arctic Terminal theme. Built for **safety, reliability, and enterprise-grade control**.

### Key Features

- **🛡️ Safe Architecture**: Daemon can run on boot but **never auto-mines**
- **🎯 Professional Control**: Background (50% CPU) and Money Hunter (80% CPU) modes  
- **❄️ Arctic Terminal Theme**: Clean, professional interface with ice-blue accents
- **🔧 Process Management**: Clean xmrig lifecycle, no zombies, graceful shutdown
- **📡 Real-time Monitoring**: Live status, hashrate, logs, and system info
- **⚙️ Secure Configuration**: Encrypted config storage with validation
- **🔌 IPC Communication**: Unix socket API for daemon/GUI separation

## Architecture

```
┌─────────────────────────────────────────┐
│              GUI Client                  │  ← Arctic Terminal Interface
│         (onyx_miner_gui.py)             │
├─────────────────────────────────────────┤
│             IPC Layer                   │  ← Unix Socket Communication
│         (JSON Commands)                 │
├─────────────────────────────────────────┤
│           Background Daemon             │  ← Process Management
│        (onyx_miner_daemon.py)          │
├─────────────────────────────────────────┤
│            XMrig Control                │  ← Mining Process
│         (xmrig subprocess)              │
└─────────────────────────────────────────┘
```

### Daemon + Thin GUI Design

**Background Daemon**:
- Runs headless, owns all xmrig control
- Starts "stopped" - mining only on explicit command
- Unix socket IPC server
- Comprehensive logging and monitoring
- Systemd service integration

**Thin GUI Client**:
- Communicates only with daemon via IPC
- Real-time status updates
- Professional Arctic Terminal theme
- Connection-aware interface

## Quick Start

### On NixOS (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/oskodiak/onyx-monero-dashboard.git
cd onyx-monero-dashboard

# 2. Enter development environment  
nix-shell -p python3Packages.pyqt6 python3Packages.psutil xmrig

# 3. Install system-wide
sudo ./install.sh

# 4. Configure your wallet
sudo nano /home/onyx-miner/.onyx_monero/config.json

# 5. Start daemon
sudo systemctl start onyx-monero-daemon

# 6. Launch GUI
onyx_miner_gui.py
```

### On Other Linux Distributions

```bash
# Install dependencies first
# Ubuntu/Debian: apt install python3-pyqt6 python3-psutil xmrig
# Arch: pacman -S python-pyqt6 python-psutil xmrig
# Fedora: dnf install python3-PyQt6 python3-psutil xmrig

# Then follow steps 1, 3-6 above
```

## Configuration

### Wallet Setup

Edit `/home/onyx-miner/.onyx_monero/config.json`:

```json
{
  "wallet_address": "YOUR_MONERO_WALLET_ADDRESS",
  "pool_url": "pool.supportxmr.com:443",
  "worker_name": "onyx-miner", 
  "use_ssl": true,
  "profile_name": "My Mining Profile"
}
```

**Required**: Replace `YOUR_MONERO_WALLET_ADDRESS` with your actual Monero wallet address.

### Recommended Pools

| Pool | URL | Features |
|------|-----|----------|
| **SupportXMR** | `pool.supportxmr.com:443` | Low 0.1 XMR minimum, reliable, SSL |
| **MineXMR** | `pool.minexmr.com:443` | Large pool, stable payouts |
| **MoneroOcean** | `gulf.moneroocean.stream:10128` | Algorithm switching |

## Usage

### Mining Modes

**Background Mining**:
- Uses ~50% of CPU threads
- Low priority process  
- Designed to not interfere with work
- Perfect for daily computer use

**Money Hunter**:
- Uses ~80% of CPU threads
- High priority process
- Maximum performance mining
- Best for idle time/overnight

### GUI Controls

1. **Launch GUI**: `onyx_miner_gui.py` or find in applications menu
2. **Status Panel**: Shows mode, threads, hashrate, uptime, pool
3. **Control Buttons**: 
   - Green "Background Mining" - Start low-impact mining
   - Blue "Money Hunter" - Start high-performance mining  
   - Red "Stop Mining" - Stop all mining
4. **Log Panel**: Real-time daemon logs and status messages

### Daemon Management

```bash
# Start daemon
sudo systemctl start onyx-monero-daemon

# Enable on boot (daemon starts but doesn't mine)
sudo systemctl enable onyx-monero-daemon

# Check status  
sudo systemctl status onyx-monero-daemon

# View logs
journalctl -u onyx-monero-daemon -f

# Stop daemon
sudo systemctl stop onyx-monero-daemon
```

### Manual Operation

```bash
# Run daemon in foreground (for testing)
./onyx_miner_daemon.py --foreground

# Test GUI without systemd
./onyx_miner_gui.py
```

## IPC API

The daemon exposes a JSON-based API over Unix socket:

```json
// Get status
{"cmd": "status"}

// Start mining
{"cmd": "start", "mode": "background"}
{"cmd": "start", "mode": "money_hunter"}

// Stop mining  
{"cmd": "stop"}

// Configuration
{"cmd": "config_get"}
{"cmd": "config_set", "wallet": "...", "pool": "...", "worker": "..."}

// System info
{"cmd": "system_info"}
{"cmd": "ping"}
```

## File Structure

```
onyx-monero-dashboard/
├── daemon/                      # Background daemon package
│   ├── config.py               # Configuration management  
│   ├── state.py                # Mining state tracking
│   ├── controller.py           # XMrig process control
│   └── server.py               # IPC server
├── gui/                         # GUI client package
│   ├── theme.py                # Arctic Terminal theme
│   ├── ipc_client.py           # Daemon communication  
│   └── main_window.py          # Main interface
├── onyx_miner_daemon.py        # Daemon entry point
├── onyx_miner_gui.py           # GUI entry point
├── onyx-monero-daemon.service  # Systemd service
├── install.sh                  # Professional installer
└── README.md                   # This file
```

## Security & Safety

### Safe Boot Behavior
- ✅ Daemon can be enabled on boot
- ✅ Daemon starts in "stopped" state
- ❌ **Mining NEVER starts automatically**  
- ✅ Mining only begins with explicit GUI command

### Process Security
- Dedicated `onyx-miner` system user
- Secure file permissions (0600/0700)
- Clean process termination with SIGTERM/SIGKILL
- No zombie processes
- Comprehensive error handling

### Configuration Security  
- Wallet address validation
- Pool URL format checking
- Secure config file storage
- Input sanitization

## Troubleshooting

### Daemon Won't Start
```bash
# Check service status
sudo systemctl status onyx-monero-daemon

# View detailed logs  
journalctl -u onyx-monero-daemon -n 50

# Check dependencies
python3 -c "import PyQt6, psutil; print('Dependencies OK')"
```

### GUI Can't Connect
```bash
# Verify daemon is running
sudo systemctl status onyx-monero-daemon

# Check socket exists
ls -la /home/onyx-miner/.onyx_monero/daemon.sock

# Test daemon connectivity
echo '{"cmd":"ping"}' | nc -U /home/onyx-miner/.onyx_monero/daemon.sock
```

### XMrig Not Found  
```bash
# Install XMrig
# NixOS: nix-shell -p xmrig  
# Ubuntu: apt install xmrig
# Arch: pacman -S xmrig

# Verify installation
which xmrig
xmrig --version
```

### Configuration Issues
```bash
# Check config file
sudo cat /home/onyx-miner/.onyx_monero/config.json

# Validate wallet address format (starts with 4)
# Validate pool URL includes port

# Reset to defaults
sudo rm /home/onyx-miner/.onyx_monero/config.json
sudo systemctl restart onyx-monero-daemon
```

### Permission Problems
```bash  
# Fix ownership
sudo chown -R onyx-miner:onyx-miner /home/onyx-miner/.onyx_monero

# Fix permissions
sudo chmod 700 /home/onyx-miner/.onyx_monero
sudo chmod 600 /home/onyx-miner/.onyx_monero/*
```

## Performance

### Resource Usage

| Component | CPU Impact | Memory | 
|-----------|------------|--------|
| **Daemon** | <1% | ~20MB |
| **GUI** | <2% | ~30MB |  
| **Background Mining** | 50% threads | Variable |
| **Money Hunter** | 80% threads | Variable |

### Thread Allocation

CPU threads are automatically detected and allocated:

- **Background**: `max(1, cpu_count * 0.5)` threads, priority 1
- **Money Hunter**: `max(1, cpu_count * 0.8)` threads, priority 3

Example on 72-thread system:
- Background: 36 threads
- Money Hunter: 58 threads

## Development

### Requirements
- Python 3.8+
- PyQt6
- psutil  
- XMrig (runtime)

### Testing
```bash
# Run daemon in debug mode
./onyx_miner_daemon.py --foreground

# Run GUI in development mode  
./onyx_miner_gui.py

# Test IPC manually
echo '{"cmd":"status"}' | nc -U ~/.onyx_monero/daemon.sock
```

### Code Structure
- **Clean separation**: Daemon, GUI, IPC, themes
- **Error handling**: Comprehensive exception management  
- **Logging**: Structured logging with rotation
- **Thread safety**: All state operations protected

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)  
5. Open Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

**Issues**: https://github.com/oskodiak/onyx-monero-dashboard/issues  
**Documentation**: This README  
**Contact**: Onyx Digital Intelligence Development

---

**Onyx Digital Intelligence Development**  
*Professional mining control solutions*