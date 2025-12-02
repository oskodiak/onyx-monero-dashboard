#!/usr/bin/env bash
# Onyx Monero Mining Dashboard - Professional Installation
# Onyx Digital Intelligence Development

set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_SYSTEMD_DIR="$HOME/.config/systemd/user"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons"
BIN_DIR="$HOME/.local/bin"

echo "============================================================"
echo "    ONYX MONERO MINING DASHBOARD - INSTALLER"
echo "    Professional XMrig Control Suite"
echo "    Onyx Digital Intelligence Development"
echo "============================================================"
echo ""

# Check dependencies
echo "Checking system dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required"
    exit 1
fi

if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "ERROR: PyQt6 is required"
    echo "On NixOS: Add python3.withPackages to your configuration.nix"
    exit 1
fi

if ! python3 -c "import psutil" 2>/dev/null; then
    echo "ERROR: psutil is required"
    exit 1
fi

if ! command -v xmrig &> /dev/null; then
    echo "WARNING: XMrig not found. Install before mining."
    echo "On NixOS: nix-shell -p xmrig"
fi

echo "Dependencies OK"
echo ""

# Create directories
echo "Creating application directories..."
mkdir -p "$USER_SYSTEMD_DIR" "$DESKTOP_DIR" "$ICON_DIR" "$BIN_DIR"

# Make scripts executable
chmod +x "$APP_DIR/onyx_miner_daemon.py"
chmod +x "$APP_DIR/onyx_miner_gui.py"

# Install daemon service
echo "Installing daemon service..."
cp "$APP_DIR/onyx-monero-daemon.service" "$USER_SYSTEMD_DIR/"
systemctl --user daemon-reload
systemctl --user enable onyx-monero-daemon

# Create GUI launcher
echo "Creating GUI launcher..."
cat > "$BIN_DIR/onyx-monero-dashboard" << EOF
#!/usr/bin/env bash
# Onyx Monero Mining Dashboard
cd "$APP_DIR"
exec python3 onyx_miner_gui.py
EOF
chmod +x "$BIN_DIR/onyx-monero-dashboard"

# Create professional icon
echo "Installing application icon..."
cat > "$ICON_DIR/onyx-monero.svg" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a1a;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#333333;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#FF6600;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#FF4500;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="64" height="64" fill="url(#grad1)" rx="12"/>
  <text x="32" y="20" font-family="Arial" font-size="10" fill="url(#grad2)" text-anchor="middle" font-weight="bold">ONYX</text>
  <text x="32" y="40" font-family="Arial" font-size="14" fill="white" text-anchor="middle" font-weight="bold">XMR</text>
  <circle cx="32" cy="50" r="2" fill="url(#grad2)" opacity="0.9"/>
  <rect x="20" y="54" width="24" height="2" fill="url(#grad2)" opacity="0.7" rx="1"/>
</svg>
EOF

# Create desktop entry
echo "Creating desktop application..."
cat > "$DESKTOP_DIR/onyx-monero-dashboard.desktop" << EOF
[Desktop Entry]
Name=Onyx Monero Mining Dashboard
Comment=Professional Monero mining control interface
Exec=$BIN_DIR/onyx-monero-dashboard
Icon=onyx-monero
Terminal=false
Type=Application
Categories=System;
Keywords=mining;monero;xmr;cryptocurrency;onyx;dashboard;
StartupNotify=true
StartupWMClass=onyx-monero-dashboard
EOF
chmod +x "$DESKTOP_DIR/onyx-monero-dashboard.desktop"

# Start daemon
echo "Starting daemon service..."
systemctl --user start onyx-monero-daemon

# Verify installation
echo ""
echo "Verifying installation..."
sleep 2

if systemctl --user is-active --quiet onyx-monero-daemon; then
    echo "✓ Daemon service running"
else
    echo "✗ Daemon service failed to start"
    echo "Check logs: journalctl --user -u onyx-monero-daemon"
fi

if [ -f "$BIN_DIR/onyx-monero-dashboard" ]; then
    echo "✓ GUI launcher installed"
else
    echo "✗ GUI launcher installation failed"
fi

if [ -f "$DESKTOP_DIR/onyx-monero-dashboard.desktop" ]; then
    echo "✓ Desktop application created"
else
    echo "✗ Desktop application creation failed"
fi

echo ""
echo "============================================================"
echo "                 INSTALLATION COMPLETE"
echo "============================================================"
echo ""
echo "USAGE:"
echo ""
echo "🎯 Launch GUI:"
echo "   • Find 'Onyx Monero Mining Dashboard' in applications menu"
echo "   • Or run: onyx-monero-dashboard"
echo ""
echo "🔧 Daemon Control:"
echo "   systemctl --user status onyx-monero-daemon"
echo "   systemctl --user stop onyx-monero-daemon"
echo "   systemctl --user restart onyx-monero-daemon"
echo ""
echo "📋 Logs:"
echo "   journalctl --user -u onyx-monero-daemon -f"
echo "   tail -f ~/.onyx_monero/xmrig.log"
echo ""
echo "⚙️  Configuration:"
echo "   Edit ~/.onyx_monero/config.json for wallet/pool settings"
echo ""
echo "MINING MODES:"
echo "• Background: 50% CPU, low priority (work-friendly)"
echo "• Money Hunter: 80% CPU, high priority (idle/night)"
echo ""
echo "The daemon auto-starts on login but never auto-mines."
echo "Mining only starts when you click buttons in the GUI."
echo ""
echo "✨ Ready for professional Monero mining control!"
echo ""