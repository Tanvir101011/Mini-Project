#!/usr/bin/env python3
"""
DNSTwist: A private DNS proxy for penetration testers and network analysts.
Intercepts DNS queries and forges responses for specified or wildcard domains.
For authorized, personal use only. Do not share or distribute.
"""

import argparse
import sys
import socketserver
import logging
from dnslib import DNSRecord, RR, QTYPE, A, AAAA
import socket
import fnmatch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("DNSTwist")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="🛠️ DNSTwist: Configurable DNS proxy for testing and analysis."
    )
    parser.add_argument(
        "--fakeip",
        help="IP for fake DNS responses (e.g., 192.168.1.100 or 2001:db8::1)"
    )
    parser.add_argument(
        "--fakedomains",
        help="Comma-separated domains for fake responses, supports wildcards (e.g., example.com,*.test.com)"
    )
    parser.add_argument(
        "--nameservers",
        default="8.8.8.8",
        help="Comma-separated upstream DNS servers (e.g., 8.8.8.8,1.1.1.1)"
    )
    parser.add_argument(
        "--interface",
        default="127.0.0.1",
        help="Interface to listen on (e.g., 127.0.0.1 or 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=53,
        help="Port for DNS server (default: 53, requires root)"
    )
    parser.add_argument(
        "--tcp",
        action="store_true",
        help="Use TCP instead of UDP for DNS queries"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    return parser.parse_args()


def validate_arguments(args):
    """Validate command-line arguments."""
    if args.fakeip and not args.fakedomains:
        log.error("⚠️ --fakeip requires --fakedomains to specify target domains")
        sys.exit(1)
    if args.port < 1 or args.port > 65535:
        log.error("⚠️ Port must be between 1 and 65535")
        sys.exit(1)
    if args.port == 53 and not args.tcp:
        log.warning("⚠️ Port 53 requires root privileges for UDP")


class DNSHandler(socketserver.BaseRequestHandler):
    """Handle incoming DNS requests."""
    def handle(self):
        # Extract request data
        if self.server.tcp:
            data = self.request[0].strip()
            socket = self.request[1]
        else:
            data = self.request[0]
            socket = self.request[1]

        try:
            # Parse DNS request
            request = DNSRecord.parse(data)
            qname = str(request.q.qname).rstrip(".")
            qtype = QTYPE[request.q.qtype]

            if args.verbose:
                log.info(f"📥 Query: {qname} ({qtype}) from {self.client_address[0]}")

            # Check if query matches fake domains (exact or wildcard)
            fake_domains = args.fakedomains.split(",") if args.fakedomains else []
            matched = False
            for domain in fake_domains:
                if domain.startswith("*."):
                    # Wildcard match
                    pattern = domain[2:]  # Remove *.
                    if fnmatch.fnmatch(qname, f"*.{pattern}") or qname == pattern:
                        matched = True
                        break
                elif qname == domain:
                    # Exact match
                    matched = True
                    break

            if matched and args.fakeip:
                # Forge response
                reply = request.reply()
                if qtype == "A" and "." in args.fakeip:
                    reply.add_answer(RR(qname, QTYPE.A, rdata=A(args.fakeip)))
                elif qtype == "AAAA" and ":" in args.fakeip:
                    reply.add_answer(RR(qname, QTYPE.AAAA, rdata=AAAA(args.fakeip)))
                else:
                    reply = None  # Fallback to proxy
                if reply:
                    log.info(f"✅ Forged response for {qname}: {args.fakeip}")
            else:
                # Proxy to upstream server
                reply = self.proxy_request(data, args.nameservers.split(",")[0])
                if reply:
                    log.info(f"🔄 Proxied response for {qname}")

            # Send response
            if reply:
                if self.server.tcp:
                    socket.sendto(reply.pack() + b"\x00", self.client_address)
                else:
                    socket.sendto(reply.pack(), self.client_address)
            else:
                log.warning(f"⚠️ No response for {qname} ({qtype})")

        except Exception as e:
            log.error(f"⚠️ Error processing query: {e}")


    def proxy_request(self, data, nameserver):
        """Forward DNS query to upstream server."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.sendto(data, (nameserver, 53))
            response, _ = sock.recvfrom(1024)
            sock.close()
            return DNSRecord.parse(response)
        except Exception as e:
            log.error(f"⚠️ Proxy error: {e}")
            return None


def main():
    """Run the DNS proxy server."""
    global args
    args = parse_arguments()
    validate_arguments(args)

    # Set verbose logging
    if args.verbose:
        log.setLevel(logging.DEBUG)

    # Start DNS server
    try:
        server_class = socketserver.TCPServer if args.tcp else socketserver.UDPServer
        server = server_class((args.interface, args.port), DNSHandler)
        server.tcp = args.tcp
        log.info(f"🚀 Starting DNSTwist on {args.interface}:{args.port} ({'TCP' if args.tcp else 'UDP'})")
        log.info(f"📍 Fake domains: {args.fakedomains or 'None'} -> {args.fakeip or 'N/A'}")
        log.info(f"🌐 Upstream: {args.nameservers}")
        server.serve_forever()
    except PermissionError:
        log.error("⚠️ Port 53 requires root privileges. Run with sudo or use --port")
        sys.exit(1)
    except Exception as e:
        log.error(f"⚠️ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()