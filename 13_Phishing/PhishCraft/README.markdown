# PhishCraft

## Overview
PhishCraft is a command-line phishing tool for ethical cybersecurity researchers and penetration testers, designed for Kali Linux. It automates the creation, delivery, and tracking of phishing emails with embedded tracking pixels and hosts phishing pages to capture credentials. PhishCraft uses Flask for hosting, ngrok for WAN access, and a local SMTP server for email delivery. It is intended for authorized security testing only.

## Features
- Generates phishing emails with customizable HTML templates (e.g., password reset).
- Embeds tracking pixels to monitor email opens (IP, user-agent, timestamp).
- Hosts phishing pages locally, exposed via ngrok.
- Captures credentials (username, password) and victim details (IP, user-agent).
- Supports multiple recipients via CSV input.
- Logs email sends, pixel tracking, and credentials to JSON and CSV.
- Redirects victims to legitimate sites after capture (optional).
- Generates a summary report with campaign statistics.
- Optimized for Kali Linux.

## Prerequisites
- Kali Linux (or similar environment)
- Python 3.6 or higher
- Python libraries: `flask`, `requests`, `pyngrok` (installed via setup script)
- Ngrok account and auth token (free tier sufficient)
- Local SMTP server (e.g., Postfix) configured on localhost:25
- Input: Internet connection, ngrok access, recipient CSV

## Installation

### Setup
1. Clone or download the repository.
2. Run the setup script to install dependencies and create a virtual environment:
   ```bash
   chmod +x set_upfile.sh
   ./set_upfile.sh
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Configure ngrok:
   - Sign up at [ngrok.com](https://ngrok.com) and get your auth token.
   - Set the token:
     ```bash
     export NGROK_AUTH_TOKEN=your_auth_token_here
     ```
5. Configure a local SMTP server:
   - Install Postfix:
     ```bash
     sudo apt-get install postfix
     ```
   - Ensure it’s running on localhost:25.

## Usage
Run the tool with:
```bash
python phishcraft.py -r <recipients> -s <sender> [-e <email-template>] [-p <phish-template>] [-j <subject>] [-u <redirect>] [-o <output-dir>] [--smtp-port <port>] [--flask-port <port>] [--verbose]
```

- **-r, --recipients**: CSV file with recipient emails (column: `email`).
- **-s, --sender**: Sender email (e.g., `alert@company.com`).
- **-e, --email-template**: Email template file (default: `email_reset.html`).
- **-p, --phish-template**: Phishing page template (default: `login.html`).
- **-j, --subject**: Email subject (default: `Urgent: Reset Your Password`).
- **-u, --redirect**: Redirect URL after capture (e.g., `https://example.com`).
- **-o, --output-dir**: Output directory (default: `phishcraft_output`).
- **--smtp-port**: SMTP port (default: 25).
- **--flask-port**: Flask port (default: 5000).
- **--verbose**: Print detailed logs.

### Recipient CSV Format
```csv
email
user1@example.com
user2@example.com
```

### Examples
1. **Send a password reset phishing email**:
   ```bash
   python phishcraft.py -r recipients.csv -s alert@company.com -e email_reset.html -p login.html -u https://example.com -o results --verbose
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Ngrok tunnel started: https://abc123.ngrok.io
   2025-05-15 18:30:00 - INFO - Sent email to user1@example.com
   2025-05-15 18:30:00 - INFO - Phishing page hosted at: https://abc123.ngrok.io/phish
   2025-05-15 18:30:00 - INFO - Waiting for interactions...
   2025-05-15 18:30:05 - INFO - Tracked: 192.168.1.100 opened email (ID: 20250515183000)
   2025-05-15 18:30:10 - INFO - Captured: testuser:pass123 from 192.168.1.100
   ```

2. **Use custom templates**:
   ```bash
   python phishcraft.py -r recipients.csv -s alert@company.com -e custom_email.html -p custom_login.html -o results
   ```

### Output Files
- **Tracking Log** (`tracking.json`):
  ```
  {"tracking_id":"20250515183000","timestamp":"2025-05-15T18:30:05","ip":"192.168.1.100","user_agent":"Mozilla/5.0..."}
  ```
- **Credentials CSV** (`credentials.csv`):
  ```csv
  timestamp,ip,user_agent,username,password
  2025-05-15T18:30:10,192.168.1.100,Mozilla/5.0...,testuser,pass123
  ```
- **Summary Report** (`summary.txt`):
  ```
  PhishCraft Summary Report - 2025-05-15T18:30:00
  --------------------------------------------------
  Sender: alert@company.com
  Subject: Urgent: Reset Your Password
  Emails Sent: 2
  Emails Opened: 1
  Credentials Captured: 1
  --------------------------------------------------
  ```

## Creating Custom Templates
1. **Email Template**:
   - Create an HTML file (e.g., `custom_email.html`) with placeholders:
     ```html
     <p>Click <a href="{{PHISH_URL}}">here</a> to reset your password.</p>
     <img src="{{TRACKING_PIXEL}}" style="display:none;" />
     ```
   - Place in `templates/`.
2. **Phishing Page**:
   - Create an HTML file (e.g., `custom_login.html`) with a form:
     ```html
     <form action="/login" method="POST">
         <input type="text" name="username" placeholder="Username" required>
         <input type="password" name="password" placeholder="Password" required>
         <button type="submit">Login</button>
     </form>
     ```
   - Place in `templates/`.
3. Run with:
   ```bash
   python phishcraft.py -r recipients.csv -s alert@company.com -e custom_email.html -p custom_login.html
   ```

## Limitations
- Requires a local SMTP server; external servers (e.g., Gmail SMTP) need additional configuration.
- Ngrok free tier has temporary URLs and connection limits.
- Tracking pixel may be blocked by email clients or security software.
- Credential capture is basic; advanced phishing may require session cookies or 2FA handling.
- No built-in spoofing; sender email must be valid for SMTP.
- Assumes stable internet and ngrok access.

## License
MIT License

## Warning
PhishCraft is for ethical security testing and authorized penetration testing only. Unauthorized use to phish or exploit systems you do not own or have permission to test is illegal and unethical. Always obtain explicit permission before conducting phishing simulations. The author is not responsible for misuse.

## Recommendations
- Test in a controlled lab environment with dummy emails and credentials.
- Use with explicit client permission and clear scope.
- Combine with security awareness training.
- Use a VPN for anonymity during testing.
- Monitor ngrok dashboard for connection issues.
- Ensure SMTP server is secure to prevent abuse.