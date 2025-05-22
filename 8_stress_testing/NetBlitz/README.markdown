# NetBlitz

## Description
NetBlitz is a Python-based tool designed for ethical security testing in your private lab (Ubuntu 24.04, home network). It simulates high-rate packet floods across TCP, UDP, and ICMP protocols to stress-test network devices (e.g., routers, firewalls, IDS) and evaluate their resilience against overload conditions. The tool features a CLI interface, SQLite logging, JSON output, and multi-threading, integrating with your tools like **NetSentry**, **NatPiercer**, **WiFiCrush**, **IdentityForge**, **IAXStorm**, **SlowStrike**, **SSLBlaze**, and **RTPStorm**.

**Important**: Use NetBlitz only on devices and networks you own or have explicit permission to test. Unauthorized packet flooding is illegal and may lead to legal consequences, network disruptions, or ethical issues. This tool is restricted to your lab for responsible use. Modern network devices may mitigate floods with rate limiting or intrusion detection systems.

## Features
- **Multi-Protocol Flooding**: Sends TCP, UDP, or ICMP packets to simulate network stress.
- **Output Formats**: SQLite database, JSON, and text logs.
- **Multi-Threading**: Efficient packet sending with configurable threads.
- **Quiet Mode**: Minimizes terminal output.
- **Logging**: Saves logs to `netblitz.log` and results to `netblitz-output/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Network access to target device.
   - Root privileges (`sudo`) for raw socket operations.
   - Private network/lab you control.
2. **Install Dependencies**:
   - Save `setup_netblitz.sh` to a directory (e.g., `/home/user/netblitz/`).
   - Make executable and run:
     ```bash
     chmod +x setup_netblitz.sh
     ./setup_netblitz.sh
     ```
   - Installs Python, pip, and `scapy`.
3. Save `netblitz.py` to the same directory.
4. Verify:
   ```bash
   sudo python3 netblitz.py --help
   ```

## Usage
NetBlitz simulates packet floods in a controlled lab setting to test network device resilience. Below are examples and expected outcomes.

### Basic Commands
Simulate a TCP flood:
```bash
sudo python3 netblitz.py -t 192.168.1.100 -p 80 -P TCP -r 100 -d 10
```

Run with UDP and custom port:
```bash
sudo python3 netblitz.py -t 192.168.1.100 -p 53 -P UDP -r 200 -d 15 -T 10
```

Run with ICMP in quiet mode:
```bash
sudo python3 netblitz.py -t 192.168.1.100 -P ICMP -r 100 -d 10 -q
```

### Options
- `-t, --target-ip`: Target IP address of network device (required).
- `-p, --target-port`: Target port (default: 80; ignored for ICMP).
- `-P, --protocol`: Protocol (TCP, UDP, ICMP; default: TCP).
- `-r, --packet-rate`: Packets per second per thread (default: 100).
- `-d, --duration`: Flood duration in seconds (default: 10).
- `-T, --threads`: Number of threads (default: 5).
- `-q, --quiet`: Log to file only.

### Features

#### Packet Flooding
- **Purpose**: Simulate flood attacks to test network device resilience.
- **Usage**:
  ```bash
  sudo python3 netblitz.py -t 192.168.1.100 -p 80 -P TCP -r 100 -d 10
  ```
- **Output**:
  ```
  2025-05-15 16:00:00 - INFO - Starting NetBlitz against 192.168.1.100:80 with TCP
  2025-05-15 16:00:10 - INFO - Sent 5000 TCP packets to 192.168.1.100:80
  ```
- **Result File** (`netblitz-output/blitz_20250515_160000.txt`):
  ```
  === NetBlitz Results ===
  Timestamp: 2025-05-15 16:00:10
  [2025-05-15 16:00:10] Sent 5000 TCP packets to 192.168.1.100:80, Target=192.168.1.100:80, Protocol=TCP, Rate=100, Packets=5000
  ```
- **JSON File** (`netblitz-output/blitz_20250515_160000.json`):
  ```json
  {
    "target_ip": "192.168.1.100",
    "target_port": 80,
    "protocol": "TCP",
    "packet_rate": 100,
    "duration": 10,
    "total_packets_sent": 5000,
    "actions": [
      {
        "target_ip": "192.168.1.100",
        "target_port": 80,
        "protocol": "TCP",
        "packet_rate": 100,
        "packets_sent": 5000,
        "status": "Sent 5000 TCP packets to 192.168.1.100:80",
        "timestamp": "2025-05-15 16:00:10"
      }
    ],
    "timestamp": "2025-05-15 16:00:10"
  }
  ```
- **Tips**: Use **NetSentry** to monitor flood traffic; test with a router or firewall in your lab.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  sudo python3 netblitz.py -t 192.168.1.100 -p 80 -P TCP -r 100 -d 10 -q
  ```
- **Tips**: Monitor `netblitz.log` with `tail -f netblitz.log`.

### Workflow
1. Set up lab (VM with network device, e.g., router/firewall, network access).
2. Install dependencies:
   ```bash
   ./setup_netblitz.sh
   ```
3. Run NetBlitz:
   ```bash
   sudo python3 netblitz.py -t 192.168.1.100 -p 80 -P TCP -r 100 -d 10
   ```
4. Monitor output in terminal or `netblitz.log`.
5. Check results in `netblitz-output/` (text, JSON, SQLite).
6. Stop with `Ctrl+C`; secure outputs (`rm -rf netblitz-output/*`).

## Output
- **Logs**: `netblitz.log`, e.g.:
  ```
  2025-05-15 16:00:00 - INFO - Starting NetBlitz against 192.168.1.100:80 with TCP
  2025-05-15 16:00:10 - INFO - Sent 5000 TCP packets to 192.168.1.100:80
  ```
- **Results**: `netblitz-output/blitz_<timestamp>.txt` and `.json`.
- **Database**: `netblitz-output/netblitz.db` (SQLite).

## Notes
- **Environment**: Use on authorized devices/networks in your lab.
- **Impact**: Flooding may disrupt network services; modern devices may mitigate with rate limiting or IDS.
- **Ethics**: Avoid unauthorized flooding to prevent legal/security issues.
- **Dependencies**: Requires `scapy` for packet crafting; root for raw sockets.
- **Root**: Requires `sudo` for packet sending.
- **Sources**: Built for network stress testing, leveraging concepts from Kali Linux toolsets and T50 functionality.[](https://sectechno.com/t50-faster-network-stress-tool/)[](https://github.com/jweyrich/t50)

## Disclaimer
**Personal Use Only**: NetBlitz is for learning on devices/networks you own or have permission to test. Unauthorized flood attacks are illegal and may lead to legal consequences or ethical issues. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM with isolated network).
- Secure outputs (`netblitz.log`, `netblitz-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate networks without permission.
- Sharing sensitive output files.
- Production environments to prevent disruptions.

## Limitations
- **Flood Scope**: Sends basic TCP, UDP, ICMP packets; lacks advanced protocol support (e.g., GRE, OSPF).
- **Mitigation**: Devices with rate limiting or IDS may block floods.
- **Interface**: CLI-only; lacks GUI or TUI.
- **Protocol**: Limited to TCP, UDP, ICMP; no support for routing protocols.

## Tips
- Test with a router, firewall, or IDS in your lab to simulate real network conditions.
- Use Wireshark or **NetSentry** to monitor flood packets (filter: `tcp`, `udp`, `icmp`).
- Combine with **WiFiCrush** for network access or **NatPiercer** for tunneling.
- Adjust packet rate and duration to avoid overwhelming lab resources.
- Check device logs to assess attack impact; configure QoS to mitigate floods.

## License
For personal educational use; no formal license. Use responsibly.