# ForceBreach

## Description
ForceBreach is a Python tool for studying authentication vulnerabilities in your private lab. Inspired by Crowbar, it performs brute-force attacks against SSH and RDP services, testing credentials with multi-threading and logging results in text and JSON formats. Designed for personal experimentation, it targets devices you own or have explicit permission to test, such as a lab server in your home network.

**Important**: Use ForceBreach only on systems you own or have clear permission to test. Unauthorized brute-forcing is illegal and may lead to legal consequences, account lockouts, or network disruptions. The tool is restricted to your lab to ensure ethical use.

## Features
- **Brute-Forcing**: Tests credentials on SSH and RDP services.
- **JSON Output**: Saves results in JSON for parsing/automation.
- **Multi-Threading**: Supports configurable thread counts for faster attacks.
- **Configurable**: Allows target IP, port, service, wordlists, and timeout settings.
- **Logging**: Saves logs to `forcebreach.log` and results to `forcebreach-output/`.
- **Quiet Mode**: Minimizes terminal output.
- **Educational**: Simple design for learning authentication security.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Network access to lab devices (e.g., `192.168.1.100`).
   - Private network you control.
2. **Install Dependencies**:
   - Save `setup_forcebreach.sh` to a directory (e.g., `/home/user/forcebreach/`).
   - Make executable and run:
     ```bash
     chmod +x setup_forcebreach.sh
     ./setup_forcebreach.sh
     ```
   - Installs `paramiko` and creates default wordlists.
3. Save `forcebreach.py` to the same directory.
4. Verify:
   ```bash
   python3 forcebreach.py --help
   ```

## Usage
ForceBreach tests credentials on SSH or RDP services to study authentication weaknesses. Below are examples and expected outcomes.

### Basic Commands
Brute-force SSH:
```bash
python3 forcebreach.py -t 192.168.1.100 -p 22 -s ssh -u users.txt -w passwords.txt -T 5
```

Brute-force RDP in quiet mode:
```bash
python3 forcebreach.py -t 192.168.1.100 -p 3389 -s rdp -u users.txt -w passwords.txt -T 10 -q
```

### Options
- `-t, --target`: Target IP (required, e.g., `192.168.1.100`).
- `-p, --port`: Target port (required, e.g., `22`).
- `-s, --service`: Service to brute-force (required, `ssh` or `rdp`).
- `-u, --user-list`: File with usernames (default: `/usr/share/wordlists/users.txt`).
- `-w, --pass-list`: File with passwords (default: `/usr/share/wordlists/passwords.txt`).
- `-T, --threads`: Number of threads (default: 5).
- `--timeout`: Connection timeout in seconds (default: 5).
- `-q, --quiet`: Log to file only.

### Features

#### Brute-Forcing
- **Purpose**: Test credentials on SSH/RDP services.
- **Usage**:
  ```bash
  python3 forcebreach.py -t 192.168.1.100 -p 22 -s ssh -u users.txt -w passwords.txt
  ```
- **Output**:
  ```
  2025-05-15 12:55:00 - INFO - Starting ForceBreach on 192.168.1.100:22, service: ssh, threads: 5
  2025-05-15 12:55:02 - INFO - SSH login successful: admin:password
  ```
- **Result File** (`forcebreach-output/192.168.1.100_22_ssh_20250515_125500.txt`):
  ```
  [2025-05-15 12:55:02] SSH login successful: admin:password
  [2025-05-15 12:55:03] Brute-force complete
  ```
- **JSON File** (`forcebreach-output/192.168.1.100_22_ssh_20250515_125500.json`):
  ```json
  {
    "target": "192.168.1.100",
    "port": 22,
    "service": "ssh",
    "results": [
      {"user": "admin", "password": "password", "status": "success", "message": "SSH login successful: admin:password"},
      {"user": "admin", "password": "admin123", "status": "failed", "message": ""}
    ],
    "timestamp": "2025-05-15 12:55:03"
  }
  ```
- **Tips**: Create `users.txt` and `passwords.txt` with credentials (e.g., `admin`, `password`).

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  python3 forcebreach.py -t 192.168.1.100 -p 22 -s ssh -q
  ```
- **Tips**: Check `forcebreach.log` with `tail -f forcebreach.log`.

### Workflow
1. Set up lab (VM with SSH server at `192.168.1.100`).
2. Install dependencies:
   ```bash
   ./setup_forcebreach.sh
   ```
3. Prepare wordlists (e.g., `echo "admin" > users.txt; echo "password" > passwords.txt`).
4. Run brute-force:
   ```bash
   python3 forcebreach.py -t 192.168.1.100 -p 22 -s ssh -u users.txt -w passwords.txt -T 5
   ```
5. Check logs (`forcebreach.log`) and results (`forcebreach-output/`); verify with manual login.
6. Stop with `Ctrl+C`; secure outputs (`rm -rf forcebreach-output/*`).

## Output
- **Logs**: `forcebreach.log`, e.g.:
  ```
  2025-05-15 12:55:00 - INFO - Starting ForceBreach on 192.168.1.100:22
  2025-05-15 12:55:02 - INFO - SSH login successful: admin:password
  ```
- **Results**: `forcebreach-output/<ip>_<port>_<service>_<timestamp>.txt` and `.json`, e.g.:
  ```
  [2025-05-15 12:55:02] SSH login successful: admin:password
  ```

## Notes
- **Environment**: Use on authorized systems (e.g., lab server).
- **Impact**: May cause lockouts; test with caution.
- **Ethics**: Avoid unauthorized use to prevent legal/security issues.
- **RDP Support**: Limited; requires an RDP library (e.g., `rdp-py`) for full functionality.

## Disclaimer
**Personal Use Only**: ForceBreach is for learning on systems you own or have permission to test. Unauthorized use is illegal and may lead to legal consequences, lockouts, or disruptions. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM with SSH/RDP server).
- Secure outputs (`forcebreach.log`, `forcebreach-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate systems without permission.
- Sharing sensitive output files.
- Production systems to prevent lockouts.

## Limitations
- Supports SSH and RDP (RDP limited without library); Crowbar includes VNC.
- Basic brute-forcing; no advanced rate limiting or proxy support.
- Depends on network access and service configuration.

## Tips
- Set up an SSH server (`sudo apt install openssh-server`).
- Verify target (`netcat -zv 192.168.1.100 22`).
- Use Wireshark to monitor login attempts.
- Test mitigations (e.g., strong passwords, SSH keys).
- Isolate setup to avoid misuse.

## License
For personal educational use; no formal license. Use responsibly.