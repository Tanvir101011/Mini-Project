# CredSnare

## Description
CredSnare is a Python-based Wi-Fi phishing tool for credential harvesting, inspired by **Fang**. It emulates a Wi-Fi access point, deploys a Flask-based phishing page, and captures credentials, designed for ethical security testing in your private lab (Ubuntu 24.04, home network). Built with `Flask`, `dnspython`, and SQLite, it supports multi-threading, JSON output, and a CLI interface, integrating with your tools like **NetPhantom**, **WiFiCrush**, and **WebSentry**.

**Important**: Use CredSnare only on networks/systems you own or have explicit permission to test. Unauthorized use is illegal and may lead to legal consequences, network disruptions, or ethical issues. The tool is restricted to your lab for responsible use.

## Features
- **Fake AP**: Emulates Wi-Fi access points with customizable SSID.
- **Phishing Portal**: Serves a Flask-based captive portal for credential capture.
- **Credential Logging**: Stores credentials in SQLite and JSON.
- **DNS Spoofing**: Redirects traffic to the phishing portal (optional).
- **Multi-Threading**: Handles concurrent tasks efficiently.
- **JSON Output**: Saves results for parsing/automation.
- **Logging**: Saves logs to `credsnare.log` and results to `credsnare-output/`.
- **Quiet Mode**: Minimizes terminal output.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Wireless adapter supporting monitor mode (e.g., `wlan0`).
   - Root privileges (`sudo`) for monitor mode and packet handling.
   - Private network you control.
2. **Install Dependencies**:
   - Save `setup_credsnare.sh` to a directory (e.g., `/home/user/credsnare/`).
   - Make executable and run:
     ```bash
     chmod +x setup_credsnare.sh
     ./setup_credsnare.sh
     ```
   - Installs `flask`, `dnspython`, `hostapd`, `dnsmasq`, and `aircrack-ng`.
3. Save `credsnare.py` to the same directory.
4. Create a phishing template (`login.html`):
   ```bash
   echo '<!DOCTYPE html><html><body><h2>Login</h2><form method="POST"><input name="username" type="text" placeholder="Username"><input name="password" type="password" placeholder="Password"><input type="submit" value="Login"></form>{{ message|default("") }}</body></html>' > login.html
   ```
5. Verify:
   ```bash
   python3 credsnare.py --help
   ```

## Usage
CredSnare creates fake Wi-Fi APs and a phishing portal to capture credentials in a controlled lab setting. Below are examples and expected outcomes.

### Basic Commands
Start fake AP and phishing portal:
```bash
sudo python3 credsnare.py -i wlan0 -s FreeWiFi -p login.html
```

Enable DNS spoofing in quiet mode:
```bash
sudo python3 credsnare.py -i wlan0 -s FreeWiFi -p login.html --dns-spoof -T 5 -q
```

### Options
- `-i, --interface`: Wireless interface (required, e.g., `wlan0`).
- `-s, --ssid`: SSID for fake AP (required, e.g., `FreeWiFi`).
- `-p, --phishing-template`: Phishing template file (default: `login.html`).
- `--dns-spoof`: Enable DNS spoofing.
- `-T, --threads`: Number of threads (default: 5).
- `-q, --quiet`: Log to file only.

### Features

#### Fake Access Point
- **Purpose**: Emulate a Wi-Fi AP to attract clients.
- **Usage**:
  ```bash
  sudo python3 credsnare.py -i wlan0 -s FreeWiFi -p login.html
  ```
- **Output**:
  ```
  2025-05-15 14:00:00 - INFO - Starting CredSnare with SSID: FreeWiFi
  2025-05-15 14:00:02 - INFO - Fake AP started
  ```
- **Tips**: Use **WiFiCrush** to capture handshakes for WPA testing.

#### Credential Capture
- **Purpose**: Log credentials via phishing portal.
- **Usage**:
  ```bash
  sudo python3 credsnare.py -i wlan0 -s FreeWiFi -p login.html
  ```
- **Output**:
  ```
  2025-05-15 14:00:05 - INFO - Credential captured: Username=test, Password=secret
  ```
- **Result File** (`credsnare-output/snare_FreeWiFi_20250515_140000.txt`):
  ```
  [2025-05-15 14:00:05] Username: test, Password: secret
  [2025-05-15 14:00:06] Snare run complete
  ```
- **JSON File** (`credsnare-output/snare_FreeWiFi_20250515_140000.json`):
  ```json
  {
    "ssid": "FreeWiFi",
    "interface": "wlan0",
    "credentials": [
      {
        "username": "test",
        "password": "secret",
        "timestamp": "2025-05-15 14:00:05"
      }
    ],
    "timestamp": "2025-05-15 14:00:06"
  }
  ```
- **Tips**: Use **WordForge** to generate phishing page templates.

#### DNS Spoofing
- **Purpose**: Redirect traffic to the phishing portal.
- **Usage**:
  ```bash
  sudo python3 credsnare.py -i wlan0 -s FreeWiFi -p login.html --dns-spoof
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
  sudo python3 credsnare.py -i wlan0 -s FreeWiFi -p login.html -q
  ```
- **Tips**: Monitor `credsnare.log` with `tail -f credsnare.log`.

### Workflow
1. Set up lab (VM with Wi-Fi adapter in monitor mode).
2. Install dependencies:
   ```bash
   ./setup_credsnare.sh
   ```
3. Create `login.html` phishing template.
4. Run CredSnare:
   ```bash
   sudo python3 credsnare.py -i wlan0 -s FreeWiFi -p login.html --dns-spoof
   ```
5. Connect a test device to `FreeWiFi`; submit credentials.
6. Check logs (`credsnare.log`) and results (`credsnare-output/`).
7. Stop with `Ctrl+C`; secure outputs (`rm -rf credsnare-output/*`).

## Output
- **Logs**: `credsnare.log`, e.g.:
  ```
  2025-05-15 14:00:00 - INFO - Starting CredSnare with SSID: FreeWiFi
  2025-05-15 14:00:05 - INFO - Credential captured: Username=test, Password=secret
  ```
- **Results**: `credsnare-output/snare_<ssid>_<timestamp>.txt` and `.json`.
- **Database**: `credsnare-output/credsnare.db` (SQLite).

## Notes
- **Environment**: Use on authorized networks in your lab.
- **Impact**: Fake APs may disrupt networks; test with caution.
- **Ethics**: Avoid unauthorized use to prevent legal/security issues.
- **Dependencies**: Requires `flask`, `dnspython`, `hostapd`, `dnsmasq`, `aircrack-ng`.
- **Root**: Requires `sudo` for monitor mode and server operations.

## Disclaimer
**Personal Use Only**: CredSnare is for learning on networks/systems you own or have permission to test. Unauthorized use is illegal and may lead to legal consequences, disruptions, or ethical issues. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM with Wi-Fi adapter).
- Secure outputs (`credsnare.log`, `credsnare-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate networks without permission.
- Sharing sensitive output files.
- Production environments to prevent disruptions.

## Limitations
- CLI-focused; lacks a GUI, unlike some phishing tools.
- Basic DNS spoofing; extend with **DNSTwist**-like mappings.
- Requires monitor-mode-capable adapter, similar to **WiFiCrush**.
- No advanced portal customization; focus on basic phishing.

## Tips
- Create advanced phishing templates with **WebSentry** findings.
- Verify interface (`iwconfig wlan0`).
- Use Wireshark to monitor traffic.
- Test mitigations (e.g., secure Wi-Fi, input validation).
- Combine with **WiFiCrush** for handshake capture or **SQLStrike** for backend testing.

## License
For personal educational use; no formal license. Use responsibly.