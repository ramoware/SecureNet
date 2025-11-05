import logging
import time
from datetime import datetime
from scapy.all import sniff, IP, TCP, UDP, ICMP

class NetworkMonitor:
    """Automated network monitoring for threat detection."""
    
    def __init__(self, alert_threshold=100):
        self.alert_threshold = alert_threshold
        self.packet_count = 0
        self.suspicious_activities = []
        self.logger = logging.getLogger(__name__)
        
    def packet_handler(self, packet):
        """Analyze individual packets for suspicious patterns."""
        self.packet_count += 1
        
        # Detect potential port scanning
        if packet.haslayer(TCP):
            tcp_layer = packet[TCP]
            if tcp_layer.flags == 'S':  SYN packets for port scanning detection
                self.logger.debug(f"TCP SYN packet detected from {packet[IP].src}")
                
        # Alert on high traffic volume (potential DoS)
        if self.packet_count > self.alert_threshold:
            alert_msg = f"High traffic volume detected: {self.packet_count} packets"
            self.trigger_alert(alert_msg)
            
        # Log unusual ICMP traffic
        if packet.haslayer(ICMP):
            self.logger.info(f"ICMP packet from {packet[IP].src}")
    
    def trigger_alert(self, message):
        """Trigger security alerts for suspicious activities."""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'packet_count': self.packet_count
        }
        self.suspicious_activities.append(alert)
        self.logger.warning(f"🚨 SECURITY ALERT: {message}")
        
    def start_monitoring(self, interface=None):
        """Start continuous network monitoring."""
        self.logger.info(f"Starting network monitoring on interface {interface or 'default'}")
        try:
            sniff(prn=self.packet_handler, iface=interface, store=False)
        except Exception as e:
            self.logger.error(f"Monitoring error: {str(e)}")
            raise
    
    def get_security_report(self):
        """Generate security summary report."""
        return {
            'total_packets_analyzed': self.packet_count,
            'alerts_triggered': len(self.suspicious_activities),
            'recent_alerts': self.suspicious_activities[-5:]  Last 5 alerts
        }
