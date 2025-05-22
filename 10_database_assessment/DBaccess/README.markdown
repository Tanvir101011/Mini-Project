# DBAssess

## Description
DBAssess is a Python-based tool designed for ethical database security assessment in your private lab (Ubuntu 24.04, home network). It evaluates the security and configuration of databases (MySQL, PostgreSQL, SQLite) for common misconfigurations, weak credentials, outdated versions, and potential vulnerabilities, generating detailed reports. The tool features a CLI interface, SQLite logging, JSON output, and compatibility with your tools like **MDBQuery**, **SQLBlaze**, **CodeSentry**, **APKForge**, **Dex2Java**, **SmaliCraft**, **PatternSentry**, **NetSentry**, **IdentityForge**, **IAXStorm**, **SlowStrike**, **SSLBlaze**, **RTPStorm**, and **NetBlitz**.

**Important**: Use DBAssess only on databases you own or have explicit permission to assess. Unauthorized access or testing may violate intellectual property laws, terms of service, or ethical standards. This tool is restricted to your lab for responsible use. Ensure compliance with local laws, including cybersecurity and data protection regulations.

## Features
- **Port Scanning**: Checks if the database port is open.
- **Credential Testing**: Detects default or weak credentials.
- **Version Checking**: Identifies outdated database versions with potential vulnerabilities.
- **Permission Auditing**: Evaluates excessive user permissions.
- **Exposure Check**: Detects if the database is externally accessible.
- **Output Formats**: SQLite database, JSON, and text reports.
- **Logging**: Saves logs to `db_assess.log` and results to `db_assess-output/logs/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Database client libraries (`mysql-connector-python`, `psycopg2`, `sqlite3`).
   - Private lab environment.
2. **Install Dependencies**:
   - Save `setup_db_assess.sh` to a directory (e.g., `/home/user/db_assess/`).
   - Make executable and run:
     ```bash
     chmod +x setup_db_assess.sh
     ./setup_db_assess.sh
     ```
   - Installs Python and required packages (`mysql-connector-python`, `psycopg2-binary`).
3. Save `db_assess.py` to the same directory.
4. Verify:
   ```bash
   python3 db_assess.py --help
   ```

## Usage
DBAssess facilitates database security assessment in a controlled lab setting for educational purposes. Below are examples and expected outcomes.

### Basic Commands
Assess a MySQL database:
```bash
python3 db_assess.py -t mysql -H localhost -P 3306 -u root -p password -o output_dir
```

Assess a PostgreSQL database:
```bash
python3 db_assess.py -t postgresql -H localhost -P 5432 -u postgres -p postgres -d mydb -o output_dir
```

Assess a SQLite database:
```bash
python3 db_assess.py -t sqlite -d /path/to/database.db -o output_dir
```

Run in quiet mode:
```bash
python3 db_assess.py -t mysql -H localhost -P 3306 -u root -p password -q
```

### Options
- `-t, --type`: Database type (mysql, postgresql, sqlite; required).
- `-H, --host`: Database host (default: localhost).
- `-P, --port`: Database port (default: 3306 for mysql, 5432 for postgresql).
- `-u, --user`: Database user (default: root).
- `-p, --password`: Database password (default: empty).
- `-d, --database`: Database name or SQLite file path.
- `-o, --output`: Output directory (default: db_assess-output).
- `-q, --quiet`: Log to file only.

### Features

#### Port Scanning
- **Purpose**: Check if the database port is open.
- **Usage**:
  ```bash
  python3 db_assess.py -t mysql -H localhost -P 3306 -u root -p password
  ```
- **Output**:
  ```
  2025-05-15 17:41:00 - INFO - Port 3306 is open on localhost
  ```
- **Tips**: Ensure the port is not exposed externally.

#### Credential Testing
- **Purpose**: Detect default or weak credentials.
- **Usage**:
  ```bash
  python3 db_assess.py -t postgresql -H localhost -P 5432 -u postgres -p postgres
  ```
- **Output**:
  ```
  2025-05-15 17:41:00 - WARNING - Default/weak credentials found: postgres:postgres
  ```
- **Tips**: Use with **IdentityForge** to generate secure credentials.

#### Version Checking
- **Purpose**: Identify outdated database versions.
- **Usage**:
  ```bash
  python3 db_assess.py -t mysql -H localhost -P 3306 -u root -p password
  ```
- **Output**:
  ```
  2025-05-15 17:41:00 - INFO - Database version: 8.0.30
  ```
- **Tips**: Cross-reference versions with CVE databases.

#### Permission Auditing
- **Purpose**: Evaluate excessive user permissions.
- **Usage**:
  ```bash
  python3 db_assess.py -t mysql -H localhost -P 3306 -u root -p password
  ```
- **Output**:
  ```
  2025-05-15 17:41:00 - WARNING - Permissions: GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' (excessive)
  ```
- **Tips**: Restrict permissions to least privilege.

#### Exposure Check
- **Purpose**: Detect if the database is externally accessible.
- **Usage**:
  ```bash
  python3 db_assess.py -t mysql -H 192.168.1.100 -P 3306 -u root -p password
  ```
- **Output**:
  ```
  2025-05-15 17:41:00 - WARNING - Database is bound to 192.168.1.100 (potentially exposed externally)
  ```
- **Tips**: Bind databases to localhost or use firewalls.

### Workflow
1. Set up lab (Ubuntu 24.04 with required packages installed).
2. Install dependencies:
   ```bash
   ./setup_db_assess.sh
   ```
3. Assess a database:
   ```bash
   python3 db_assess.py -t mysql -H localhost -P 3306 -u root -p password -o output_dir
   ```
4. Monitor output in terminal or `db_assess.log`.
5. Check results in `db_assess-output/` (text, JSON, SQLite).
6. Secure outputs (`rm -rf db_assess-output/*`).

## Output
- **Logs**: `db_assess.log`, e.g.:
  ```
  2025-05-15 17:41:00 - INFO - Connected to mysql database at localhost:3306
  2025-05-15 17:41:00 - WARNING - Default/weak credentials found: root:
  2025-05-15 17:41:01 - INFO - Results saved to output_dir/db_assess_report_20250515_174100.txt
  ```
- **Reports**: `db_assess-output/db_assess_report_<timestamp>.txt`, e.g.:
  ```
  Database Assessment Report
  Database: mysql at localhost:3306
  Timestamp: 2025-05-15 17:41:00
  ==================================================
  Check: Default Credentials
  Status: Vulnerable
  Details: Default/weak credentials found: root:
  --------------------------------------------------
  Check: Version Check
  Status: OK
  Details: Database version: 8.0.30
  --------------------------------------------------
  ```
- **JSON**: `db_assess-output/logs/db_assess_<timestamp>.json`.
- **Database**: `db_assess-output/logs/db_assess.db` (SQLite).

## Notes
- **Environment**: Use on databases you own or have permission to assess in your lab.
- **Impact**: Identifies security issues for remediation; requires manual verification.
- **Ethics**: Avoid unauthorized access to prevent legal or ethical issues.
- **Dependencies**: Requires `mysql-connector-python`, `psycopg2-binary`.
- **Root**: Not required.
- **Sources**: Built for database security, leveraging concepts from OWASP and SANS Institute.

## Disclaimer
**Personal Use Only**: DBAssess is for educational testing of databases you own or have permission to assess. Unauthorized access or testing may violate laws or terms of service. Ensure compliance with local laws, including cybersecurity and data protection regulations.

**Safe Use**:
- Use in a private lab (e.g., Ubuntu 24.04).
- Secure outputs (`db_assess.log`, `db_assess-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Testing proprietary databases without permission.
- Sharing assessment reports.
- Using in production environments.

## Limitations
- **Scope**: CLI-based; lacks GUI.
- **Databases**: Limited to MySQL, PostgreSQL, SQLite.
- **Checks**: Basic security assessments; no advanced vulnerability scanning (e.g., SQL injection).
- **Dependencies**: Relies on database client libraries.

## Tips
- Use with **SQLBlaze** to test for SQL injection vulnerabilities.
- Combine with **PatternSentry** to scan database exports for sensitive data.
- Test on local setups (e.g., XAMPP, Dockerized databases) before real systems.
- Review OWASP Database Security Cheat Sheet for secure configuration practices.

## License
For personal educational use; no formal license. Use responsibly.