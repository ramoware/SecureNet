import socket
import subprocess
import logging
from concurrent.futures import ThreadPoolExecutor

class NetworkScanner:
    """Network scanning utilities for asset discovery."""
    
    def __init__(self, max_workers=50):
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
    
    def check_port(self, args):
        """Check if a specific port is open on a host."""
        host, port = args
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                if result == 0:
                    self.logger.info(f"Port {port} open on {host}")
                    return (host, port, "Open")
        except Exception as e:
            self.logger.debug(f"Error scanning {host}:{port} - {str(e)}")
        return (host, port, "Closed")
    
    def scan_network(self, subnet, ports=[22, 80, 443, 3389, 5432]):
        """Perform network discovery and port scanning."""
        self.logger.info(f"Scanning subnet {subnet} on ports {ports}")
        
        discovered_devices = []
        
        # Generate IPs to scan (simplified - in production, use proper subnet calculation)
        base_ip = ".".join(subnet.split(".")[:-1])
        ip_range = [f"{base_ip}.{i}" for i in range(1, 50)]  # Scan first 50 IPs
        
        # Multi-threaded port scanning
        scan_tasks = []
        for ip in ip_range:
            for port in ports:
                scan_tasks.append((ip, port))
        
        open_ports = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = executor.map(self.check_port, scan_tasks)
            for result in results:
                if result[2] == "Open":
                    open_ports.append(result)
        
        # Format results
        for ip in ip_range:
            device_ports = [port for (host, port, status) in open_ports if host == ip]
            if device_ports:
                device_info = {
                    'ip_address': ip,
                    'open_ports': device_ports,
                    'status': 'Active'
                }
                discovered_devices.append(device_info)
                self.logger.info(f"Discovered active device: {ip} with ports {device_ports}")
        
        return discovered_devices
    
    def ping_sweep(self, subnet):
        """Perform ping sweep to identify active devices."""
        active_hosts = []
        base_ip = ".".join(subnet.split(".")[:-1])
        
        self.logger.info(f"Starting ping sweep for {subnet}")
        
        for i in range(1, 255):
            ip = f"{base_ip}.{i}"
            try:
                # Platform-independent ping command
                param = "-n" if subprocess.os.name == "nt" else "-c"
                command = ["ping", param, "1", "-W", "1", ip]
                response = subprocess.run(command, capture_output=True, text=True, timeout=2)
                
                if response.returncode == 0:
                    active_hosts.append(ip)
                    self.logger.info(f"Active host found: {ip}")
                    
            except subprocess.TimeoutExpired:
                continue
            except Exception as e:
                self.logger.debug(f"Ping error for {ip}: {str(e)}")
        
        return active_hosts
