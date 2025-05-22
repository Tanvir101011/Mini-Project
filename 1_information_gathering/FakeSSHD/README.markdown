# FakeSSHD

## Description
FakeSSHD is a Python-based fake SSH server designed for ethical penetration testing. It simulates an SSH server to capture login credentials (username and password) in a controlled environment, helping security professionals assess SSH authentication vulnerabilities and user awareness. Similar to Fiked, which targets VPN authentication, FakeSSHD focuses on SSH services and is intended for authorized security assessments on Kali Linux.

**WARNING**: This tool is for ethical use only. Unauthorized use to capture credentials without explicit permission is illegal and unethical. Always obtain proper authorization before conducting penetration tests.

## Features
- Simulates an SSH server with a customizable banner to mimic real SSH services.
- Captures usernames and passwords entered by clients, logging them to a file and optionally to stdout.
- Supports customizable host and port for targeted testing.
- Quiet mode for silent operation (logs to file only).
- Multi-threaded client handling for simultaneous connections.
- Graceful shutdown on interrupt (Ctrl+C) to ensure clean termination.
- Logs all connection attempts and captured credentials for analysis.

## Installation
1. **Prerequisites**:
   - Kali Linux (2024.4 or compatible) with Python 3.12+ installed.
   - Root access for binding to privileged ports (e.g., port 22).
   - No external dependencies required (uses standard Python libraries).
2. Save the `fakesahd.py` script to a directory (e.g., `/home/kali/fakesahd/`).
3. Ensure no real SSH server is running on the target port (stop it with `sudo systemctl stop sshd` if necessary).
4. Run the script with root permissions:
   ```bash
   sudo python3 fakesahd.py
   ```

## Usage
FakeSSHD can be run with default settings or customized using command-line options. Below is a detailed guide on how to use each feature, including examples and expected outcomes.

### General Usage
Start the fake SSH server with default settings (binds to `0.0.0.0:22`):
```bash
sudo python3 fakesahd.py
```

### Command-Line Options
- `-H, --host`: Specify the host IP to bind (default: `0.0.0.0`).
- `-p, --port`: Specify the port to bind (default: `22`).
- `-b, --banner`: Customize the SSH banner (default: `SSH-2.0-OpenSSH_7.4p1 Debian-10+deb9u7`).
- `-q, --quiet`: Run in quiet mode (logs to file only, no stdout).

### Feature Usage Instructions

#### 1. Simulating an SSH Server
**Description**: FakeSSHD mimics an SSH server by listening for connections and presenting a fake login prompt to capture credentials.
**How to Use**:
1. Run the tool with default settings:
   ```bash
   sudo python3 fakesahd.py
   ```
2. Clients connecting via SSH (e.g., `ssh user@<server-ip>`) will see a login prompt.
3. The tool sends the SSH banner, prompts for username and password, and logs the input.
**Outcome**:
- Logs show connections and credentials in `fakesahd.log` and (by default) stdout:
  ```
⁠
  ```
  2025-05-15 09:45:23,123 - INFO - Connection from 192.168.1.50:12345
  2025-05-15 09:45:25,456 - INFO - Captured from 192.168.1.50: username='admin', password='password123'
  ```
- Clients receive a fake “Permission denied” message to simulate a failed login.
**Tips**:
- Test with an SSH client: `ssh test@<server-ip>`.
- Ensure no real SSH server conflicts with the port.

#### 2. Customizable Host and Port
**Description**: Bind the server to a specific IP and port for targeted testing.
**How to Use**:
1. Specify host and port:
   ```bash
   sudo python3 fakesahd.py -H 192.168.1.100 -p 2222
   ```
2. Clients must connect to the specified IP/port (e.g., `ssh user@192.168.1.100 -p 2222`).
**Outcome**:
- Server binds to the specified IP/port, logged as:
  ```
  2025-05-15 09:50:00,000 - INFO - Fake SSH server started on 192.168.1.100:2222
  ```
**Tips**:
- Use non-privileged ports (e.g., `2222`) to avoid needing root.
- Verify reachability with `nmap -p 2222 192.168.1.100`.

#### 3. Customizable SSH Banner
**Description**: Set a custom SSH banner to mimic specific server versions.
**How to Use**:
1. Specify a banner:
   ```bash
   sudo python3 fakesahd.py -b "SSH-2.0-MyFakeServer_1.0"
   ```
2. Clients see the custom banner in their SSH client.
**Outcome**:
- Banner is sent to clients, logged as:
  ```
  2025-05-15 09:55:00,000 - INFO - Fake SSH server started on 0.0.0.0:22
  ```
- Client view:
  ```
  $ ssh user@<server-ip>
  SSH-2.0-MyFakeServer_1.0
  login:
  ```
**Tips**:
- Use realistic banners (e.g., `SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1`).
- Avoid suspicious banners that may alert users.

#### 4. Credential Capture and Logging
**Description**: Captures and logs usernames and passwords entered by clients.
**How to Use**:
1. Run the tool:
   ```bash
   sudo python3 fakesahd.py
   ```
2. Credentials are logged automatically when clients connect.
3. Check `fakesahd.log` or stdout.
**Outcome**:
- Logs include client IP, port, username, and password:
  ```
  2025-05-15 10:00:00,000 - INFO - Captured from 192.168.1.50: username='testuser', password='secret123'
  ```
**Tips**:
- Monitor logs in real-time: `tail -f fakesahd.log`.
- Secure logs post-testing to prevent leaks.

#### 5. Quiet Mode
**Description**: Disables stdout logging for stealthy operation (logs to file only).
**How to Use**:
1. Enable quiet mode:
   ```bash
   sudo python3 fakesahd.py -q
   ```
2. No terminal output; logs written to `fakesahd.log`.
**Outcome**:
- Terminal is silent, but logs capture activity:
  ```
  $ sudo python3 fakesahd.py -q
  [No output]
  ```
- Log file:
  ```
  2025-05-15 10:05:00,000 - INFO - Fake SSH server started on 0.0.0.0:22
  ```
**Tips**:
- Ideal for background operation.
- Verify logs with `cat fakesahd.log`.

#### 6. Multi-Threaded Client Handling
**Description**: Handles multiple simultaneous client connections.
**How to Use**:
1. Run the tool:
   ```bash
   sudo python3 fakesahd.py
   ```
2. Connect multiple clients (e.g., from different machines).
**Outcome**:
- Each connection is handled separately:
  ```
  2025-05-15 10:10:00,000 - INFO - Connection from 192.168.1.50:12345
  2025-05-15 10:10:01,000 - INFO - Connection from 192.168.1.51:54321
  ```
**Tips**:
- Test with multiple `ssh` commands.
- Monitor resource usage for many connections.

#### 7. Graceful Shutdown
**Description**: Stops the server cleanly on interrupt (Ctrl+C).
**How to Use**:
1. Start the server:
   ```bash
   sudo python3 fakesahd.py
   ```
2. Press `Ctrl+C` to stop.
**Outcome**:
- Server shuts down and logs:
  ```
  2025-05-15 10:15:00,000 - INFO - Fake SSH server started on 0.0.0.0:22
  ^C
  2025-05-15 10:15:10,000 - INFO - Fake SSH server stopped
  ```
**Tips**:
- Stop after testing to free the port.
- Restart with the same command if needed.

### Example Workflow
To test a network for weak SSH credentials:
1. Obtain written permission from the network owner.
2. Run FakeSSHD:
   ```bash
   sudo python3 fakesahd.py -H 192.168.1.100 -p 2222 -b "SSH-2.0-OpenSSH_8.9p1" -q
   ```
3. Redirect traffic to `192.168.1.100:2222` (e.g., via authorized DNS spoofing).
4. Monitor `fakesahd.log` for credentials.
5. Stop with `Ctrl+C` and securely delete logs.

## Output
- Logs are saved to `fakesahd.log` in the working directory.
- Example log:
  ```
  2025-05-15 09:45:23,123 - INFO - Connection from 192.168.1.50:12345
  2025-05-15 09:45:25,456 - INFO - Captured from 192.168.1.50: username='admin', password='password123'
  ```

## Ethical Use and Disclaimer

### Legal and Ethical Use Only
FakeSSHD is a penetration testing tool for authorized security assessments. Unauthorized use to capture credentials or intercept traffic is illegal and unethical, potentially violating laws like the Computer Fraud and Abuse Act (CFAA) in the US or similar regulations worldwide. Misuse may lead to criminal charges, civil penalties, or other legal consequences.

### Usage Guidelines
- **Explicit Permission**: Obtain written authorization from the system/network owner before use, even in lab environments unless you own all systems.
- **Controlled Environment**: Deploy in isolated environments or authorized tests to avoid impacting production systems or users.
- **Data Security**: Treat captured credentials as sensitive. Store logs securely, share only with authorized parties, and delete promptly after testing.
- **Transparency**: Inform stakeholders about the tool’s purpose and scope during testing.
- **Compliance**: Adhere to laws, policies, and standards (e.g., OWASP, NIST).

### Limitations and Risks
- FakeSSHD is not a full SSH server and may be detected by advanced clients or security tools.
- Improper configuration (e.g., public IP binding) risks unintended access or detection.
- Logs are unencrypted; secure them to prevent unauthorized access.

### No Warranty
FakeSSHD is provided “as is” without warranty. The authors and xAI are not liable for damages, losses, or legal consequences from its use or misuse. Users are fully responsible for ensuring legal and ethical use.

### Reporting Misuse
If you suspect malicious use of FakeSSHD, report to authorities or the tool’s maintainers (if hosted) with evidence.

## Limitations
- Does not support full SSH protocol negotiation (mimics only login prompt).
- Not a complete man-in-the-middle tool; captures credentials only.
- May be detected by advanced SSH clients or security tools.

## Testing Tips
- Verify server operation: `nmap -p 2222 192.168.1.100` or `nc 192.168.1.100 2222`.
- Secure logs post-testing: `shred -u fakesahd.log`.
- Use realistic configurations to avoid detection.

## Contributing
Contributions are welcome! Submit pull requests or issues via the repository (if hosted). Follow PEP 8 standards and include comments.

## License
Released under the MIT License. See `LICENSE` for details (not included here but recommended).

## Contact
For questions or feedback, engage with the Kali Linux community forums or contact repository maintainers (if applicable).