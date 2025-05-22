# SSLBlaze

## Description
SSLBlaze is a Python-based tool designed for ethical security testing in your private lab (Ubuntu 24.04, home network). It simulates SSL/TLS exhaustion attacks, such as renegotiation and reconnect attacks, to stress-test SSL/TLS-enabled servers (e.g., Apache, Nginx) and evaluate their resilience against resource exhaustion. The tool features a CLI interface, SQLite logging, JSON output, and multi-threading, integrating with your tools like **NetSentry**, **NatPiercer**, **WiFiCrush**, **IdentityForge**, and **SlowStrike**.

**Important**: Use SSLBlaze only on servers and networks you own or have explicit permission to test. Unauthorized SSL/TLS attacks are illegal and may lead to legal consequences, network disruptions, or ethical issues. This tool is restricted to your lab for responsible use. Modern servers may mitigate attacks with renegotiation disabled or intrusion detection systems (IDS).[](https://www.infoworld.com/article/2263741/new-dos-tool-from-thc-another-overhyped-threat.html)

## Features
- **SSL/TLS Exhaustion Attacks**: Simulates renegotiation and reconnect attacks to exhaust server resources.
- **Output Formats**: SQLite database, JSON, and text logs.
- **Multi-Threading**: Efficient connection management with configurable threads.
- **Quiet Mode**: Minimizes terminal output.
- **Logging**: Saves logs to `sslblaze.log` and results to `sslblaze-output/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Network access to target SSL/TLS server.
   - Private network/lab you control.
2. **Install Dependencies**:
   - Save `setup_sslblaze.sh` to a directory (e.g., `/home/user/sslblaze/`).
   - Make executable and run:
     ```bash
     chmod +x setup_sslblaze.sh
     ./setup_sslblaze.sh
     ```
   - Installs Python and pip.
3. Save `sslblaze.py` to the same directory.
4. Verify:
   ```bash
   python3 sslblaze.py --help
   ```

## Usage
SSLBlaze simulates SSL/TLS exhaustion attacks in a controlled lab setting to test server resilience. Below are examples and expected outcomes.

### Basic Commands
Simulate a renegotiation attack:
```bash
python3 sslblaze.py -t example.com -m renegotiate -c 100 -d 60
```

Simulate a reconnect attack:
```bash
python3 sslblaze.py -t example.com -p 443 -m reconnect -c 50 -d 30
```

Run in quiet mode:
```bash
python3 sslblaze.py -t example.com -m renegotiate -c 100 -d 60 -q
```

### Options
- `-t, --target`: Target hostname or IP address (required).
- `-p, --port`: Target port (default: 443).
- `-m, --mode`: Attack mode: renegotiate or reconnect (default: renegotiate).
- `-c, --connections`: Number of concurrent connections (default: 100).
- `-i, --interval`: Interval between handshakes in seconds (default: 1).
- `-d, --duration`: Attack duration in seconds (default: 60).
- `-T, --threads`: Number of threads (default: 5).
- `-q, --quiet`: Log to file only.

### Features

#### Renegotiation Attack
- **Purpose**: Simulate repeated SSL handshakes to exhaust server resources.
- **Usage**:
  ```bash
  python3 sslblaze.py -t example.com -m renegotiate -c 100 -d 60
  ```
- **Output**:
  ```
  2025-05-15 16:00:00 - INFO - Starting SSLBlaze against example.com:443 in renegotiate mode
  2025-05-15 16:01:00 - INFO - Renegotiation attack to example.com:443 completed, 500 handshakes
  ```
- **Result File** (`sslblaze-output/blaze_20250515_160000.txt`):
  ```
  === SSLBlaze Results ===
  Timestamp: 2025-05-15 16:01:00
  [2025-05-15 16:01:00] Renegotiation attack to example.com:443 completed, 500 handshakes, Target=example.com:443, Mode=renegotiate, Handshakes=500, Connections=100
  ```
- **JSON File** (`sslblaze-output/blaze_20250515_160000.json`):
  ```json
  {
    "target": "example.com",
    "port": 443,
    "mode": "renegotiate",
    "connections": 100,
    "duration": 60,
    "total_handshakes": 500,
    "actions": [
      {
        "target": "example.com",
        "port": 443,
        "mode": "renegotiate",
        "handshakes": 500,
        "connections": 100,
        "status": "Renegotiation attack to example.com:443 completed, 500 handshakes",
        "timestamp": "2025-05-15 16:01:00"
      }
    ],
    "timestamp": "2025-05-15 16:01:00"
  }
  ```
- **Tips**: Use **NetSentry** to monitor server traffic; test with a local Apache/Nginx server with SSL enabled.

#### Reconnect Attack
- **Purpose**: Simulate repeated SSL connections to consume server resources.
- **Usage**:
  ```bash
  python3 sslblaze.py -t example.com -p 443 -m reconnect -c 50 -d 30
  ```
- **Output**:
  ```
  2025-05-15 16:00:00 - INFO - Starting SSLBlaze against example.com:443 in reconnect mode
  2025-05-15 16:00:30 - INFO - Reconnect attack to example.com:443 completed, 300 handshakes
  ```
- **Tips**: Test non-443 ports (e.g., SMTPS, POP3S) for servers without SSL accelerators.[](https://blog.insecure.in/thc-ssl-dos-tool-released/)

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  python3 sslblaze.py -t example.com -m renegotiate -c 100 -d 60 -q
  ```
- **Tips**: Monitor `sslblaze.log` with `tail -f sslblaze.log`.

### Workflow
1. Set up lab (VM with SSL-enabled server, e.g., Apache/Nginx, network access).
2. Install dependencies:
   ```bash
   ./setup_sslblaze.sh
   ```
3. Run SSLBlaze:
   ```bash
   python3 sslblaze.py -t example.com -m renegotiate -c 100 -d 60
   ```
4. Monitor output in terminal or `sslblaze.log`.
5. Check results in `sslblaze-output/` (text, JSON, SQLite).
6. Stop with `Ctrl+C`; secure outputs (`rm -rf sslblaze-output/*`).

## Output
- **Logs**: `sslblaze.log`, e.g.:
  ```
  2025-05-15 16:00:00 - INFO - Starting SSLBlaze against example.com:443 in renegotiate mode
  2025-05-15 16:01:00 - INFO - Renegotiation attack to example.com:443 completed, 500 handshakes
  ```
- **Results**: `sslblaze-output/blaze_<timestamp>.txt` and `.json`.
- **Database**: `sslblaze-output/sslblaze.db` (SQLite).

## Notes
- **Environment**: Use on authorized servers/networks in your lab.
- **Impact**: Exhaustion attacks may degrade server performance; modern servers may mitigate with renegotiation disabled or IDS.[](https://www.infoworld.com/article/2263741/new-dos-tool-from-thc-another-overhyped-threat.html)
- **Ethics**: Avoid unauthorized testing to prevent legal/security issues.
- **Dependencies**: Minimal; uses Python’s `ssl` and `socket` libraries.
- **Root**: Not required, but network access is needed.
- **Sources**: Built for SSL/TLS testing, leveraging security concepts from Kali Linux toolsets and OWASP guidelines.[](https://www.kali.org/tools/thc-ssl-dos/)

## Disclaimer
**Personal Use Only**: SSLBlaze is for learning on servers/networks you own or have permission to test. Unauthorized SSL/TLS attacks are illegal and may lead to legal consequences or ethical issues. Ensure compliance with local laws, including the Computer Misuse Act 1990.[](https://www.softwaretestinghelp.com/ddos-attack-tools/)

**Safe Use**:
- Use in a private lab (e.g., VM with isolated network).
- Secure outputs (`sslblaze.log`, `sslblaze-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate networks without permission.
- Sharing sensitive output files.
- Production environments to prevent disruptions.

## Limitations
- **Attack Scope**: Simulates renegotiation and reconnect attacks; lacks other DoS methods (e.g., HTTPS flood).
- **Mitigation**: Servers with renegotiation disabled or IDS may block attacks.[](https://www.infoworld.com/article/2263741/new-dos-tool-from-thc-another-overhyped-threat.html)
- **Interface**: CLI-only; lacks GUI or TUI.
- **Protocol**: Focuses on SSL/TLS; no other protocols (e.g., DTLS).

## Tips
- Test with a local Apache/Nginx server with SSL enabled to simulate real TLS traffic.
- Use Wireshark or **NetSentry** to monitor handshake traffic (filter: `tls.handshake.type == 1`).[](https://blog.apnic.net/2022/11/18/service-exhaustion-floods-http-https-flood-http-pipelining-and-ssl-renegotiation-ddos-attack/)
- Combine with **WiFiCrush** for network access or **NatPiercer** for tunneling.
- Adjust connections and interval to avoid overwhelming lab resources.
- Check server logs to assess attack impact; disable renegotiation to mitigate (`SSLInsecureRenegotiation off` in Apache).[](https://security.stackexchange.com/questions/45410/how-to-mitigate-ssl-based-ddos-attacks)

## License
For personal educational use; no formal license. Use responsibly.