# NetBrute

## Description
NetBrute is a Python tool for studying network service vulnerabilities in your private lab. Inspired by BruteSpray, it combines Nmap port scanning with automated brute-force attacks using Medusa to test credentials on services like SSH, FTP, Telnet, SMB, HTTP, HTTPS, MySQL, and RDP. Designed for personal experimentation, it targets devices you own or have explicit permission to test, such as a lab server or router in your home network. Results are saved in text and JSON formats for analysis.

**Important**: Use NetBrute only on systems you own or have clear permission to test. Unauthorized scanning or brute-forcing is illegal and may lead to legal consequences, account lockouts, or network disruptions. The tool is restricted to your lab to ensure ethical use.

## Features
- **Port Scanning**: Uses Nmap with version detection to identify open services.
- **Brute-Forcing**: Tests credentials on supported services via Medusa.
- **JSON Output**: Saves brute-force results in JSON for parsing/automation.
- **Configurable**: Supports target IP/CIDR, custom wordlists, and thread count.
- **Logging**: Saves detailed logs to `netbrute.log` and results to `netbrute-output/`.
- **Error Handling**: Validates dependencies and inputs.
- **Educational**: Simple design for learning network security.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Network access to lab devices (e.g., `192.168.1.0/24`).
   - Root privileges (`sudo`) for Nmap and Medusa.
   - Private network you control.
2. **Install Dependencies**:
   - Save `setup_netbrute.sh` to a directory (e.g., `/home/user/netbrute/`).
   - Make executable and run:
     ```bash
     chmod +x setup_netbrute.sh
     ./setup_netbrute.sh
     ```
   - Installs `nmap`, `medusa`, and Python libraries.
3. Save `netbrute.py` to the same directory.
4. Verify:
   ```bash
   python3 netbrute.py --help
   ```

## Usage
NetBrute scans for open services and attempts credential brute-forcing. Below are examples and expected outcomes.

### Basic Commands
Scan and brute-force a network:
```bash
python3 netbrute.py -t 192.168.1.0/24 -u users.txt -p passwords.txt -T 5
```

Use existing Nmap XML output:
```bash
python3 netbrute.py -f nmap_output.xml -u users.txt -p passwords.txt -T 5
```

### Options
- `-t, --target`: Target IP or CIDR range (e.g., `192.168.1.0/24`).
- `-f, --file`: Nmap XML output file (alternative to `-t`).
- `-u, --user-list`: File with usernames (default: `/usr/share/wordlists/users.txt`).
- `-p, --pass-list`: File with passwords (default: `/usr/share/wordlists/passwords.txt`).
- `-T, --threads`: Number of brute-force threads (default: 5).
- `-o, --output`: Nmap XML output file (default: `nmap_output.xml`).

### Features

#### Port Scanning
- **Purpose**: Identify open services using Nmap.
- **Usage**:
  ```bash
  python3 netbrute.py -t 192.168.1.100 -o scan.xml
  ```
- **Output**:
  ```
  2025-05-15 12:52:00 - Starting Nmap scan on 192.168.1.100
  2025-05-15 12:52:05 - Nmap scan completed. Output saved to scan.xml
  2025-05-15 12:52:06 - Parsed 2 open services from Nmap output
  ```
- **Tips**: Verify with `cat scan.xml` or `nmap 192.168.1.100`.

#### Brute-Forcing
- **Purpose**: Test credentials on services (e.g., SSH, FTP).
- **Usage**:
  ```bash
  python3 netbrute.py -t 192.168.1.100 -u users.txt -p passwords.txt
  ```
- **Output**:
  ```
  2025-05-15 12:52:10 - Starting brute-force on ssh at 192.168.1.100:22
  2025-05-15 12:52:15 - Credentials found for ssh at 192.168.1.100:22! Check netbrute-output/192.168.1.100_22_ssh_20250515_125215.txt
  ```
- **Result File** (`netbrute-output/192.168.1.100_22_ssh_20250515_125215.txt`):
  ```
  ACCOUNT FOUND: [ssh] Host: 192.168.1.100 User: admin Password: cisco
  ```
- **JSON File** (if implemented): Results are stored in text; extend script for JSON if needed.
- **Tips**: Create `users.txt` and `passwords.txt` with credentials (e.g., `admin`, `cisco`).

### Workflow
1. Set up lab (VM with target devices at `192.168.1.0/24`).
2. Install dependencies:
   ```bash
   ./setup_netbrute.sh
   ```
3. Prepare wordlists (e.g., `echo "admin" > users.txt; echo "cisco" > passwords.txt`).
4. Run scan and brute-force:
   ```bash
   python3 netbrute.py -t 192.168.1.0/24 -u users.txt -p passwords.txt -T 5
   ```
5. Check logs (`netbrute.log`) and results (`netbrute-output/`); verify with manual login.
6. Stop with `Ctrl+C`; secure outputs (`rm -rf netbrute-output/*`).

## Output
- **Logs**: `netbrute.log`, e.g.:
  ```
  2025-05-15 12:52:00 - INFO - Starting Nmap scan on 192.168.1.100
  2025-05-15 12:52:15 - INFO - Credentials found for ssh at 192.168.1.100:22
  ```
- **Results**: `netbrute-output/<ip>_<port>_<service>_<timestamp>.txt`, e.g.:
  ```
  ACCOUNT FOUND: [ssh] Host: 192.168.1.100 User: admin Password: cisco
  ```
- **Nmap Output**: `nmap_output.xml` (or specified file).

## Notes
- **Environment**: Use on authorized systems (e.g., lab server).
- **Root**: Requires `sudo` for Nmap/Medusa in some cases.
- **Impact**: May cause lockouts or DoS; test with caution.
- **Ethics**: Avoid unauthorized use to prevent legal/security issues.

## Disclaimer
**Personal Use Only**: NetBrute is for learning on systems you own or have permission to test. Unauthorized use is illegal and may lead to legal consequences, lockouts, or disruptions. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM with target devices).
- Secure outputs (`netbrute.log`, `netbrute-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate systems without permission.
- Sharing sensitive output files.
- Production systems to prevent lockouts or outages.

## Limitations
- Supports services mapped to Medusa modules (SSH, FTP, etc.); BruteSpray may cover more.
- No JSON output for results (extend script if needed).
- Depends on Nmap/Medusa availability and network access.

## Tips
- Set up a lab server (e.g., SSH with `sudo apt install openssh-server`).
- Verify target (`ping 192.168.1.100`).
- Use Wireshark to monitor traffic.
- Test mitigations (e.g., strong passwords, rate limiting).
- Isolate setup to avoid misuse.

## License
For personal educational use; no formal license. Use responsibly.