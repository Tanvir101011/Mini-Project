# NatPiercer

## Description
NatPiercer is a Python-based NAT traversal tool inspired by **pwnat**, designed to enable direct communication between clients and servers behind separate NATs without port forwarding, DMZ, or third-party services. Built for ethical security testing in your private lab (Ubuntu 24.04, home network), it uses UDP to tunnel TCP payloads, supporting basic NATs (RFC 1631). With a CLI interface, SQLite logging, JSON output, and multi-threading, it integrates with your tools like **NetSentry**, **SignalSnare**, and **WiFiCrush**.

**Important**: Use NatPiercer only on networks you own or have explicit permission to test. Unauthorized NAT traversal or tunneling is illegal and may lead to legal consequences, network disruptions, or ethical issues. This tool is restricted to your lab for responsible use. Modern NATs (NAPT) may block or disrupt functionality due to strict packet handling ().

## Features
- **NAT Traversal**: Establishes direct UDP-based tunnels between NATed devices.
- **Server/Client Modes**: Supports server (proxy) and client (connection) modes.
- **Flexible Connections**: Clients can connect to any host/port or a fixed server-defined endpoint.
- **Output Formats**: SQLite database, JSON, and text logs.
- **Multi-Threading**: Efficient connection handling.
- **Quiet Mode**: Minimizes terminal output.
- **Logging**: Saves logs to `natpiercer.log` and results to `natpiercer-output/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Network with basic NAT (RFC 1631); modern NAPT may limit functionality.
   - Root privileges (`sudo`) for socket operations.
   - Private network/lab you control.
2. **Install Dependencies**:
   - Save `setup_natpiercer.sh` to a directory (e.g., `/home/user/natpiercer/`).
   - Make executable and run:
     ```bash
     chmod +x setup_natpiercer.sh
     ./setup_natpiercer.sh
     ```
   - Installs Python and pip.
3. Save `natpiercer.py` to the same directory.
4. Verify:
   ```bash
   python3 natpiercer.py --help
   ```

## Usage
NatPiercer establishes UDP tunnels for TCP payloads in a controlled lab setting, bypassing NAT restrictions. Below are examples and expected outcomes.

### Basic Commands
Run server on port 8080:
```bash
sudo python3 natpiercer.py -m server -p 8080
```

Run client to connect to google.com:80 via server at 192.168.1.202:8080:
```bash
sudo python3 natpiercer.py -m client -l 127.0.0.1 -p 8000 --proxy-host 192.168.1.202 --proxy-port 8080 --remote-host google.com --remote-port 80
```

Run server in quiet mode:
```bash
sudo python3 natpiercer.py -m server -p 8080 -q
```

### Options
- `-m, --mode`: Mode (server or client, required).
- `-l, --local-ip`: Local IP address (default: 0.0.0.0).
- `-p, --local-port`: Local port (default: 2222).
- `--proxy-host`: Proxy server host (client mode).
- `--proxy-port`: Proxy server port (default: 2222).
- `--remote-host`: Remote host to connect to (client mode).
- `--remote-port`: Remote port (client mode).
- `-T, --threads`: Number of threads (default: 5).
- `-q, --quiet`: Log to file only.

### Features

#### Server Mode
- **Purpose**: Runs a proxy server behind a NAT, accepting client connections.
- **Usage**:
  ```bash
  sudo python3 natpiercer.py -m server -p 8080
  ```
- **Output**:
  ```
  2025-05-15 14:00:00 - INFO - Starting NatPiercer
  2025-05-15 14:00:02 - INFO - New client: 192.168.1.100:12345
  ```
- **Result File** (`natpiercer-output/piercer_20250515_140000.txt`):
  ```
  === NatPiercer Results ===
  Timestamp: 2025-05-15 14:00:02
  [2025-05-15 14:00:00] server: Server started, Local=0.0.0.0:8080, Proxy=None:2222, Remote=None:None
  [2025-05-15 14:00:02] server: Client connected: 192.168.1.100:12345, Local=0.0.0.0:8080, Proxy=None:2222, Remote=None:None
  ```
- **JSON File** (`natpiercer-output/piercer_20250515_140000.json`):
  ```json
  {
    "mode": "server",
    "local_ip": "0.0.0.0",
    "local_port": 8080,
    "proxy_host": null,
    "proxy_port": 2222,
    "remote_host": null,
    "remote_port": null,
    "connections": [
      {
        "mode": "server",
        "local_ip": "0.0.0.0",
        "local_port": 8080,
        "proxy_host": null,
        "proxy_port": 2222,
        "remote_host": null,
        "remote_port": null,
        "status": "Server started",
        "timestamp": "2025-05-15 14:00:00"
      },
      {
        "mode": "server",
        "local_ip": "0.0.0.0",
        "local_port": 8080,
        "proxy_host": null,
        "proxy_port": 2222,
        "remote_host": null,
        "remote_port": null,
        "status": "Client connected: 192.168.1.100:12345",
        "timestamp": "2025-05-15 14:00:02"
      }
    ],
    "timestamp": "2025-05-15 14:00:02"
  }
  ```
- **Tips**: Use **NetSentry** to identify server’s public IP.

#### Client Mode
- **Purpose**: Connects to a server behind a NAT, tunneling to a remote host.
- **Usage**:
  ```bash
  sudo python3 natpiercer.py -m client -l 127.0.0.1 -p 8000 --proxy-host 192.168.1.202 --proxy-port 8080 --remote-host google.com --remote-port 80
  ```
- **Output**:
  ```
  2025-05-15 14:00:03 - INFO - Received data from 192.168.1.202:8080: 1460 bytes
  ```
- **Tips**: Test with local services (e.g., HTTP server) before external hosts.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  sudo python3 natpiercer.py -m server -p 8080 -q
  ```
- **Tips**: Monitor `natpiercer.log` with `tail -f natpiercer.log`.

### Workflow
1. Set up lab (VM with network access, basic NAT).
2. Install dependencies:
   ```bash
   ./setup_natpiercer.sh
   ```
3. Run server on one machine:
   ```bash
   sudo python3 natpiercer.py -m server -p 8080
   ```
4. Run client on another:
   ```bash
   sudo python3 natpiercer.py -m client -l 127.0.0.1 -p 8000 --proxy-host <server_public_ip> --proxy-port 8080 --remote-host google.com --remote-port 80
   ```
5. Monitor output in terminal or `natpiercer.log`.
6. Check results in `natpiercer-output/` (text, JSON, SQLite).
7. Stop with `Ctrl+C`; secure outputs (`rm -rf natpiercer-output/*`).

## Output
- **Logs**: `natpiercer.log`, e.g.:
  ```
  2025-05-15 14:00:00 - INFO - Starting NatPiercer
  2025-05-15 14:00:02 - INFO - New client: 192.168.1.100:12345
  ```
- **Results**: `natpiercer-output/piercer_<timestamp>.txt` and `.json`.
- **Database**: `natpiercer-output/natpiercer.db` (SQLite).

## Notes
- **Environment**: Use on authorized networks with basic NATs in your lab.
- **Impact**: May fail with modern NAPT devices due to strict packet handling ().
- **Ethics**: Avoid unauthorized tunneling to prevent legal/security issues.
- **Dependencies**: Minimal; relies on Python’s standard library.
- **Root**: Requires `sudo` for socket binding.
- **Sources**: Inspired by pwnat’s documentation () and Kali Linux tools ().

## Disclaimer
**Personal Use Only**: NatPiercer is for learning on networks you own or have permission to test. Unauthorized NAT traversal is illegal and may lead to legal consequences or ethical issues. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM with basic NAT).
- Secure outputs (`natpiercer.log`, `natpiercer-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate networks without permission.
- Sharing sensitive output files.
- Production environments to prevent disruptions.

## Limitations
- **NAT Compatibility**: Works with basic NATs (RFC 1631); fails with modern NAPT due to port mapping or ICMP restrictions ().
- **Protocol**: Supports UDP tunneling for TCP; lacks pwnat’s ICMP-based approach ().
- **Features**: Basic proxy functionality; no advanced firewall bypassing or IPv6 support.
- **Interface**: CLI-only; lacks GUI or TUI.
- **Reliability**: May fail in double-NAT scenarios ().

## Tips
- Verify NAT type with Wireshark or **NetSentry**.
- Test with local HTTP/SSH servers before external hosts.
- Combine with **WiFiCrush** for network access or **SignalSnare** for signal analysis.
- Monitor traffic with Wireshark to debug failures.
- Consider IPv6 for NAT-free communication if available ().

## License
For personal educational use; no formal license. Use responsibly.