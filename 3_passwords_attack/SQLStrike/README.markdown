# SQLStrike

## Description
SQLStrike is a Python tool for studying authentication vulnerabilities in SQL databases within your private lab, inspired by **SQLdict**. It performs dictionary-based brute-force attacks against MySQL and Microsoft SQL Server (MSSQL) using custom or default credential wordlists. Designed for educational purposes, it supports multi-threading, logs results in text and JSON formats, and is compatible with tools like **WordForge** and **HashSnipe** in your lab setup (e.g., Ubuntu 24.04, home network).

**Important**: Use SQLStrike only on systems you own or have explicit permission to test. Unauthorized brute-forcing is illegal and may lead to legal consequences, account lockouts, or service disruptions. The tool is restricted to your lab to ensure ethical use.

## Features
- **Brute-Forcing**: Tests credentials on MySQL and MSSQL databases.
- **Multi-Threading**: Supports configurable thread counts for faster attacks.
- **JSON Output**: Saves results in JSON for parsing/automation.
- **Configurable**: Allows target IP, port, service, wordlists, database name, and timeout settings.
- **Logging**: Saves logs to `sqlstrike.log` and results to `sqlstrike-output/`.
- **Quiet Mode**: Minimizes terminal output.
- **Educational**: Simple design for learning database security.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Network access to lab SQL servers (e.g., `192.168.1.100`).
   - Private network you control.
2. **Install Dependencies**:
   - Save `setup_sqlstrike.sh` to a directory (e.g., `/home/user/sqlstrike/`).
   - Make executable and run:
     ```bash
     chmod +x setup_sqlstrike.sh
     ./setup_sqlstrike.sh
     ```
   - Installs `pymysql`, `pyodbc`, MSSQL ODBC driver, and default wordlists.
3. Save `sqlstrike.py` to the same directory.
4. Verify:
   ```bash
   python3 sqlstrike.py --help
   ```

## Usage
SQLStrike tests SQL server credentials to study authentication weaknesses. Below are examples and expected outcomes.

### Basic Commands
Brute-force MySQL:
```bash
python3 sqlstrike.py -t 192.168.1.100 -p 3306 -s mysql -u users.txt -w passwords.txt -T 5
```

Brute-force MSSQL with a specific database in quiet mode:
```bash
python3 sqlstrike.py -t 192.168.1.100 -p 1433 -s mssql -u users.txt -w passwords.txt -T 10 -d master -q
```

### Options
- `-t, --target`: Target IP (required, e.g., `192.168.1.100`).
- `-p, --port`: Target port (required, e.g., `3306` for MySQL, `1433` for MSSQL).
- `-s, --service`: Service to brute-force (required, `mysql` or `mssql`).
- `-u, --user-list`: File with usernames (default: `/usr/share/wordlists/users.txt`).
- `-w, --pass-list`: File with passwords (default: `/usr/share/wordlists/passwords.txt`).
- `-T, --threads`: Number of threads (default: 5).
- `--timeout`: Connection timeout in seconds (default: 5).
- `-d, --database`: Database name (optional, e.g., `master` for MSSQL).
- `-q, --quiet`: Log to file only.

### Features

#### Brute-Forcing
- **Purpose**: Test credentials on SQL servers.
- **Usage**:
  ```bash
  python3 sqlstrike.py -t 192.168.1.100 -p 3306 -s mysql -u users.txt -w passwords.txt
  ```
- **Output**:
  ```
  2025-05-15 13:10:00 - INFO - Starting SQLStrike on 192.168.1.100:3306, service: mysql, threads: 5
  2025-05-15 13:10:02 - INFO - MySQL login successful: admin:password
  ```
- **Result File** (`sqlstrike-output/192.168.1.100_3306_mysql_20250515_131000.txt`):
  ```
  [2025-05-15 13:10:02] MySQL login successful: admin:password
  [2025-05-15 13:10:03] Brute-force complete
  ```
- **JSON File** (`sqlstrike-output/192.168.1.100_3306_mysql_20250515_131000.json`):
  ```json
  {
    "target": "192.168.1.100",
    "port": 3306,
    "service": "mysql",
    "database": null,
    "results": [
      {"user": "admin", "password": "password", "status": "success", "message": "MySQL login successful: admin:password"},
      {"user": "admin", "password": "admin123", "status": "failed", "message": "MySQL login failed: Access denied"}
    ],
    "timestamp": "2025-05-15 13:10:03"
  }
  ```
- **Tips**: Generate wordlists with **WordForge** (`python3 wordforge.py -m 4 -M 6 -c abc123`).

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  python3 sqlstrike.py -t 192.168.1.100 -p 1433 -s mssql -q
  ```
- **Tips**: Check `sqlstrike.log` with `tail -f sqlstrike.log`.

### Workflow
1. Set up lab (VM with MySQL/MSSQL server at `192.168.1.100`).
2. Install dependencies:
   ```bash
   ./setup_sqlstrike.sh
   ```
3. Prepare wordlists (e.g., `echo "admin" > users.txt; echo "password" > passwords.txt`).
4. Run brute-force:
   ```bash
   python3 sqlstrike.py -t 192.168.1.100 -p 3306 -s mysql -u users.txt -w passwords.txt -T 5
   ```
5. Check logs (`sqlstrike.log`) and results (`sqlstrike-output/`); verify with manual login.
6. Stop with `Ctrl+C`; secure outputs (`rm -rf sqlstrike-output/*`).

## Output
- **Logs**: `sqlstrike.log`, e.g.:
  ```
  2025-05-15 13:10:00 - INFO - Starting SQLStrike on 192.168.1.100:3306
  2025-05-15 13:10:02 - INFO - MySQL login successful: admin:password
  ```
- **Results**: `sqlstrike-output/<ip>_<port>_<service>_<timestamp>.txt` and `.json`.

## Notes
- **Environment**: Use on authorized SQL servers in your lab.
- **Impact**: May cause lockouts or load; test with caution.
- **Ethics**: Avoid unauthorized use to prevent legal/security issues.
- **Dependencies**: MSSQL requires ODBC driver; MySQL needs `pymysql`.

## Disclaimer
**Personal Use Only**: SQLStrike is for learning on systems you own or have permission to test. Unauthorized use is illegal and may lead to legal consequences, lockouts, or disruptions. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM with SQL server).
- Secure outputs (`sqlstrike.log`, `sqlstrike-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Public/corporate databases without permission.
- Sharing sensitive output files.
- Production systems to prevent lockouts.

## Limitations
- Supports MySQL and MSSQL; **SQLdict** may target more protocols.
- No advanced rate limiting or proxy support.
- Depends on network access and server configuration.

## Tips
- Set up MySQL (`sudo apt install mysql-server`) or MSSQL in your lab.
- Verify target (`netcat -zv 192.168.1.100 3306`).
- Use Wireshark to monitor login attempts.
- Test mitigations (e.g., strong passwords, account lockout policies).
- Combine with **WordForge** for wordlists or **HashSnipe** for hash cracking.

## License
For personal educational use; no formal license. Use responsibly.