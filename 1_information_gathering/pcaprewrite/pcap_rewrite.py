#!/usr/bin/env python3
"""
PcapRewrite: A private tool for editing PCAP files.
Modifies Ethernet MAC addresses, IPv4/IPv6 addresses, and TCP/UDP ports.
For authorized, personal use only. Do not share or distribute.
"""

import argparse
import sys
from scapy.all import rdpcap, wrpcap, Ether, IP, IPv6, TCP, UDP


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="PcapRewrite: Modify packet headers in PCAP files."
    )
    parser.add_argument(
        "--infile", required=True, help="Input PCAP file path (e.g., input.pcap)"
    )
    parser.add_argument(
        "--outfile", required=True, help="Output PCAP file path (e.g., output.pcap)"
    )
    parser.add_argument(
        "--src-mac", help="New source MAC address (e.g., 00:01:02:03:04:05)"
    )
    parser.add_argument(
        "--dst-mac", help="New destination MAC address (e.g., 06:07:08:09:10:11)"
    )
    parser.add_argument(
        "--src-ip", help="New source IP address (IPv4 or IPv6, e.g., 192.168.1.100)"
    )
    parser.add_argument(
        "--dst-ip", help="New destination IP address (e.g., 192.168.1.200)"
    )
    parser.add_argument(
        "--src-port", type=int, help="New source port for TCP/UDP (1-65535)"
    )
    parser.add_argument(
        "--dst-port", type=int, help="New destination port for TCP/UDP (1-65535)"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output for debugging"
    )
    return parser.parse_args()


def validate_arguments(args):
    """Validate command-line arguments."""
    if args.src_port and (args.src_port < 1 or args.src_port > 65535):
        print("Error: Source port must be between 1 and 65535")
        sys.exit(1)
    if args.dst_port and (args.dst_port < 1 or args.dst_port > 65535):
        print("Error: Destination port must be between 1 and 65535")
        sys.exit(1)
    # Basic MAC address format check (not exhaustive)
    for mac in [args.src_mac, args.dst_mac]:
        if mac and not all(c in "0123456789abcdefABCDEF:" for c in mac):
            print(f"Error: Invalid MAC address format: {mac}")
            sys.exit(1)


def modify_packet(packet, args):
    """Modify a single packet based on provided arguments."""
    # Create a copy to avoid altering the original
    new_packet = packet.copy()

    # Layer 2: Ethernet MAC addresses
    if Ether in new_packet:
        if args.src_mac:
            new_packet[Ether].src = args.src_mac
        if args.dst_mac:
            new_packet[Ether].dst = args.dst_mac

    # Layer 3: IPv4 or IPv6 addresses
    if IP in new_packet and (args.src_ip or args.dst_ip):
        if args.src_ip:
            new_packet[IP].src = args.src_ip
        if args.dst_ip:
            new_packet[IP].dst = args.dst_ip
        # Remove checksum to trigger recalculation
        del new_packet[IP].chksum

    elif IPv6 in new_packet and (args.src_ip or args.dst_ip):
        if args.src_ip:
            new_packet[IPv6].src = args.src_ip
        if args.dst_ip:
            new_packet[IPv6].dst = args.dst_ip

    # Layer 4: TCP or UDP ports
    if (TCP in new_packet or UDP in new_packet) and (args.src_port or args.dst_port):
        proto = TCP if TCP in new_packet else UDP
        if args.src_port:
            new_packet[proto].sport = args.src_port
        if args.dst_port:
            new_packet[proto].dport = args.dst_port
        # Remove checksum to trigger recalculation
        if proto == TCP:
            del new_packet[TCP].chksum
        else:
            del new_packet[UDP].chksum

    return new_packet


def main():
    """Main function to process PCAP file."""
    args = parse_arguments()
    validate_arguments(args)

    # Read input PCAP
    try:
        packets = rdpcap(args.infile)
    except Exception as e:
        print(f"Error reading PCAP file: {e}")
        sys.exit(1)

    # Process packets
    modified_packets = []
    for i, packet in enumerate(packets, 1):
        try:
            new_packet = modify_packet(packet, args)
            modified_packets.append(new_packet)

            # Verbose output
            if args.verbose:
                print(f"Packet {i}:")
                new_packet.show()
        except Exception as e:
            print(f"Warning: Skipping packet {i} due to error: {e}")
            modified_packets.append(packet)  # Copy unchanged

    # Write output PCAP
    try:
        wrpcap(args.outfile, modified_packets)
        print(f"Modified PCAP written to {args.outfile}")
    except Exception as e:
        print(f"Error writing PCAP file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()