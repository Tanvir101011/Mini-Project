# WiFiCrush

## Description
WiFiCrush is a Python-based tool for auditing Wi-Fi security in your private lab, inspired by **Aircrack-ng**. It captures WPA/WPA2 handshake packets and performs dictionary-based attacks to crack pre-shared keys (PSKs), using tools like `scapy` for packet analysis. Designed for educational purposes, it supports multi-threading, JSON output, and a CLI interface, integrating with your lab tools like **WordForge**, **SQLStrike**, and **WebSentry** (Ubuntu 24.04, home network).

**Important**: Use WiFiCrush only on networks you own or have explicit permission to test. Unauthorized Wi-Fi testing is illegal and may lead to legal consequences, network disruptions, or ethical issues. The tool is restricted to your lab to ensure responsible use.

## Features
- **Packet Capture**: Captures WPA/WPA2 handshakes using monitor mode.
- **Key Cracking**: Performs dictionary attacks to crack PSKs.
- **Multi-Threading**: Speeds up cracking with configurable threads.
- **JSON Output**: Saves results for parsing/automation.
- **Configurable**: Supports interface, BSSID, wordlist, and capture file inputs.
- **Logging**: Saves logs to `wificrush.log` and results to `wificrush-output/`.
- **Quiet Mode**: Minimizes terminal output.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Wireless adapter supporting monitor mode (e.g., `wlan0`).
   - Root privileges (`sudo`) for monitor mode and packet capture.
   - Private network you control.
2. **Install Dependencies**:
   - Save `setup_wificrush.sh` to a directory (e.g., `/home/user/wificrush/`).
   - Make executable and run:
     ```bash
     chmod +x setup_wificrush.sh
     ./setup_wificrush.sh
     ```
   - Installs `scapy`, `aircrack-ng`, and default wordlists.
3. Save `wificrush.py` to the same directory.
4. Verify:
   ```bash
   python3 wificrush.py --help
   ```

## Usage
WiFiCrush captures Wi-Fi handshakes and attempts to crack WPA/WPA2 keys. Below are examples and expected outcomes.

### Basic Commands
Capture handshake and crack key:
```bash
sudo python3 wificrush.py -i wlan0 -b 00:14:22:01:23:45 -w passwords.txt -T 5
```

Use existing capture file:
```bash
sudo python3 wificrush.py -i wlan0 -b 00:14:22:01:23:45 -w passwords.txt -c capture.pcap -q
```

### Options
- `-i, --interface`: Wireless interface (required, e.g., `wlan0`).
- `-b, --bssid`: Target BSSID (required, e.g., `00:14:22:01:23:45`).
- `-w, --wordlist`: Wordlist file (default: `/usr/share/wordlists/passwords.txt`).
- `-c, --capture-file`: Existing capture file with WPA handshake.
- `-T, --threads`: Number of threads (default: 5).
- `-q, --quiet`: Log to file only.

### Features

#### Packet Capture
- **Purpose**: Capture WPA/WPA2 handshake packets.
- **Usage**:
  ```bash
  sudo python3 wificrush.py -i wlan0 -b 00:14:22:01:23:45 -w passwords.txt
  ```
- **Output**:
  ```
  2025-05-15 14:30:00 - INFO - Starting WiFiCrush on interface wlan0, BSSID: 00:14:22:01:23:45
  2025-05-15 14:30:05 - INFO - WPA handshake packet captured
  ```
- **Tips**: Use **WordForge** to generate wordlists (`python3 wordforge.py -m 8 -M 12 -c abc123`).

#### Key Cracking
- **Purpose**: Crack WPA/WPA2 PSK using a dictionary.
- **Usage**:
  ```bash
  sudo python3 wificrush.py -i wlan0 -b 00:14:22:01:23:45 -w passwords.txt -T 5
  ```
- **Output**:
  ```
  2025-05-15 14:30:10 - INFO - WPA key found: mysecretpass
  ```
- **Result File** (`wificrush-output/crack_001422012345_20250515_143000.txt`):
  ```
  [2025-05-15 14:30:10] WPA key found: mysecretpass
  [2025-05-15 14:30:11] Crack attempt complete
  ```
- **JSON File** (`wificrush-output/crack_001422012345_20250515_143000.json`):
  ```json
  {
    "interface": "wlan0",
    "bssid": "00:14:22:01:23:45",
    "capture_file": "wificrush-output/capture_20250515_143000.pcap",
    "results": [
      {"password": "mysecretpass", "status": "success", "message": "WPA key found: mysecretpass"},
      {"password": "wrongpass", "status": "failed", "message": ""}
    ],
    "timestamp": "2025-05-15 14:30:11"
  }
  ```
- **Tips**: Verify with `airodump-ng wlan0` to find BSSID.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  sudo python3 wificrush.py -i wlan0 -b 00:14:22:01:23:45 -w passwords.txt -q
  ```
- **Tips**: Check `wificrush.log` with `tail -f wificrush.log`.

### Workflow
1. Set up lab (VM with Wi-Fi adapter in monitor mode).
2. Install dependencies:
   ```bash
   ./setup_wificrush.sh
   ```
3. Identify target BSSID (`sudo airodump-ng wlan0`).
4. Prepare wordlist (e.g., `echo "mysecretpass" > passwords.txt` or use **WordForge**).
5. Run WiFiCrush:
   ```bash
   sudo python3 wificrush.py -i wlan0 -b 00:14:22:01:23:45 -w passwords.txt -T 5
   ```
6. Check logs (`wificrush.log`) and results (`wificrush-output/`).
7. Stop with `Ctrl+C`; secure outputs (`rm -rf wificrush-output/*`).

## Output
- **Logs**: `wificrush.log`, e.g.:
  ```
  2025-05-15 14:30:00 - INFO - Starting WiFiCrush on interface wlan0
  2025-05-15 14:30:10 - INFO - WPA key found: mysecretpass
  ```
- **Results**: `wificrush-output/crack_<bssid>_<timestamp>.txt` and `.json`.
- **Capture**: `wificrush-output/capture_<timestamp>.pcap`.

## Notes
- **Environment**: Use on authorized Wi-Fi networks in your lab.
- **Impact**: Packet capture may disrupt networks; test with caution.
- **Ethics**: Avoid unauthorized use to prevent legal/security issues.
- **Dependencies**: Requires `scapy`, `aircrack-ng`, and monitor mode support.
- **Root**: Requires `sudo` for monitor mode and packet capture.

## Disclaimer
**Personal Use Only**: WiFiCrush is for learning on networks you own or have permission to test. Unauthorized use is illegal and may lead to legal consequences, disruptions, or ethical issues. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM with Wi-Fi adapter).
- Secure outputs (`wificrush.log`, `wificrush-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate networks without permission.
- Sharing sensitive capture files or results.
- Production environments to prevent disruptions.

## Limitations
- Supports WPA/WPA2; **Aircrack-ng** also handles WEP and advanced attacks.
- Simplified handshake extraction; requires manual SSID input.
- Depends on wireless adapter compatibility and monitor mode.
- No GUI; CLI-focused, unlike **Aircrack-ng**’s companion tools.

## Tips
- Set up a test AP (`sudo hostapd hostapd.conf`).
- Verify interface (`iwconfig wlan0`).
- Use Wireshark to analyze `.pcap` files.
- Test mitigations (e.g., strong PSKs, WPA3).
- Combine with **WordForge** for wordlists or **WebSentry** for web testing.

## License
For personal educational use; no formal license. Use responsibly.