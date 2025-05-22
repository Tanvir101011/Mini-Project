# NoSQLAssess

## Description
NoSQLAssess is a Python-based tool designed for ethical security assessment of NoSQL databases (MongoDB, Redis, Cassandra) in your private lab (Ubuntu 24.04, home network). It evaluates common security misconfigurations, weak credentials, outdated versions, and potential vulnerabilities, generating detailed reports. The tool features a CLI interface, SQLite logging, JSON output, and compatibility with your tools like **DBAssess**, **MDBQuery**, **SQLBlaze**, **CodeSentry**, **APKForge**, **Dex2Java**, **SmaliCraft**, **PatternSentry**, **NetSentry**, **IdentityForge**, **IAXStorm**, **SlowStrike**, **SSLBlaze**, **RTPStorm**, and **NetBlitz**.

**Important**: Use NoSQLAssess only on databases you own or have explicit permission to assess. Unauthorized access or testing may violate intellectual property laws, terms of service, or ethical standards. This tool is restricted to your lab for responsible use. Ensure compliance with local laws, including cybersecurity and data protection regulations.

## Features
- **Port Scanning**: Checks if the database port is open.
- **Credential Testing**: Detects default or weak credentials.
- **Version Checking**: Identifies outdated database versions with potential vulnerabilities.
- **Authentication Auditing**: Verifies if authentication is enabled.
- **Exposure Check**: Detects if the database is externally accessible.
- **Output Formats**: SQLite database, JSON, and text reports.
- **Logging**: Saves logs to `nosql_assess.log` and results to `nosql_assess-output/logs/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Database client libraries (`pymongo`, `redis`, `cassandra-driver`).
   - Private lab environment.
2. **Install Dependencies**:
   - Save `setup_nosql_assess.sh` to a directory (e.g., `/home/user/nosql_assess/`).
   - Make executable and run:
     ```bash
     chmod +x setup_nosql_assess.sh
     ./setup_nosql_assess.sh
     ```
   - Installs Python and required packages (`pymongo`, `redis`, `cassandra-driver`).
3. Save `nosql_assess.py` to the same directory.
4. Verify:
   ```bash
   python3 nosql_assess.py --help
   ```

## Usage
NoSQLAssess facilitates NoSQL database security assessment in a controlled lab setting for educational purposes. Below are examples and expected outcomes.

### Basic Commands
Assess a MongoDB database:
```bash
python3 nosql_assess.py -t mongodb -H localhost -P 27017 -o output_dir
```

Assess a Redis database with credentials:
```bash
python3 nosql_assess.py -t redis -H localhost -P 6379 -p mypassword -o output_dir
```

Assess a Cassandra database:
```bash
python3 nosql_assess.py -t cassandra -H localhost -P 9042 -u cassandra -p cassandra -o output_dir
```

Run in quiet mode:
```bash
python3 nosql_assess.py -t mongodb -H localhost -P 27017 -q
```

### Options
- `-t, --type`: Database type (mongodb, redis, cassandra; required).
- `-H, --host`: Database host (default: localhost).
- `-P, --port`: Database port (default: 27017 for mongodb, 6379 for redis, 9042 for cassandra).
- `-u, --user`: Database user.
- `-p, --password`: Database password.
- `-o, --output`: Output directory (default: nosql_assess-output).
- `-q, --quiet`: Log to file only.

### Features

#### Port Scanning
- **Purpose**: Check if the database port is open.
- **Usage**:
  ```bash
  python3 nosql_assess.py -t mongodb -H localhost -P 27017
  ```
- **Output**:
  ```
  2025-05-15 17:44:00 - INFO - Port 27017 is open on localhost
  ```
- **Tips**: Ensure the port is not exposed externally.

#### Credential Testing
- **Purpose**: Detect default or weak credentials.
- **Usage**:
  ```bash
  python3 nosql_assess.py -t cassandra -H localhost -P 9042 -u cassandra -p cassandra
  ```
- **Output**:
  ```
  2025-05-15 17:44:00 - WARNING - Default/weak credentials found: cassandra:cassandra
  ```
- **Tips**: Use with **IdentityForge** to generate secure credentials.

#### Version Checking
- **Purpose**: Identify outdated database versions.
- **Usage**:
  ```bash
  python3 nosql_assess.py -t redis -H localhost -P 6379
  ```
- **Output**:
  ```
  2025-05-15 17:44:00 - INFO - Database version: 7.0.12
  ```
- **Tips**: Cross-reference versions with CVE databases.

#### Authentication Auditing
- **Purpose**: Verify if authentication is enabled.
- **Usage**:
  ```bash
  python3 nosql_assess.py -t redis -H localhost -P 6379
  ```
- **Output**:
  ```
  2025-05-15 17:44:00 - WARNING - No authentication configured for Redis
  ```
- **Tips**: Enable authentication in database configurations.

#### Exposure Check
- **Purpose**: Detect if the database is externally accessible.
- **Usage**:
  ```bash
  python3 nosql_assess.py -t mongodb -H 192.168.1.100 -P 27017
  ```
- **Output**:
  ```
  2025-05-15 17:44:00 - WARNING - Database is bound to 192.168.1.100 (potentially exposed externally)
  ```
- **Tips**: Bind databases to localhost or use firewalls.

### Workflow
1. Set up lab (Ubuntu 24.04 with required packages installed).
2. Install dependencies:
   ```bash
   ./setup_nosql_assess.sh
   ```
3. Assess a NoSQL database:
   ```bash
   python3 nosql_assess.py -t mongodb -H localhost -P 27017 -o output_dir
   ```
4. Monitor output in terminal or `nosql_assess.log`.
5. Check results in `nosql_assess-output/` (text, JSON, SQLite).
6. Secure outputs (`rm -rf nosql_assess-output/*`).

## Output
- **Logs**: `nosql_assess.log`, e.g.:
  ```
  2025-05-15 17:44:00 - INFO - Connected to mongodb database at localhost:27017
  2025-05-15 17:44:00 - WARNING - No authentication configured for MongoDB
  2025-05-15 17:44:01 - INFO - Results saved to output_dir/nosql_assess_report_20250515_174400.txt
  ```
- **Reports**: `nosql_assess-output/nosql_assess_report_<timestamp>.txt`, e.g.:
  ```
  NoSQL Database Assessment Report
  Database: mongodb at localhost:27017
  Timestamp: 2025-05-15 17:44:00
  ==================================================
  Check: Authentication Check
  Status: Vulnerable
  Details: No authentication configured for MongoDB
  --------------------------------------------------
  Check: Version Check
  Status: OK
  Details: Database version: 6.0.5
  --------------------------------------------------
  ```
- **JSON**: `nosql_assess-output/logs/nosql_assess_<timestamp>.json`.
- **Database**: `nosql_assess-output/logs/nosql_assess.db` (SQLite).

## Notes
- **Environment**: Use on databases you own or have permission to assess in your lab.
- **Impact**: Identifies security issues for remediation; requires manual verification.
- **Ethics**: Avoid unauthorized access to prevent legal or ethical issues.
- **Dependencies**: Requires `pymongo`, `redis`, `cassandra-driver`.
- **Root**: Not required.
- **Sources**: Built for NoSQL security, leveraging concepts from OWASP and MongoDB security guidelines.

## Disclaimer
**Personal Use Only**: NoSQLAssess is for educational testing of databases you own or have permission to assess. Unauthorized access or testing may violate laws or terms of service. Ensure compliance with local laws, including cybersecurity and data protection regulations.

**Safe Use**:
- Use in a private lab (e.g., Ubuntu 24.04).
- Secure outputs (`nosql_assess.log`, `nosql_assess-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Testing proprietary databases without permission.
- Sharing assessment reports.
- Using in production environments.

## Limitations
- **Scope**: CLI-based; lacks GUI.
- **Databases**: Limited to MongoDB, Redis, Cassandra.
- **Checks**: Basic security assessments; no advanced vulnerability scanning (e.g., injection attacks).
- **Dependencies**: Relies on database client libraries.

## Tips
- Use with **DBAssess** to assess SQL databases for a complete security audit.
- Combine with **PatternSentry** to scan database exports for sensitive data.
- Test on local setups (e.g., Dockerized MongoDB, Redis) before real systems.
- Review OWASP NoSQL Security Cheat Sheet for secure configuration practices.

## License
For personal educational use; no formal license. Use responsibly.