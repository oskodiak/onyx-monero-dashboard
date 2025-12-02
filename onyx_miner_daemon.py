#!/usr/bin/env python3
"""
Onyx Monero Mining Daemon
Background service for professional xmrig control
Onyx Digital Intelligence Development
"""

import sys
import argparse
from pathlib import Path

# Add daemon package to path
daemon_path = Path(__file__).parent / "daemon"
sys.path.insert(0, str(daemon_path))

from daemon import DaemonServer, setup_logging
import logging

logger = logging.getLogger(__name__)

def main():
    """Main daemon entry point"""
    parser = argparse.ArgumentParser(
        description="Onyx Monero Mining Daemon - Professional XMrig Control"
    )
    parser.add_argument(
        "--foreground", "-f",
        action="store_true",
        help="Run in foreground (don't daemonize)"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Onyx Monero Daemon 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    logger.info("=" * 60)
    logger.info("Onyx Monero Mining Daemon - Starting")
    logger.info("Professional XMrig Control Service")
    logger.info("Onyx Digital Intelligence Development")
    logger.info("=" * 60)
    
    # Create and start daemon
    daemon = DaemonServer()
    
    if not daemon.start():
        logger.error("Failed to start daemon")
        sys.exit(1)
    
    try:
        # Run daemon
        daemon.run()
    except Exception as e:
        logger.error(f"Daemon error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()