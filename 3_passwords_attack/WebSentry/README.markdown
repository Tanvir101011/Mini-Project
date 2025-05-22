# WebSentry

## Description
WebSentry is a Python-based web application security testing tool inspired by **WebScarab**, designed for studying vulnerabilities in web applications within your private lab. It acts as an intercepting proxy to capture, modify, and analyze HTTP/HTTPS traffic, with features like spidering, fuzzing, and vulnerability detection (e.g., XSS, SQL injection). Built for educational purposes, it supports multi-threading, JSON output, and a CLI interface, integrating with your lab tools like **SQLStrike**, **WordForge**, and **HashSnipe** (Ubuntu 24.04, home network).

**Important**: Use WebSentry only on systems you own or have explicit permission to test. Unauthorized testing is illegal and may lead to legal consequences, account lockouts, or service disruptions. The tool is restricted to your lab to ensure ethical use.

## Features
- **Proxy**: Intercepts HTTP/HTTPS requests and responses.
- **Spidering**: Crawls target site to discover URLs.
- **Fuzzing**: Tests for vulnerabilities like XSS and SQL injection.
- **Analysis**: Detects common vulnerabilities in responses.
- **Multi-Threading**: Handles multiple requests efficiently.
- **JSON Output**: Saves results for parsing/automation.
- **Database**: Stores requests in SQLite for analysis.
- **Configurable**: Supports custom host, port, and target URL.
- **Logging**: Saves logs to `websentry.log` and results to `websentry-output/`.
- **Quiet Mode**: Minimizes terminal output.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Network access to lab web server (e.g., `192.168.1.100`).
   - Private network you control.
2. **Install Dependencies**:
   - Save `setup_websentry.sh` to a directory (e.g., `/home/user/websentry/`).
   - Make executable and run:
     ```bash
     chmod +x setup_websentry.sh
     ./setup_websentry.sh
     ```
   - Installs `requests`, `beautifulsoup4`, and `lxml`.
3. Save `websentry.py` to the same directory.
4. Configure browser proxy to `127.0.0.1:8008` (default).
5. Verify:
   ```bash
   python3 websentry.py --help
   ```

## Usage
WebSentry tests web applications by intercepting traffic and analyzing for vulnerabilities. Below are examples and expected outcomes.

### Basic Commands
Start proxy for a target:
```bash
python3 websentry.py -l 127.0.0.1 -p 8008 -t http://192.168.1.100
```

Enable fuzzing and spidering in quiet mode:
```bash
python3 websentry.py -l 127.0.0.1 -p 8008 -t http://192.168.1.100 -T 10 --fuzz --spider --analyze -q
```

### Options
- `-l, --listen-host`: Host to listen on (default: `127.0.0.1`).
- `-p, --listen-port`: Port to listen on (default: `8008`).
- `-t, --target-url`: Target URL (required, e.g., `http://192.168.1.100`).
- `-T, --threads`: Number of threads (default: 5).
- `--fuzz`: Enable fuzzing for vulnerabilities.
- `--spider`: Enable spidering to discover URLs.
- `--analyze`: Enable vulnerability analysis.
- `-q, --quiet`: Log to file only.

### Features

#### Proxy
- **Purpose**: Intercept and log HTTP/HTTPS traffic.
- **Usage**:
  ```bash
  python3 websentry.py -l 127.0.0.1 -p 8008 -t http://192.168.1.100
  ```
  Configure browser proxy to `127.0.0.1:8008`, then browse the target.
- **Output**:
  ```
  2025-05-15 14:00:00 - INFO - Starting WebSentry proxy on 127.0.0.1:8008
  2025-05-15 14:00:02 - INFO - Intercepted GET request: /index.html
  ```
- **Tips**: Use with **DNSTwist** to test DNS-based vulnerabilities.

#### Spidering
- **Purpose**: Discover URLs on the target site.
- **Usage**:
  ```bash
  python3 websentry.py -l 127.0.0.1 -p 8008 -t http://192.168.1.100 --spider
  ```
- **Output**:
  ```
  2025-05-15 14:00:00 - INFO - Spidering http://192.168.1.100
  2025-05-15 14:00:01 - INFO - Found URL: http://192.168.1.100/login
  ```
- **Tips**: Combine with **WordForge** to generate payloads for discovered forms.

#### Fuzzing and Analysis
- **Purpose**: Test for vulnerabilities like XSS and SQL injection.
- **Usage**:
  ```bash
  python3 websentry.py -l 127.0.0.1 -p 8008 -t http://192.168.1.100 --fuzz --analyze
  ```
- **Output**:
  ```
  2025-05-15 14:00:03 - INFO - Potential vulnerability: XSS - Payload <script>alert('XSS')</script> reflected
  ```
- **Result File** (`websentry-output/scan_127.0.0.1_8008_20250515_140000.txt`):
  ```
  [2025-05-15 14:00:03] XSS: Payload <script>alert('XSS')</script> reflected in response
  [2025-05-15 14:00:04] Scan complete
  ```
- **JSON File** (`websentry-output/scan_127.0.0.1_8008_20250515_140000.json`):
  ```json
  {
    "target": "http://192.168.1.100",
    "listen": "127.0.0.1:8008",
    "urls": ["http://192.168.1.100", "http://192.168.1.100/login"],
    "vulnerabilities": [
      {
        "type": "XSS",
        "details": "Payload <script>alert('XSS')</script> reflected in response",
        "timestamp": "2025-05-15 14:00:03"
      }
    ],
    "timestamp": "2025-05-15 14:00:04"
  }
  ```
- **Tips**: Use **HashSnipe** to crack captured credentials.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  python3 websentry.py -l 127.0.0.1 -p 8008 -t http://192.168.1.100 -q
  ```
- **Tips**: Monitor `websentry.log` with `tail -f websentry.log`.

### Workflow
1. Set up lab (VM with web server at `192.168.1.100`).
2. Install dependencies:
   ```bash
   ./setup_websentry.sh
   ```
3. Start WebSentry:
   ```bash
   python3 websentry.py -l 127.0.0.1 -p 8008 -t http://192.168.1.100 --fuzz --spider --analyze
   ```
4. Configure browser proxy to `127.0.0.1:8008`.
5. Browse target site; check logs (`websentry.log`) and results (`websentry-output/`).
6. Stop with `Ctrl+C`; secure outputs (`rm -rf websentry-output/*`).

## Output
- **Logs**: `websentry.log`, e.g.:
  ```
  2025-05-15 14:00:00 - INFO - Starting WebSentry proxy on 127.0.0.1:8008
  2025-05-15 14:00:02 - INFO - Intercepted GET request: /index.html
  ```
- **Results**: `websentry-output/scan_<host>_<port>_<timestamp>.txt` and `.json`.
- **Database**: `websentry-output/websentry.db` (SQLite).

## Notes
- **Environment**: Use on authorized web servers in your lab.
- **Impact**: Fuzzing may cause load; test with caution.
- **Ethics**: Avoid unauthorized use to prevent legal/security issues.
- **Dependencies**: Requires `requests`, `beautifulsoup4`, `lxml`.

## Disclaimer
**Personal Use Only**: WebSentry is for learning on systems you own or have permission to test. Unauthorized use is illegal and may lead to legal consequences, lockouts, or disruptions. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM with web server).
- Secure outputs (`websentry.log`, `websentry-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate websites without permission.
- Sharing sensitive output files.
- Production systems to prevent disruptions.

## Limitations
- Supports HTTP; HTTPS requires self-signed certificate setup (commented in code).
- Basic fuzzing payloads; **WebScarab** may offer more plugins.
- No GUI; CLI-focused, unlike **WebScarab**’s interface.
- Limited to basic vulnerability detection (XSS, SQL injection).

## Tips
- Set up a test web server (`sudo apt install apache2`).
- Verify target (`curl http://192.168.1.100`).
- Use Wireshark to monitor traffic.
- Test mitigations (e.g., input sanitization, WAF).
- Combine with **SQLStrike** for database testing or **DNSTwist** for DNS spoofing.

## License
For personal educational use; no formal license. Use responsibly.