"""
Configuration settings for SecureNet application.
"""

# Logging Configuration
LOG_LEVEL = "INFO"

# Network Configuration
SCAN_SUBNET = "192.168.1.0/24"
MONITORING_INTERFACE = None  # None for default interface

# Security Configuration
ALERT_THRESHOLD = 1000  # packets per minute
SCAN_PORTS = [21, 22, 23, 80, 443, 3389, 5432]

# RBAC Configuration
DEFAULT_ROLE = "viewer"
ADMIN_USERS = ["admin", "security-admin"]
