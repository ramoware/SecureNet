#!/usr/bin/env python3
"""
SecureNet - Main Entry Point
Network Security Automation | Security Research Project | September 2025
"""

import logging
from network.monitor import NetworkMonitor
from network.scanner import NetworkScanner
from auth.rbac import RBAC
from config.settings import LOG_LEVEL, SCAN_SUBNET

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('securenet.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point."""
    try:
        logger.info("🚀 Starting SecureNet Security Automation System")
        
        # Initialize RBAC system
        rbac = RBAC()
        logger.info("✅ RBAC System initialized")
        
        # Demonstrate network scanning
        scanner = NetworkScanner()
        scan_results = scanner.scan_network(SCAN_SUBNET)
        
        print("🔍 Network Scan Results:")
        for device in scan_results:
            print(f"   - {device}")
            
        # Start continuous monitoring
        monitor = NetworkMonitor()
        logger.info("🛡️ Starting network monitoring...")
        monitor.start_monitoring()
        
    except KeyboardInterrupt:
        logger.info("🛑 SecureNet stopped by user")
    except Exception as e:
        logger.error(f"❌ Error in main application: {str(e)}")
        raise

if __name__ == "__main__":
    main()
