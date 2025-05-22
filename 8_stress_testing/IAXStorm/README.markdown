# IAXStorm

## Description
IAXStorm is a Python-based tool designed for ethical security testing in your private lab (Ubuntu 24.04, home network). It simulates high-rate IAX2 packet floods to stress-test IAX2 servers (e.g., Asterisk), helping evaluate VoIP infrastructure resilience against flood attacks. The tool features a CLI interface, SQLite logging, JSON output, and multi-threading, integrating with your tools like **NetSentry**, **NatPiercer**, **WiFiCrush**, and **IdentityForge**.

**Important**: Use IAXStorm only on servers and networks you own or have explicit permission to test. Unauthorized flood attacks are illegal and may lead to legal consequences, network disruptions, or ethical issues. This tool is restricted to your lab for responsible use. Modern VoIP servers may mitigate floods with rate limiting or intrusion detection.

## Features
- **IAX2 Packet Flooding**: Sends high-rate IAX2 packets to simulate flood attacks.
- **Output Formats**: SQLite database, JSON, and text logs.
- **Multi-Threading**: Efficient packet sending with configurable threads.
- **Quiet Mode**: Minimizes terminal output.
- **Logging**: Saves logs to `iaxstorm.log` and results to `iaxstorm-output/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Network access to target IAX2 server.
   - Root privileges (`sudo`) for raw socket operations.
   - Private network/lab you control.
2. **Install Dependencies**:
   - Save `setup_iaxstorm.sh` to a directory (e.g., `/home/user/iaxstorm/`).
   - Make executable and run:
     ```bash
     chmod +x setup_iaxstorm.sh
     ./setup_iaxstorm.sh
     ```
   - Installs Python, pip, and `scapy`.
3. Save `iaxstorm.py` to the same directory.
4. Verify:
   ```bash
   sudo python3 iaxstorm.py --help
   ```

## Usage
IAXStorm simulates IAX2 flood attacks in a controlled lab setting to test VoIP server resilience. Below are examples and expected outcomes.

### Basic Commands
Simulate an IAX2 flood:
```bash
sudo python3 iaxstorm.py -t 192.168.1.100 -r 100 -d 10
```

Run with custom port and threads:
```bash
sudo python3 iaxstorm.py -t 192.168.1.100 -p 4569 -r 200 -d 15 -T 10
```

Run in quiet mode:
```bash
sudo python3 iaxstorm.py -t 192.168.1.100 -r 100 -d 10 -q
```

### Options
- `-t, --target-ip`: Target IP address of IAX2 server (required).
- `-p, --target-port`: Target port (default: 4569).
- `-r, --packet-rate`: Packets per second per thread (default: 100).
- `-d, --duration`: Flood duration in seconds (default: 10).
- `-T, --threads`: Number of threads (default: 5).
- `-q, --quiet`: Log to file only.

### Features

#### IAX2 Flooding
- **Purpose**: Simulate flood attacks to test IAX2 server resilience.
- **Usage**:
  ```bash
  sudo python3 iaxstorm.py -t 192.168.1.100 -r 100 -d 10
  ```
- **Output**:
  ```
  2025-05-15 16:00:00 - INFO - Starting IAXStorm against 192.168.1.100:4569
  2025-05-15 16:00:10 - INFO - Sent 5000 packets to 192.168.1.100:4569
  ```
- **Result File** (`iaxstorm-output/storm_20250515_160000.txt`):
  ```
  === IAXStorm Results ===
  Timestamp: 2025-05-15 16:00:10
  [2025-05-15 16:00:10] Sent 5000 packets to 192.168.1.100:4569, Target=192.168.1.100:4569, Rate=100, Packets=5000
  ```
- **JSON File** (`iaxstorm-output/storm_20250515_160000.json`):
  ```json
  {
    "target_ip": "192.168.1.100",
    "target_port": 4569,
    "packet_rate": 100,
    "duration": 10,
    "total_packets_sent": 5000,
    "actions": [
      {
        "target_ip": "192.168.1.100",
        "target_port": 4569,
        "packet_rate": 100,
        "packets_sent": 5000,
        "status": "Sent 5000 packets to 192.168.1.100:4569",
        "timestamp": "2025-05-15 16:00:10"
      }
    ],
    "timestamp": "2025-05-15 16:00:10"
  }
  ```
- **Tips**: Use **NetSentry** to monitor flood traffic; test with an Asterisk server in your lab.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  sudo python3 iaxstorm.py -t 192.168.1.100 -r 100 -d 10 -q
  ```
- **Tips**: Monitor `iaxstorm.log` with `tail -f iaxstorm.log`.

### Workflow
1. Set up lab (VM with Asterisk server, network access).
2. Install dependencies:
   ```bash
   ./setup_iaxstorm.sh
   ```
3. Run IAXStorm:
   ```bash
   sudo python3 iaxstorm.py -t 192.168.1.100 -r 100 -d 10
   ```
4. Monitor output in terminal or `iaxstorm.log`.
5. Check results in `iaxstorm-output/` (text, JSON, SQLite).
6. Stop with `Ctrl+C`; secure outputs (`rm -rf iaxstorm-output/*`).

## Output
- **Logs**: `iaxstorm.log`, e.g.:
  ```
  2025-05-15 16:00:00 - INFO - Starting IAXStorm against 192.168.1.100:4569
  2025-05-15 16:00:10 - INFO - Sent 5000 packets to 192.168.1.100:4569
  ```
- **Results**: `iaxstorm-output/storm_<timestamp>.txt` and `.json`.
- **Database**: `iaxstorm-output/iaxstorm.db` (SQLite).

## Notes
- **Environment**: Use on authorized servers/networks in your lab.
- **Impact**: Flooding may disrupt VoIP services; modern servers may mitigate with rate limiting.
- **Ethics**: Avoid unauthorized flooding to prevent legal/security issues.
- **Dependencies**: Requires `scapy` for packet crafting; root for raw sockets.
- **Root**: Requires `sudo` for packet sending.
- **Sources**: Built for IAX2 testing, leveraging VoIP security concepts and Kali Linux toolsets.

## Disclaimer
**Personal Use Only**: IAXStorm is for learning on servers/networks you own or have permission to test. Unauthorized flood attacks are illegal and may lead to legal consequences or ethical issues. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM with isolated network).
- Secure outputs (`iaxstorm.log`, `iaxstorm-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate networks without permission.
- Sharing sensitive output files.
- Production environments to prevent disruptions.

## Limitations
- **Flood Scope**: Sends simplified IAX2 packets; lacks full protocol handshake simulation.
- **Mitigation**: Servers with rate limiting or IDS may block floods.
- **Interface**: CLI-only; lacks GUI or TUI.
- **Protocol**: Focuses on IAX2; no SIP or other VoIP protocol support.

## Tips
- Test with an Asterisk server in your lab to simulate real IAX2 traffic.
- Use Wireshark or **NetSentry** to monitor flood packets.
- Combine with **WiFiCrush** for network access or **NatPiercer** for tunneling.
- Adjust packet rate and duration to avoid overwhelming lab resources.
- Report vulnerabilities to server admins.

## License
For personal educational use; no formal license. Use responsibly.