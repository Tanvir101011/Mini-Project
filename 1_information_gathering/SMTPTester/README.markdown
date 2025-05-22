# SMTPTester

## Description
SMTPTester is a Python tool you can use to test SMTP servers in your own private network by sending test emails. It helps you learn how email servers work, check their configurations, and see how they respond to email attempts. Inspired by tools that probe SMTP servers, SMTPTester is designed for your personal experimentation in a controlled environment, like a home lab with servers you own or have permission to test.

**Important**: This tool is for your personal use only with servers and email accounts you own or have explicit permission to test. Using it on servers or accounts without clear authorization is illegal and could cause serious issues.

## Features
- Sends test emails to a specified recipient through an SMTP server.
- Supports authentication (username/password) or anonymous access.
- Tests multiple SMTP servers from a command line or a file (host:port per line).
- Logs server responses (success, errors, timeouts) to a text file.
- Quiet mode to reduce terminal output.
- Configurable email content (sender, subject, body) for flexible testing.
- Simple design for easy use in personal projects.

## Installation
1. **What You Need**:
   - Python 3.12 or later (check with `python3 --version`).
   - A computer on a private network you control (e.g., your home lab).
   - Access to an SMTP server you own or have permission to test (e.g., a local Postfix or Sendmail server).
   - No additional libraries required (uses Python’s built-in `smtplib`).
2. Save the `smtptester.py` script to a folder (e.g., `/home/user/smtptester/`).
3. Run the script:
   ```bash
   python3 smtptester.py --help
   ```

## How to Use
SMTPTester sends test emails to a recipient through one or more SMTP servers to check their functionality. You specify the servers, recipient, and optional settings like authentication or email content. Below is a guide on how to use each feature with examples and expected results.

### Basic Usage
Test a single SMTP server:
```bash
python3 smtptester.py -s 127.0.0.1:25 -r test@local.lab
```

Test multiple servers from a file:
```bash
python3 smtptester.py -f servers.txt -r test@local.lab
```

### Options
- `-s, --servers`: SMTP servers (host:port, e.g., `127.0.0.1:25`).
- `-f, --servers-file`: File with SMTP servers (host:port per line).
- `-r, --recipient`: Recipient email address (required).
- `--sender`: Sender email address (default: `test@local.lab`).
- `--subject`: Email subject (default: `SMTP Test`).
- `--body`: Email body (default: `This is a test email.`).
- `-u, --username`: SMTP username for authentication.
- `-p, --password`: SMTP password for authentication.
- `-q, --quiet`: Run quietly (logs to file only).

### Using Each Feature

#### 1. Testing a Single Server
**What It Does**: Sends a test email through one SMTP server.
**How to Use**:
1. Test a local server:
   ```bash
   python3 smtptester.py -s 127.0.0.1:25 -r test@local.lab
   ```
**What Happens**:
- The tool attempts to send an email and logs the result:
  ```
  2025-05-15 10:30:00 - Starting SMTPTester: Servers=1, Recipient=test@local.lab
  2025-05-15 10:30:01 - Success: 127.0.0.1:25 - Email sent to test@local.lab
  2025-05-15 10:30:01 - Results saved to smtptester_results_20250515_103001.txt
  ```
- Results file example:
  ```
  [2025-05-15 10:30:01] 127.0.0.1:25
  Status: success
  Response: Email sent successfully
  --------------------------------------------------
  ```
**Tips**:
- Set up a local SMTP server (e.g., Postfix) for testing.
- Use a test email address you control.

#### 2. Testing Multiple Servers
**What It Does**: Tests multiple SMTP servers from a file or command line.
**How to Use**:
1. Create a `servers.txt` file:
   ```
   127.0.0.1:25
   192.168.1.100:587
   ```
2. Run the tool:
   ```bash
   python3 smtptester.py -f servers.txt -r test@local.lab
   ```
3. Or specify multiple servers directly:
   ```bash
   python3 smtptester.py -s 127.0.0.1:25 192.168.1.100:587 -r test@local.lab
   ```
**What Happens**:
- Each server is tested, and results are logged:
  ```
  2025-05-15 10:35:00 - Starting SMTPTester: Servers=2, Recipient=test@local.lab
  2025-05-15 10:35:01 - Success: 127.0.0.1:25 - Email sent to test@local.lab
  2025-05-15 10:35:02 - Error: 192.168.1.100:587 - Connection refused
  2025-05-15 10:35:02 - Results saved to smtptester_results_20250515_103502.txt
  ```
**Tips**:
- Ensure `servers.txt` has one `host:port` per line.
- Test with servers you control to avoid issues.

#### 3. Using Authentication
**What It Does**: Tests servers requiring username/password.
**How to Use**:
1. Provide credentials:
   ```bash
   python3 smtptester.py -s 192.168.1.100:587 -r test@local.lab -u user -p pass123
   ```
**What Happens**:
- The tool attempts authentication before sending:
  ```
  2025-05-15 10:40:00 - Starting SMTPTester: Servers=1, Recipient=test@local.lab
  2025-05-15 10:40:01 - Success: 192.168.1.100:587 - Email sent to test@local.lab
  ```
- If authentication fails:
  ```
  2025-05-15 10:40:01 - Error: 192.168.1.100:587 - Authentication failed
  ```
**Tips**:
- Use credentials for your test server.
- Test with a server that supports STARTTLS (port 587).

#### 4. Customizing Email Content
**What It Does**: Allows custom sender, subject, and body.
**How to Use**:
1. Specify custom content:
   ```bash
   python3 smtptester.py -s 127.0.0.1:25 -r test@local.lab --sender me@lab.local --subject "Test Email" --body "Hello, this is a test!"
   ```
**What Happens**:
- The email uses the specified content:
  ```
  2025-05-15 10:45:00 - Starting SMTPTester: Servers=1, Recipient=test@local.lab
  2025-05-15 10:45:01 - Success: 127.0.0.1:25 - Email sent to test@local.lab
  ```
**Tips**:
- Keep the body short for quick tests.
- Verify the email content in the recipient’s inbox.

#### 5. Quiet Mode
**What It Does**: Reduces terminal output, logging only to the file.
**How to Use**:
1. Enable quiet mode:
   ```bash
   python3 smtptester.py -s 127.0.0.1:25 -r test@local.lab -q
   ```
**What Happens**:
- No terminal output; logs go to `smtptester.log`:
  ```
  $ python3 smtptester.py -s 127.0.0.1:25 -r test@local.lab -q
  [No output]
  ```
- Log file example:
  ```
  2025-05-15 10:50:00 - Starting SMTPTester: Servers=1, Recipient=test@local.lab
  2025-05-15 10:50:01 - Success: 127.0.0.1:25 - Email sent to test@local.lab
  ```
**Tips**:
- Check logs with `cat smtptester.log` or `tail -f smtptester.log`.
- Useful for testing multiple servers quietly.

#### 6. Stopping the Tool
**What It Does**: Stops testing when all servers are processed or you press Ctrl+C.
**How to Use**:
1. Start testing:
   ```bash
   python3 smtptester.py -s 127.0.0.1:25 -r test@local.lab
   ```
2. Press `Ctrl+C` to stop early.
**What Happens**:
- Testing stops, and results are saved:
  ```
  2025-05-15 10:55:00 - Starting SMTPTester: Servers=1, Recipient=test@local.lab
  ^C
  2025-05-15 10:55:01 - SMTPTester stopped by user
  2025-05-15 10:55:01 - Results saved to smtptester_results_20250515_105501.txt
  ```
**Tips**:
- Always stop the tool to free resources.
- Results are saved even if stopped early.

### Example Workflow
To experiment with SMTP servers in your home lab:
1. Set up a test SMTP server (e.g., Postfix on `127.0.0.1:25` or a VM at `192.168.1.100:587`).
2. Create a `servers.txt` file:
   ```
   127.0.0.1:25
   192.168.1.100:587
   ```
3. Test the servers:
   ```bash
   python3 smtptester.py -f servers.txt -r test@local.lab -u user -p pass123 -q
   ```
4. Check the recipient’s inbox for test emails.
5. Review `smtptester.log` and `smtptester_results_*.txt` for server responses.
6. Stop with `Ctrl+C` and delete output files securely.

## Output
- Logs are saved to `smtptester.log`.
- Test results are saved to `smtptester_results_<timestamp>.txt`.
- Example results file:
  ```
  [2025-05-15 10:30:01] 127.0.0.1:25
  Status: success
  Response: Email sent successfully
  --------------------------------------------------
  ```

## Important Notes
- **Environment**: Use SMTPTester only with SMTP servers and email accounts you own or have explicit permission to test (e.g., a local Postfix server in your lab).
- **Recipient Safety**: Use a test email address you control to avoid sending emails to real users.
- **Server Safety**: Test only servers you own or have permission to access to avoid causing disruptions.

## Disclaimer
**Personal Use Only**: SMTPTester is for your personal learning with servers and email accounts you own or have explicit permission to test. Using it on servers or accounts without clear authorization is illegal and could lead to legal consequences, technical issues, or unintended harm. Always ensure you have permission from the server owner before testing.

**Safe Use**:
- **Controlled Setup**: Use in a private lab (e.g., home network with your servers) to avoid affecting others. For example, test on `127.0.0.1` or a local VM.
- **Data Security**: Output files (`smtptester.log`, `smtptester_results_*.txt`) may contain sensitive data (e.g., email addresses). Store them securely and delete them after use (e.g., `rm smtptester_*.txt`).
- **Legal Compliance**: Follow all applicable laws and regulations in your area, including anti-spam laws like CAN-SPAM.
- **No Warranty**: This tool is provided “as is” for educational purposes. You are responsible for its use and any consequences.

**What to Avoid**:
- Do not test public SMTP servers (e.g., Gmail, Yahoo) without permission.
- Do not send emails to addresses you don’t own.
- Do not share output files, as they may contain private data.

## Limitations
- Requires network access to the SMTP server.
- Only supports basic SMTP testing (no advanced features like DKIM/SPF checks).
- May fail if the server requires complex authentication or non-standard ports.
- Limited to plain-text email bodies for simplicity.

## Testing Tips
- Set up Postfix: Install Postfix on a VM and configure it to listen on `25` or `587`.
- Verify servers: Use `telnet host port` to check server availability.
- Monitor traffic: Use `tcpdump` (e.g., `sudo tcpdump -i eth0 port 25`) to verify email attempts.
- Secure outputs: Delete files after use (`rm smtptester_*.txt`).
- Check logs in real-time: `tail -f smtptester.log`.

## Troubleshooting
- **Connection failed**: Ensure the server is running and the port is open (`telnet host port`).
- **Authentication errors**: Verify username/password and ensure the server supports STARTTLS.
- **Recipient refused**: Check the recipient address and server’s relay settings.
- **No servers provided**: Ensure `-s` or `-f` includes valid `host:port` entries.

## License
This tool is for your personal use. No formal license is provided, but please use it responsibly.