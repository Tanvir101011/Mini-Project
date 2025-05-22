# SlowStrike

## Description
SlowStrike is a Python-based tool designed for ethical security testing in your private lab (Ubuntu 24.04, home network). It simulates slow HTTP attacks, such as Slowloris and Slow POST, to stress-test web servers (e.g., Apache, Nginx) and evaluate their resilience against resource exhaustion. The tool features a CLI interface, SQLite logging, JSON output, and multi-threading, integrating with your tools like **NetSentry**, **NatPiercer**, **WiFiCrush**, and **IdentityForge**.

**Important**: Use SlowStrike only on servers and networks you own or have explicit permission to test. Unauthorized HTTP attacks are illegal and may lead to legal consequences, network disruptions, or ethical issues. This tool is restricted to your lab for responsible use. Modern web servers may mitigate slow attacks with timeouts or intrusion detection.

## Features
- **Slow HTTP Attacks**: Simulates Slowloris (slow headers) and Slow POST attacks.
- **Output Formats**: SQLite database, JSON, and text logs.
- **Multi-Threading**: Efficient connection management with configurable threads.
- **Quiet Mode**: Minimizes terminal output.
- **Logging**: Saves logs to `slowstrike.log` and results to `slowstrike-output/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Network access to target web server.
   - Private network/lab you control.
2. **Install Dependencies**:
   - Save `setup_slowstrike.sh` to a directory (e.g., `/home/user/slowstrike/`).
   - Make executable and run:
     ```bash
     chmod +x setup_slowstrike.sh
     ./setup_slowstrike.sh
     ```
   - Installs Python and pip.
3. Save `slowstrike.py` to the same directory.
4. Verify:
   ```bash
   python3 slowstrike.py --help
   ```

## Usage
SlowStrike simulates slow HTTP attacks in a controlled lab setting to test web server resilience. Below are examples and expected outcomes.

### Basic Commands
Simulate a Slowloris attack:
```bash
python3 slowstrike.py -t example.com -m slowloris -c 100 -d 60
```

Simulate a Slow POST attack on HTTPS:
```bash
python3 slowstrike.py -t example.com -p 443 -m slowpost -c 50 -d 30
```

Run in quiet mode:
```bash
python3 slowstrike.py -t example.com -m slowloris -c 100 -d 60 -q
```

### Options
- `-t, --target`: Target hostname or IP address (required).
- `-p, --port`: Target port (default: 80).
- `-m, --mode`: Attack mode: slowloris or slowpost (default: slowloris).
- `-c, --connections`: Number of concurrent connections (default: 100).
- `-i, --interval`: Interval between sends in seconds (default: 10).
- `-d, --duration`: Attack duration in seconds (default: 60).
- `-T, --threads`: Number of threads (default: 5).
- `-q, --quiet`: Log to file only.

### Features

#### Slowloris Attack
- **Purpose**: Simulate slow HTTP header attacks to exhaust server resources.
- **Usage**:
  ```bash
  python3 slowstrike.py -t example.com -m slowloris -c 100 -d 60
  ```
- **Output**:
  ```
  2025-05-15 16:00:00 - INFO - Starting SlowStrike against example.com:80 in slowloris mode
  2025-05-15 16:01:00 - INFO - Slowloris connection to example.com:80 completed
  ```
- **Result File** (`slowstrike-output/strike_20250515_160000.txt`):
  ```
  === SlowStrike Results ===
  Timestamp: 2025-05-15 16:01:00
  [2025-05-15 16:01:00] Slowloris connection to example.com:80 completed, Target=example.com:80, Mode=slowloris, Connections=100
  ```
- **JSON File** (`slowstrike-output/strike_20250515_160000.json`):
  ```json
  {
    "target": "example.com",
    "port": 80,
    "mode": "slowloris",
    "connections": 100,
    "duration": 60,
    "actions": [
      {
        "target": "example.com",
        "port": 80,
        "mode": "slowloris",
        "connections": 100,
        "status": "Slowloris connection to example.com:80 completed",
        "timestamp": "2025-05-15 16:01:00"
      }
    ],
    "timestamp": "2025-05-15 16:01:00"
  }
  ```
- **Tips**: Use **NetSentry** to monitor server traffic; test with a local Apache/Nginx server.

#### Slow POST Attack
- **Purpose**: Simulate slow POST data attacks to consume server resources.
- **Usage**:
  ```bash
  python3 slowstrike.py -t example.com -p 443 -m slowpost -c 50 -d 30
  ```
- **Output**:
  ```
  2025-05-15 16:00:00 - INFO - Starting SlowStrike against example.com:443 in slowpost mode
  2025-05-15 16:00:30 - INFO - Slow POST connection to example.com:443 completed, sent 5000 bytes
  ```
- **Tips**: Test HTTPS servers with port 443; verify server logs for connection handling.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  python3 slowstrike.py -t example.com -m slowloris -c 100 -d 60 -q
  ```
- **Tips**: Monitor `slowstrike.log` with `tail -f slowstrike.log`.

### Workflow
1. Set up lab (VM with web server, e.g., Apache/Nginx, network access).
2. Install dependencies:
   ```bash
   ./setup_slowstrike.sh
   ```
3. Run SlowStrike:
   ```bash
   python3 slowstrike.py -t example.com -m slowloris -c 100 -d 60
   ```
4. Monitor output in terminal or `slowstrike.log`.
5. Check results in `slowstrike-output/` (text, JSON, SQLite).
6. Stop with `Ctrl+C`; secure outputs (`rm -rf slowstrike-output/*`).

## Output
- **Logs**: `slowstrike.log`, e.g.:
  ```
  2025-05-15 16:00:00 - INFO - Starting SlowStrike against example.com:80 in slowloris mode
  2025-05-15 16:01:00 - INFO - Slowloris connection to example.com:80 completed
  ```
- **Results**: `slowstrike-output/strike_<timestamp>.txt` and `.json`.
- **Database**: `slowstrike-output/slowstrike.db` (SQLite).

## Notes
- **Environment**: Use on authorized servers/networks in your lab.
- **Impact**: Slow attacks may degrade server performance; modern servers may mitigate with timeouts or IDS.
- **Ethics**: Avoid unauthorized testing to prevent legal/security issues.
- **Dependencies**: Minimal; uses Python’s standard library.
- **Root**: Not required, but network access is needed.
- **Sources**: Built for HTTP testing, leveraging web security concepts and Kali Linux toolsets.

## Disclaimer
**Personal Use Only**: SlowStrike is for learning on servers/networks you own or have permission to test. Unauthorized HTTP attacks are illegal and may lead to legal consequences or ethical issues. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM with isolated network).
- Secure outputs (`slowstrike.log`, `slowstrike-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate networks without permission.
- Sharing sensitive output files.
- Production environments to prevent disruptions.

## Limitations
- **Attack Scope**: Simulates Slowloris and Slow POST; lacks other DoS methods (e.g., RUDY).
- **Mitigation**: Servers with timeouts or IDS may block attacks.
- **Interface**: CLI-only; lacks GUI or TUI.
- **Protocol**: Focuses on HTTP/HTTPS; no other protocols.

## Tips
- Test with a local Apache/Nginx server to simulate real HTTP traffic.
- Use Wireshark or **NetSentry** to monitor attack traffic.
- Combine with **WiFiCrush** for network access or **NatPiercer** for tunneling.
- Adjust connections and interval to avoid overwhelming lab resources.
- Check server logs to assess attack impact.

## License
For personal educational use; no formal license. Use responsibly.