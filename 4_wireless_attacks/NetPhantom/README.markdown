# NetPhantom

## Description
NetPhantom is a Python-based tool for Wi-Fi and Ethernet security auditing and phishing, inspired by **Ghost Phisher**. It emulates access points, deploys fake DNS, DHCP, and HTTP servers, and captures credentials, designed for educational use in your private lab (Ubuntu 24.04, home network). Built with `scapy`, `dns`, and SQLite, it supports multi-threading, JSON output, and a CLI interface, integrating with your tools like **WebSentry**, **WiFiCrush**, and **SQLStrike**.

**Important**: Use NetPhantom only on networks/systems you own or have explicit permission to test. Unauthorized use is illegal and may lead to legal consequences, network disruptions, or ethical issues. The tool is restricted to your lab for responsible use.

## Features
- **Fake AP**: Emulates Wi-Fi access points with customizable SSID.
- **Fake Servers**: Runs DNS, DHCP, and HTTP servers for phishing.
- **Credential Capture**: Logs credentials via phishing pages to SQLite.
- **DNS Spoofing**: Redirects traffic to malicious IPs (optional).
- **Multi-Threading**: Handles concurrent tasks efficiently.
- **JSON Output**: Saves results for parsing/automation.
- **Logging**: Saves logs to `netphantom.log` and results to `netphantom-output/`.
- **Quiet Mode**: Minimizes terminal output.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Wireless adapter supporting monitor mode (e.g., `wlan0`).
   - Root privileges (`sudo`) for monitor mode and packet handling.
   - Private network you control.
2. **Install Dependencies**:
   - Save `setup_netphantom.sh` to a directory (e.g., `/home/user/netphantom/`).
   - Make executable and run:
     ```bash
     chmod +x setup_netphantom.sh
     ./setup_netphantom.sh
     ```
   - Installs `scapy`, `dnspython`, `hostapd`, `dnsmasq`, and `aircrack-ng`.
3. Save `netphantom.py` to the same directory.
4. Create a phishing page (`login.html`):
   ```bash
   echo '<form method="POST"><input name="username" type="text"><input name="password" type="password"><input type="submit"></form>' > login.html
   ```
5. Verify:
   ```bash
   python3 netphantom.py --help
   ```

## Usage
NetPhantom creates fake Wi-Fi APs and servers to capture credentials in a controlled lab setting. Below are examples and expected outcomes.

### Basic Commands
Start fake AP and HTTP server:
```bash
sudo python3 netphantom.py -i wlan0 -s MyAP -p login.html
```

Enable DNS spoofing in quiet mode:
```bash
sudo python3 netphantom.py -i wlan0 -s MyAP -p login.html --dns-spoof -T 5 -q
```

### Options
- `-i, --interface`: Wireless interface (required, e.g., `wlan0`).
- `-s, --ssid`: SSID for fake AP (required, e.g., `MyAP`).
- `-p, --phishing-page`: Phishing page file (default: `login.html`).
- `--dns-spoof`: Enable DNS spoofing.
- `-T, --threads`: Number of threads (default: 5).
- `-q, --quiet`: Log to file only.

### Features

#### Fake Access Point
- **Purpose**: Emulate a Wi-Fi AP to attract clients.
- **Usage**:
  ```bash
  sudo python3 netphantom.py -i wlan0 -s MyAP -p login.html
  ```
- **Output**:
  ```
  2025-05-15 14:00:00 - INFO - Starting NetPhantom with SSID: MyAP
  2025-05-15 14:00:02 - INFO - Fake AP started
  ```
- **Tips**: Use **WiFiCrush** to capture handshakes for WPA testing.

#### Credential Capture
- **Purpose**: Log credentials via phishing page.
- **Usage**:
  ```bash
  sudo python3 netphantom.py -i wlan0 -s MyAP -p login.html
  ```
- **Output**:
  ```
  2025-05-15 14:00:05 - INFO - Credential captured: username=test&password=secret
  ```
- **Result File** (`netphantom-output/phantom_MyAP_20250515_140000.txt`):
  ```
  [2025-05-15 14:00:05] POST /: username=test&password=secret
  [2025-05-15 14:00:06] Phantom run complete
  ```
- **JSON File** (`netphantom-output/phantom_MyAP_20250515_140000.json`):
  ```json
  {
    "ssid": "MyAP",
    "interface": "wlan0",
    "credentials": [
      {
        "method": "POST",
        "path": "/",
        "headers": {},
        "body": "username=test&password=secret",
        "timestamp": "2025-05-15 14:00:05"
      }
    ],
    "timestamp": "2025-05-15 14:00:06"
  }
  ```
- **Tips**: Use **WordForge** to generate phishing page payloads.

#### DNS Spoofing
- **Purpose**: Redirect traffic to malicious IPs.
- **Usage**:
  ```bash
  sudo python3 netphantom.py -i wlan0 -s MyAP -p login.html --dns-spoof
  ```
- **Output**:
  ```
  2025-05-15 14:00:03 - INFO - Starting fake DNS server
  ```
- **Tips**: Combine with **DNSTwist** for advanced DNS spoofing.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  sudo python3 netphantom.py -i wlan0 -s MyAP -p login.html -q
  ```
- **Tips**: Monitor `netphantom.log` with `tail -f netphantom.log`.

### Workflow
1. Set up lab (VM with Wi-Fi adapter in monitor mode).
2. Install dependencies:
   ```bash
   ./setup_netphantom.sh
   ```
3. Create `login.html` phishing page.
4. Run NetPhantom:
   ```bash
   sudo python3 netphantom.py -i wlan0 -s MyAP -p login.html --dns-spoof
   ```
5. Connect a test device to `MyAP`; submit credentials.
6. Check logs (`netphantom.log`) and results (`netphantom-output/`).
7. Stop with `Ctrl+C`; secure outputs (`rm -rf netphantom-output/*`).

## Output
- **Logs**: `netphantom.log`, e.g.:
  ```
  2025-05-15 14:00:00 - INFO - Starting NetPhantom with SSID: MyAP
  2025-05-15 14:00:05 - INFO - Credential captured: username=test&password=secret
  ```
- **Results**: `netphantom-output/phantom_<ssid>_<timestamp>.txt` and `.json`.
- **Database**: `netphantom-output/netphantom.db` (SQLite).

## Notes
- **Environment**: Use on authorized networks in your lab.
- **Impact**: Fake APs may disrupt networks; test with caution.
- **Ethics**: Avoid unauthorized use to prevent legal/security issues.
- **Dependencies**: Requires `scapy`, `dnspython`, `hostapd`, `dnsmasq`, `aircrack-ng`.
- **Root**: Requires `sudo` for monitor mode and server operations.

## Disclaimer
**Personal Use Only**: NetPhantom is for learning on networks/systems you own or have permission to test. Unauthorized use is illegal and may lead to legal consequences, disruptions, or ethical issues. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM with Wi-Fi adapter).
- Secure outputs (`netphantom.log`, `netphantom-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate networks without permission.
- Sharing sensitive output files.
- Production environments to prevent disruptions.

## Limitations
- CLI-focused; lacks **Ghost Phisher**’s Qt GUI.
- Basic DNS spoofing; extend with **DNSTwist**-like mappings.
- Requires monitor-mode-capable adapter, unlike **WebSentry**.
- No Metasploit integration; focus on phishing basics.

## Tips
- Create advanced phishing pages with **WebSentry** findings.
- Verify interface (`iwconfig wlan0`).
- Use Wireshark to monitor traffic.
- Test mitigations (e.g., secure Wi-Fi, input validation).
- Combine with **WiFiCrush** for handshake capture or **SQLStrike** for backend testing.

## License
For personal educational use; no formal license. Use responsibly.