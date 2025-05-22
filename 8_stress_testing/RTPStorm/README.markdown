# RTPStorm

## Description
RTPStorm is a Python-based tool designed for ethical security testing in your private lab (Ubuntu 24.04, home network). It simulates high-rate RTP packet floods to stress-test VoIP or streaming servers (e.g., Asterisk, FreeSWITCH) and evaluate their resilience against denial-of-service attacks. The tool features a CLI interface, SQLite logging, JSON output, and multi-threading, integrating with your tools like **NetSentry**, **NatPiercer**, **WiFiCrush**, **IdentityForge**, **SlowStrike**, and **SSLBlaze**.

**Important**: Use RTPStorm only on servers and networks you own or have explicit permission to test. Unauthorized flood attacks are illegal and may lead to legal consequences, network disruptions, or ethical issues. This tool is restricted to your lab for responsible use. Modern RTP servers may mitigate floods with rate limiting or intrusion detection systems.

## Features
- **RTP Packet Flooding**: Sends high-rate RTP packets to simulate flood attacks.
- **Output Formats**: SQLite database, JSON, and text logs.
- **Multi-Threading**: Efficient packet sending with configurable threads.
- **Quiet Mode**: Minimizes terminal output.
- **Logging**: Saves logs to `rtpstorm.log` and results to `rtpstorm-output/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Network access to target RTP server.
   - Root privileges (`sudo`) for raw socket operations.
   - Private network/lab you control.
2. **Install Dependencies**:
   - Save `setup_rtpstorm.sh` to a directory (e.g., `/home/user/rtpstorm/`).
   - Make executable and run:
     ```bash
     chmod +x setup_rtpstorm.sh
     ./setup_rtpstorm.sh
     ```
   - Installs Python, pip, and `scapy`.
3. Save `rtpstorm.py` to the same directory.
4. Verify:
   ```bash
   sudo python3 rtpstorm.py --help
   ```

## Usage
RTPStorm simulates RTP flood attacks in a controlled lab setting to test VoIP or streaming server resilience. Below are examples and expected outcomes.

### Basic Commands
Simulate an RTP flood:
```bash
sudo python3 rtpstorm.py -t 192.168.1.100 -p 10000 -r 100 -d 10
```

Run with custom port and threads:
```bash
sudo python3 rtpstorm.py -t 192.168.1.100 -p 5060 -r 200 -d 15 -T 10
```

Run in quiet mode:
```bash
sudo python3 rtpstorm.py -t 192.168.1.100 -p 10000 -r 100 -d 10 -q
```

### Options
- `-t, --target-ip`: Target IP address of RTP server (required).
- `-p, --target-port`: Target port (default: 10000).
- `-r, --packet-rate`: Packets per second per thread (default: 100).
- `-d, --duration`: Flood duration in seconds (default: 10).
- `-T, --threads`: Number of threads (default: 5).
- `-q, --quiet`: Log to file only.

### Features

#### RTP Flooding
- **Purpose**: Simulate flood attacks to test RTP server resilience.
- **Usage**:
  ```bash
  sudo python3 rtpstorm.py -t 192.168.1.100 -p 10000 -r 100 -d 10
  ```
- **Output**:
  ```
  2025-05-15 16:00:00 - INFO - Starting RTPStorm against 192.168.1.100:10000
  2025-05-15 16:00:10 - INFO - Sent 5000 packets to 192.168.1.100:10000
  ```
- **Result File** (`rtpstorm-output/storm_20250515_160000.txt`):
  ```
  === RTPStorm Results ===
  Timestamp: 2025-05-15 16:00:10
  [2025-05-15 16:00:10] Sent 5000 packets to 192.168.1.100:10000, Target=192.168.1.100:10000, Rate=100, Packets=5000
  ```
- **JSON File** (`rtpstorm-output/storm_20250515_160000.json`):
  ```json
  {
    "target_ip": "192.168.1.100",
    "target_port": 10000,
    "packet_rate": 100,
    "duration": 10,
    "total_packets_sent": 5000,
    "actions": [
      {
        "target_ip": "192.168.1.100",
        "target_port": 10000,
        "packet_rate": 100,
        "packets_sent": 5000,
        "status": "Sent 5000 packets to 192.168.1.100:10000",
        "timestamp": "2025-05-15 16:00:10"
      }
    ],
    "timestamp": "2025-05-15 16:00:10"
  }
  ```
- **Tips**: Use **NetSentry** to monitor flood traffic; test with an Asterisk or FreeSWITCH server in your lab.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  sudo python3 rtpstorm.py -t 192.168.1.100 -p 10000 -r 100 -d 10 -q
  ```
- **Tips**: Monitor `rtpstorm.log` with `tail -f rtpstorm.log`.

### Workflow
1. Set up lab (VM with RTP server, e.g., Asterisk/FreeSWITCH, network access).
2. Install dependencies:
   ```bash
   ./setup_rtpstorm.sh
   ```
3. Run RTPStorm:
   ```bash
   sudo python3 rtpstorm.py -t 192.168.1.100 -p 10000 -r 100 -d 10
   ```
4. Monitor output in terminal or `rtpstorm.log`.
5. Check results in `rtpstorm-output/` (text, JSON, SQLite).
6. Stop with `Ctrl+C`; secure outputs (`rm -rf rtpstorm-output/*`).

## Output
- **Logs**: `rtpstorm.log`, e.g.:
  ```
  2025-05-15 16:00:00 - INFO - Starting RTPStorm against 192.168.1.100:10000
  2025-05-15 16:00:10 - INFO - Sent 5000 packets to 192.168.1.100:10000
  ```
- **Results**: `rtpstorm-output/storm_<timestamp>.txt` and `.json`.
- **Database**: `rtpstorm-output/rtpstorm.db` (SQLite).

## Notes
- **Environment**: Use on authorized servers/networks in your lab.
- **Impact**: Flooding may disrupt VoIP/streaming services; modern servers may mitigate with rate limiting or IDS.
- **Ethics**: Avoid unauthorized flooding to prevent legal/security issues.
- **Dependencies**: Requires `scapy` for packet crafting; root for raw sockets.
- **Root**: Requires `sudo` for packet sending.
- **Sources**: Built for RTP testing, leveraging VoIP security concepts and Kali Linux toolsets.

## Disclaimer
**Personal Use Only**: RTPStorm is for learning on servers/networks you own or have permission to test. Unauthorized flood attacks are illegal and may lead to legal consequences or ethical issues. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM with isolated network).
- Secure outputs (`rtpstorm.log`, `rtpstorm-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate networks without permission.
- Sharing sensitive output files.
- Production environments to prevent disruptions.

## Limitations
- **Flood Scope**: Sends simplified RTP packets; lacks full protocol handshake simulation.
- **Mitigation**: Servers with rate limiting or IDS may block floods.
- **Interface**: CLI-only; lacks GUI or TUI.
- **Protocol**: Focuses on RTP; no support for other VoIP protocols (e.g., SIP).

## Tips
- Test with an Asterisk or FreeSWITCH server in your lab to simulate real RTP traffic.
- Use Wireshark or **NetSentry** to monitor flood packets (filter: `rtp`).
- Combine with **WiFiCrush** for network access or **NatPiercer** for tunneling.
- Adjust packet rate and duration to avoid overwhelming lab resources.
- Check server logs to assess attack impact; configure QoS to mitigate floods.

## License
For personal educational use; no formal license. Use responsibly.