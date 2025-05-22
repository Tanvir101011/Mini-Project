# NetSentry

## Description
NetSentry is a Python-based wireless network and device scanner inspired by **Kismet**, designed for detecting Wi-Fi networks, capturing packets, and tracking devices in your private lab (Ubuntu 24.04, home network). Built with `scapy` and SQLite, it features a CLI interface, JSON output, and multi-threading, integrating with your tools like **WiFiCrush**, **SignalSnare**, and **xscan**. It scans for access points, logs network details (SSID, BSSID, channel, encryption), and tracks client devices, with optional packet capture to PCAP files.

**Important**: Use NetSentry only on networks you own or have explicit permission to monitor. Unauthorized scanning or packet capture is illegal and may lead to legal consequences, network disruptions, or ethical issues. This tool is restricted to your lab for responsible use.

## Features
- **Network Detection**: Scans for Wi-Fi networks (SSID, BSSID, channel, signal, encryption).
- **Device Tracking**: Detects client devices (MAC, associated BSSID, signal).
- **Packet Capture**: Optionally saves packets to PCAP files.
- **Output Formats**: SQLite database, JSON, and text logs.
- **Multi-Threading**: Efficient scanning and processing.
- **Quiet Mode**: Minimizes terminal output.
- **Logging**: Saves logs to `netsentry.log` and results to `netsentry-output/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Wireless adapter supporting monitor mode (e.g., `wlan0`).
   - Root privileges (`sudo`) for monitor mode and packet capture.
   - Private network you control.
2. **Install Dependencies**:
   - Save `setup_netsentry.sh` to a directory (e.g., `/home/user/netsentry/`).
   - Make executable and run:
     ```bash
     chmod +x setup_netsentry.sh
     ./setup_netsentry.sh
     ```
   - Installs `scapy`, `aircrack-ng`, and required tools.
3. Save `netsentry.py` to the same directory.
4. Verify:
   ```bash
   python3 netsentry.py --help
   ```

## Usage
NetSentry scans Wi-Fi networks and devices in a controlled lab setting, logging details and optionally capturing packets. Below are examples and expected outcomes.

### Basic Commands
Scan all channels:
```bash
sudo python3 netsentry.py -i wlan0
```

Scan a specific channel with packet capture:
```bash
sudo python3 netsentry.py -i wlan0 -c 6 --capture --min-power -80
```

Run in quiet mode:
```bash
sudo python3 netsentry.py -i wlan0 --capture -q
```

### Options
- `-i, --interface`: Wireless interface (required, e.g., `wlan0`).
- `-c, --channel`: Channel to scan (default: all).
- `--min-power`: Minimum signal strength in dBm (default: -100).
- `--capture`: Capture packets to PCAP file.
- `-T, --threads`: Number of threads (default: 5).
- `-q, --quiet`: Log to file only.

### Features

#### Network Detection
- **Purpose**: Discover Wi-Fi networks and their details.
- **Usage**:
  ```bash
  sudo python3 netsentry.py -i wlan0
  ```
- **Output**:
  ```
  2025-05-15 14:00:00 - INFO - Starting NetSentry
  2025-05-15 14:00:02 - INFO - Network: SSID=MyWiFi, BSSID=00:14:22:01:23:45, Channel=6, Signal=-50dBm
  ```
- **Result File** (`netsentry-output/sentry_20250515_140000.txt`):
  ```
  === NetSentry Results ===
  Timestamp: 2025-05-15 14:00:02
  Networks:
  SSID: MyWiFi, BSSID: 00:14:22:01:23:45, Channel: 6, Signal: -50dBm, Encryption: WPA2, Packets: 10
  ```
- **JSON File** (`netsentry-output/sentry_20250515_140000.json`):
  ```json
  {
    "interface": "wlan0mon",
    "channel": 0,
    "networks": [
      {
        "ssid": "MyWiFi",
        "bssid": "00:14:22:01:23:45",
        "channel": 6,
        "signal": -50,
        "encryption": "WPA2",
        "packets": 10,
        "timestamp": "2025-05-15 14:00:02"
      }
    ],
    "devices": [],
    "capture_file": null,
    "timestamp": "2025-05-15 14:00:02"
  }
  ```
- **Tips**: Use **WiFiCrush** to crack detected networks.

#### Device Tracking
- **Purpose**: Detect client devices and their associations.
- **Usage**:
  ```bash
  sudo python3 netsentry.py -i wlan0
  ```
- **Output**:
  ```
  2025-05-15 14:00:03 - INFO - Device: MAC=00:16:17:AB:CD:EF, Associated BSSID=00:14:22:01:23:45, Signal=-60dBm
  ```
- **Tips**: Combine with **NetPhantom** for phishing detected devices.

#### Packet Capture
- **Purpose**: Save packets to PCAP for analysis.
- **Usage**:
  ```bash
  sudo python3 netsentry.py -i wlan0 --capture
  ```
- **Output**:
  ```
  2025-05-15 14:00:04 - INFO - Capturing packets to netsentry-output/capture_20250515_140000.pcap
  ```
- **Tips**: Analyze PCAP files with Wireshark.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  sudo python3 netsentry.py -i wlan0 -q
  ```
- **Tips**: Monitor `netsentry.log` with `tail -f netsentry.log`.

### Workflow
1. Set up lab (VM with Wi-Fi adapter in monitor mode).
2. Install dependencies:
   ```bash
   ./setup_netsentry.sh
   ```
3. Run NetSentry:
   ```bash
   sudo python3 netsentry.py -i wlan0 --capture
   ```
4. Monitor output in terminal or `netsentry.log`.
5. Check results in `netsentry-output/` (text, JSON, SQLite, PCAP).
6. Stop with `Ctrl+C`; secure outputs (`rm -rf netsentry-output/*`).

## Output
- **Logs**: `netsentry.log`, e.g.:
  ```
  2025-05-15 14:00:00 - INFO - Starting NetSentry
  2025-05-15 14:00:02 - INFO - Network: SSID=MyWiFi, BSSID=00:14:22:01:23:45, Channel=6, Signal=-50dBm
  ```
- **Results**: `netsentry-output/sentry_<timestamp>.txt` and `.json`.
- **Database**: `netsentry-output/netsentry.db` (SQLite).
- **Capture**: `netsentry-output/capture_<timestamp>.pcap` (if enabled).

## Notes
- **Environment**: Use on authorized networks in your lab.
- **Impact**: Packet capture may disrupt networks; test with caution.
- **Ethics**: Avoid unauthorized scanning to prevent legal/security issues.
- **Dependencies**: Requires `scapy`, `aircrack-ng`.
- **Root**: Requires `sudo` for monitor mode and packet capture.
- **Sources**: Inspired by Kismet documentation () and Kali Linux tools ().

## Disclaimer
**Personal Use Only**: NetSentry is for learning on networks you own or have permission to monitor. Unauthorized scanning or packet capture is illegal and may lead to legal consequences or ethical issues. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM with Wi-Fi adapter).
- Secure outputs (`netsentry.log`, `netsentry-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate networks without permission.
- Sharing sensitive output files.
- Production environments to prevent disruptions.

## Limitations
- **Scope**: Focuses on Wi-Fi (802.11); lacks Kismet’s Bluetooth, Zigbee, or SDR support ().
- **Features**: Basic network/device detection; no intrusion detection or GPS integration.
- **Interface**: CLI-only; lacks Kismet’s web UI or TUI ().
- **Hardware**: Requires monitor-mode-capable adapter, similar to **WiFiCrush**.

## Tips
- Verify interface (`iwconfig wlan0`).
- Use Wireshark to analyze PCAP files.
- Combine with **WiFiCrush** for cracking or **SignalSnare** for signal decoding.
- Test mitigations (e.g., hidden SSIDs, MAC filtering).
- Extend with **xscan** for vulnerability scanning of detected devices.

## License
For personal educational use; no formal license. Use responsibly.