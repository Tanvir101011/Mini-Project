import argparse
import logging
import smtplib
import sys
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('smtptester.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class SMTPTester:
    def __init__(self, servers, recipient, sender="test@local.lab", subject="SMTP Test", body="This is a test email.", username=None, password=None, quiet=False):
        self.servers = servers  # List of (host, port) tuples
        self.recipient = recipient
        self.sender = sender
        self.subject = subject
        self.body = body
        self.username = username
        self.password = password
        self.quiet = quiet
        self.results = []
        self.output_file = f"smtptester_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    def create_email(self):
        """Create a test email."""
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = self.recipient
        msg['Subject'] = self.subject
        msg.attach(MIMEText(self.body, 'plain'))
        return msg

    def test_server(self, host, port):
        """Test a single SMTP server."""
        result = {'host': host, 'port': port, 'status': 'unknown', 'response': ''}
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(host, port, timeout=10)
            server.set_debuglevel(0)

            # Attempt STARTTLS if available
            try:
                server.starttls()
            except:
                pass  # Continue without TLS if not supported

            # Authenticate if credentials provided
            if self.username and self.password:
                try:
                    server.login(self.username, self.password)
                except smtplib.SMTPAuthenticationError as e:
                    result['status'] = 'auth_failed'
                    result['response'] = str(e)
                    return result

            # Send test email
            msg = self.create_email()
            server.sendmail(self.sender, self.recipient, msg.as_string())
            server.quit()

            result['status'] = 'success'
            result['response'] = 'Email sent successfully'
            logging.info(f"Success: {host}:{port} - Email sent to {self.recipient}")
        except smtplib.SMTPConnectError as e:
            result['status'] = 'connect_failed'
            result['response'] = str(e)
            logging.error(f"Connect failed: {host}:{port} - {str(e)}")
        except smtplib.SMTPRecipientsRefused as e:
            result['status'] = 'recipient_refused'
            result['response'] = str(e)
            logging.error(f"Recipient refused: {host}:{port} - {str(e)}")
        except Exception as e:
            result['status'] = 'error'
            result['response'] = str(e)
            logging.error(f"Error: {host}:{port} - {str(e)}")
        
        return result

    def save_results(self):
        """Save test results to a file."""
        with open(self.output_file, 'w') as f:
            for result in self.results:
                f.write(f"[{result['timestamp']}] {result['host']}:{result['port']}\n")
                f.write(f"Status: {result['status']}\n")
                f.write(f"Response: {result['response']}\n")
                f.write(f"{'-'*50}\n")
        logging.info(f"Results saved to {self.output_file}")

    def start(self):
        """Start testing SMTP servers."""
        logging.info(f"Starting SMTPTester: Servers={len(self.servers)}, Recipient={self.recipient}")
        for host, port in self.servers:
            result = self.test_server(host, port)
            result['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.results.append(result)
            time.sleep(1)  # Avoid overwhelming servers
        self.save_results()

def parse_servers(server_list):
    """Parse server list into (host, port) tuples."""
    servers = []
    for server in server_list:
        try:
            host, port = server.split(':')
            port = int(port)
            servers.append((host, port))
        except ValueError:
            logging.error(f"Invalid server format: {server} (expected host:port)")
    return servers

def read_servers_from_file(file_path):
    """Read servers from a file (host:port per line)."""
    try:
        with open(file_path, 'r') as f:
            return parse_servers([line.strip() for line in f if line.strip()])
    except Exception as e:
        logging.error(f"Error reading servers file: {str(e)}")
        return []

def main():
    parser = argparse.ArgumentParser(description="SMTPTester - A tool to test SMTP servers for learning.")
    parser.add_argument('-s', '--servers', nargs='+', help='SMTP servers (host:port, e.g., 127.0.0.1:25)')
    parser.add_argument('-f', '--servers-file', help='File with SMTP servers (host:port per line)')
    parser.add_argument('-r', '--recipient', required=True, help='Recipient email address')
    parser.add_argument('--sender', default='test@local.lab', help='Sender email address (default: test@local.lab)')
    parser.add_argument('--subject', default='SMTP Test', help='Email subject (default: SMTP Test)')
    parser.add_argument('--body', default='This is a test email.', help='Email body (default: This is a test email.)')
    parser.add_argument('-u', '--username', help='SMTP username for authentication')
    parser.add_argument('-p', '--password', help='SMTP password for authentication')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (log to file only)')

    args = parser.parse_args()

    # Collect servers from command line or file
    servers = []
    if args.servers:
        servers.extend(parse_servers(args.servers))
    if args.servers_file:
        servers.extend(read_servers_from_file(args.servers_file))

    if not servers:
        logging.error("No valid servers provided")
        sys.exit(1)

    if args.quiet:
        logging.getLogger().handlers = [logging.FileHandler('smtptester.log')]

    tester = SMTPTester(
        servers=servers,
        recipient=args.recipient,
        sender=args.sender,
        subject=args.subject,
        body=args.body,
        username=args.username,
        password=args.password,
        quiet=args.quiet
    )

    try:
        tester.start()
    except KeyboardInterrupt:
        logging.info("SMTPTester stopped by user")

if __name__ == "__main__":
    main()