# KeyValueAssess

## Description
KeyValueAssess is a Python-based tool designed for ethical security assessment of key-value NoSQL databases (Redis, Memcached, etcd) in your private lab (Ubuntu 24.04, home network). It evaluates common security misconfigurations, weak credentials, outdated versions, and potential vulnerabilities, generating detailed reports. The tool features a CLI interface, SQLite logging, JSON output, and compatibility with your tools like **NoSQLAssess**, **DBAssess**, **MDBQuery**, **SQLBlaze**, **CodeSentry**, **APKForge**, **Dex2Java**, **SmaliCraft**, **PatternSentry**, **NetSentry**, **IdentityForge**, **IAXStorm**, **SlowStrike**, **SSLBlaze**, **RTPStorm**, and **NetBlitz**.

**Important**: Use KeyValueAssess only on databases you own or have explicit permission to assess. Unauthorized access or testing may violate intellectual property laws, terms of service, or ethical standards. This tool is restricted to your lab for responsible use. Ensure compliance with local laws, including cybersecurity and data protection regulations.

## Features
- **Port Scanning**: Checks if the database port is open.
- **Credential Testing**: Detects default or weak credentials (Redis only).
- **Version Checking**: Identifies outdated database versions with potential vulnerabilities.
- **Authentication Auditing**: Verifies if authentication is enabled.
- **Exposure Check**: Detects if the database is externally accessible.
- **Output Formats**: SQLite database, JSON, and text reports.
- **Logging**: Saves logs to `keyvalue_assess.log` and results to `keyvalue_assess-output/logs/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Database client libraries (`redis`, `pylibmc`, `etcd3`).
   - Private lab environment.
2. **Install Dependencies**:
   - Save `setup_keyvalue_assess.sh` to a directory (e.g., `/home/user/keyvalue_assess/`).
   - Make executable and run:
     ```bash
     chmod +x setup_keyvalue_assess.sh
     ./setup_keyvalue_assess.sh
     ```
   - Installs Python, required packages (`redis`, `pylibmc`, `etcd3`), and dependencies (`libmemcached-dev`).
3. Save `keyvalue_assess.py` to the same directory.
4. Verify:
   ```bash
   python3 keyvalue_assess.py --help
   ```

## Usage
KeyValueAssess facilitates key-value database security assessment in a controlled lab setting for educational purposes. Below are examples and expected outcomes.

### Basic Commands
Assess a Redis database:
```bash
python3 keyvalue_assess.py -t redis -H localhost -P 6379 -o output_dir
```

Assess a Memcached database:
```bash
python3 keyvalue_assess.py -t memcached -H localhost -P 11211 -o output_dir
```

Assess an etcd database:
```bash
python3 keyvalue_assess.py -t etcd -H localhost -P 2379 -o output_dir
```

Run in quiet mode:
```bash
python3 keyvalue_assess.py -t redis -H localhost -P 6379 -q
```

### Options
- `-t, --type`: Database type (redis, memcached, etcd; required).
- `-H, --host`: Database host (default: localhost).
- `-P, --port`: Database port (default: 6379 for redis, 11211 for memcached, 2379 for etcd).
- `-p, --password`: Database password (for redis).
- `-o, --output`: Output directory (default: keyvalue_assess-output).
- `-q, --quiet`: Log to file only.

### Features

#### Port Scanning
- **Purpose**: Check if the database port is open.
- **Usage**:
  ```bash
  python3 keyvalue_assess.py -t redis -H localhost -P 6379
  ```
- **Output**:
  ```
  2025-05-15 17:47:00 - INFO - Port 6379 is open on localhost
  ```
- **Tips**: Ensure the port is not exposed externally.

#### Credential Testing
- **Purpose**: Detect default or weak credentials (Redis only).
- **Usage**:
  ```bash
  python3 keyvalue_assess.py -t redis -H localhost -P 6379
  ```
- **Output**:
  ```
  2025-05-15 17:47:00 - WARNING - Default/weak credentials found: no password
  ```
- **Tips**: Use with **IdentityForge** to generate secure credentials.

#### Version Checking
- **Purpose**: Identify outdated database versions.
- **Usage**:
  ```bash
  python3 keyvalue_assess.py -t memcached -H localhost -P 11211
  ```
- **Output**:
  ```
  2025-05-15 17:47:00 - INFO - Database version: 1.6.22
  ```
- **Tips**: Cross-reference versions with CVE databases.

#### Authentication Auditing
- **Purpose**: Verify if authentication is enabled.
- **Usage**:
  ```bash
  python3 keyvalue_assess.py -t memcached -H localhost -P 11211
  ```
- **Output**:
  ```
  2025-05-15 17:47:00 - WARNING - No authentication configured for Memcached
  ```
- **Tips**: Enable authentication where supported (e.g., Redis).

#### Exposure Check
- **Purpose**: Detect if the database is externally accessible.
- **Usage**:
  ```bash
  python3 keyvalue_assess.py -t etcd -H 192.168.1.100 -P 2379
  ```
- **Output**:
  ```
  2025-05-15 17:47:00 - WARNING - Database is bound to 192.168.1.100 (potentially exposed externally)
  ```
- **Tips**: Bind databases to localhost or use firewalls.

### Workflow
1. Set up lab (Ubuntu 24.04 with required packages installed).
2. Install dependencies:
   ```bash
   ./setup_keyvalue_assess.sh
   ```
3. Assess a key-value database:
   ```bash
   python3 keyvalue_assess.py -t redis -H localhost -P 6379 -o output_dir
   ```
4. Monitor output in terminal or `keyvalue_assess.log`.
5. Check results in `keyvalue_assess-output/` (text, JSON, SQLite).
6. Secure outputs (`rm -rf keyvalue_assess-output/*`).

## Output
- **Logs**: `keyvalue_assess.log`, e.g.:
  ```
  2025-05-15 17:47:00 - INFO - Connected to redis database at localhost:6379
  2025-05-15 17:47:00 - WARNING - No authentication configured for Redis
  2025-05-15 17:47:01 - INFO - Results saved to output_dir/keyvalue_assess_report_20250515_174700.txt
  ```
- **Reports**: `keyvalue_assess-output/keyvalue_assess_report_<timestamp>.txt`, e.g.:
  ```
  Key-Value Database Assessment Report
  Database: redis at localhost:6379
  Timestamp: 2025-05-15 17:47:00
  ==================================================
  Check: Authentication Check
  Status: Vulnerable
  Details: No authentication configured for Redis
  --------------------------------------------------
  Check: Version Check
  Status: OK
  Details: Database version: 7.0.12
  --------------------------------------------------
  ```
- **JSON**: `keyvalue_assess-output/logs/keyvalue_assess_<timestamp>.json`.
- **Database**: `keyvalue_assess-output/logs/keyvalue_assess.db` (SQLite).

## Notes
- **Environment**: Use on databases you own or have permission to assess in your lab.
- **Impact**: Identifies security issues for remediation; requires manual verification.
- **Ethics**: Avoid unauthorized access to prevent legal or ethical issues.
- **Dependencies**: Requires `redis`, `pylibmc`, `etcd3`, `libmemcached-dev`.
- **Root**: Required for `libmemcached-dev` installation.
- **Sources**: Built for key-value store security, leveraging concepts from OWASP and Redis security guidelines.

## Disclaimer
**Personal Use Only**: KeyValueAssess is for educational testing of databases you own or have permission to assess. Unauthorized access or testing may violate laws or terms of service. Ensure compliance with local laws, including cybersecurity and data protection regulations.

**Safe Use**:
- Use in a private lab (e.g., Ubuntu 24.04).
- Secure outputs (`keyvalue_assess.log`, `keyvalue_assess-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Testing proprietary databases without permission.
- Sharing assessment reports.
- Using in production environments.

## Limitations
- **Scope**: CLI-based; lacks GUI.
- **Databases**: Limited to Redis, Memcached, etcd.
- **Checks**: Basic security assessments; no advanced vulnerability scanning (e.g., data leakage).
- **Dependencies**: Relies on database client libraries.

## Tips
- Use with **NoSQLAssess** to assess other NoSQL databases or **DBAssess** for SQL databases.
- Combine with **PatternSentry** to scan database exports for sensitive data.
- Test on local setups (e.g., Dockerized Redis, etcd) before real systems.
- Review OWASP NoSQL Security Cheat Sheet for secure configuration practices.

## License
For personal educational use; no formal license. Use responsibly.