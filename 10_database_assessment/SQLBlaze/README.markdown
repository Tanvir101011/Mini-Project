# SQLBlaze

## Description
SQLBlaze is a Python-based tool designed for ethical SQL injection testing in your private lab (Ubuntu 24.04, home network). It automates the detection and exploitation of SQL injection vulnerabilities in web applications, supporting multiple injection strategies (Normal, Blind, Time-based) and database engines (MySQL, PostgreSQL, SQLite). The tool features a CLI interface, SQLite logging, JSON output, tamper scripts to bypass filters, and proxy support, integrating with your tools like **CodeSentry**, **APKForge**, **Dex2Java**, **SmaliCraft**, **PatternSentry**, **NetSentry**, **IdentityForge**, **IAXStorm**, **SlowStrike**, **SSLBlaze**, **RTPStorm**, and **NetBlitz**.

**Important**: Use SQLBlaze only on systems you own or have explicit permission to test. Unauthorized SQL injection may violate intellectual property laws, terms of service, or ethical standards. This tool is restricted to your lab for responsible use. Ensure compliance with local laws, including cybersecurity and data protection regulations.

## Features
- **Detection**: Identifies SQL injection vulnerabilities using error-based payloads.
- **Blind Injection**: Extracts data using boolean-based blind SQL injection.
- **Time-based Injection**: Detects vulnerabilities via response delays.
- **Enumeration**: Extracts database information (e.g., table names) using union-based payloads.
- **Tamper Scripts**: Bypasses filters with random case or space-to-comment transformations.
- **Output Formats**: SQLite database, JSON, and text logs.
- **Logging**: Saves logs to `sql_blaze.log` and results to `sql_blaze-output/logs/`.
- **Proxy Support**: Routes traffic through HTTP proxies.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Private lab environment.
2. **Install Dependencies**:
   - Save `setup_sql_blaze.sh` to a directory (e.g., `/home/user/sql_blaze/`).
   - Make executable and run:
     ```bash
     chmod +x setup_sql_blaze.sh
     ./setup_sql_blaze.sh
     ```
   - Installs Python and required packages (`requests`, `python-cookiejar`).
3. Save `sql_blaze.py` to the same directory.
4. Verify:
   ```bash
   python3 sql_blaze.py --help
   ```

## Usage
SQLBlaze facilitates SQL injection testing in a controlled lab setting for educational purposes. Below are examples and expected outcomes.

### Basic Commands
Detect SQL injection:
```bash
python3 sql_blaze.py -a detect -u "http://example.com?id=1"
```

Perform blind SQL injection:
```bash
python3 sql_blaze.py -a blind -u "http://example.com?id=1" -o output_dir
```

Perform time-based SQL injection:
```bash
python3 sql_blaze.py -a time-based -u "http://example.com?id=1" -o output_dir
```

Enumerate database tables:
```bash
python3 sql_blaze.py -a enumerate -u "http://example.com?id=1" -o output_dir
```

Use tamper script and proxy:
```bash
python3 sql_blaze.py -a detect -u "http://example.com?id=1" -t randomcase -p "http://localhost:8080"
```

Run in quiet mode:
```bash
python3 sql_blaze.py -a detect -u "http://example.com?id=1" -q
```

### Options
- `-a, --action`: Action to perform (detect, blind, time-based, enumerate; required).
- `-u, --url`: Target URL with injectable parameter (required).
- `-m, --method`: HTTP method (GET, POST; default: GET).
- `-d, --data`: POST data (e.g., 'id=1&name=test' or JSON).
- `-c, --cookies`: Path to Netscape cookie file.
- `-p, --proxy`: Proxy URL (e.g., http://localhost:8080).
- `-o, --output`: Output directory (default: sql_blaze-output).
- `-t, --tamper`: Tamper script (randomcase, space2comment).
- `-q, --quiet`: Log to file only.

### Features

#### Detection
- **Purpose**: Identify SQL injection vulnerabilities using error-based payloads.
- **Usage**:
  ```bash
  python3 sql_blaze.py -a detect -u "http://example.com?id=1"
  ```
- **Output**:
  ```
  2025-05-15 17:29:00 - INFO - SQL injection detected with payload: ' OR '1'='1
  ```
- **JSON File** (`output_dir/logs/sql_blaze_20250515_172900.json`):
  ```json
  {
    "url": "http://example.com?id=1",
    "output_dir": "output_dir",
    "actions": [
      {
        "url": "http://example.com?id=1",
        "action": "Detect Injection",
        "status": "SQL injection detected with payload: ' OR '1'='1",
        "output_path": "",
        "timestamp": "2025-05-15 17:29:00"
      }
    ],
    "timestamp": "2025-05-15 17:29:00"
  }
  ```
- **Tips**: Use with tamper scripts (`-t randomcase`) to bypass WAFs.

#### Blind Injection
- **Purpose**: Extract data using boolean-based blind SQL injection.
- **Usage**:
  ```bash
  python3 sql_blaze.py -a blind -u "http://example.com?id=1" -o output_dir
  ```
- **Output**:
  ```
  2025-05-15 17:29:00 - INFO - Blind injection extracted data to output_dir/blind_results.txt
  ```
- **Result File** (`output_dir/blind_results.txt`):
  ```
  Database name: testdb
  ```
- **Tips**: Slow but stealthy; combine with proxy (`-p`) for anonymity.

#### Time-based Injection
- **Purpose**: Detect vulnerabilities via response delays.
- **Usage**:
  ```bash
  python3 sql_blaze.py -a time-based -u "http://example.com?id=1" -o output_dir
  ```
- **Output**:
  ```
  2025-05-15 17:29:00 - INFO - Time-based injection results saved to output_dir/time_based_results.txt
  ```
- **Result File** (`output_dir/time_based_results.txt`):
  ```
  Time-based injection successful
  ```
- **Tips**: Effective for servers without error messages.

#### Enumeration
- **Purpose**: Extract database information (e.g., table names).
- **Usage**:
  ```bash
  python3 sql_blaze.py -a enumerate -u "http://example.com?id=1" -o output_dir
  ```
- **Output**:
  ```
  2025-05-15 17:29:00 - INFO - Database enumeration saved to output_dir/enumerate_results.txt
  ```
- **Result File** (`output_dir/enumerate_results.txt`):
  ```
  Table: users
  Table: orders
  ```
- **Tips**: Use with **PatternSentry** to analyze extracted data.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  python3 sql_blaze.py -a detect -u "http://example.com?id=1" -q
  ```
- **Tips**: Monitor `sql_blaze.log` with `tail -f sql_blaze.log`.

### Workflow
1. Set up lab (Ubuntu 24.04 with required packages installed).
2. Install dependencies:
   ```bash
   ./setup_sql_blaze.sh
   ```
3. Detect SQL injection:
   ```bash
   python3 sql_blaze.py -a detect -u "http://example.com?id=1"
   ```
4. Perform blind or time-based injection:
   ```bash
   python3 sql_blaze.py -a blind -u "http://example.com?id=1" -o output_dir
   ```
5. Enumerate database:
   ```bash
   python3 sql_blaze.py -a enumerate -u "http://example.com?id=1" -o output_dir
   ```
6. Monitor output in terminal or `sql_blaze.log`.
7. Check results in `sql_blaze-output/logs/` (text, JSON, SQLite).
8. Secure outputs (`rm -rf sql_blaze-output/*`).

## Output
- **Logs**: `sql_blaze.log`, e.g.:
  ```
  2025-05-15 17:29:00 - INFO - SQL injection detected with payload: ' OR '1'='1
  2025-05-15 17:29:01 - INFO - Results saved to output_dir/logs/sql_blaze_20250515_172900.json
  ```
- **Results**: `sql_blaze-output/logs/sql_blaze_<timestamp>.json` and result files.
- **Database**: `sql_blaze-output/logs/sql_blaze.db` (SQLite).

## Notes
- **Environment**: Use on systems you own or have permission to test in your lab.
- **Impact**: Extracts database information for security analysis; requires manual verification.
- **Ethics**: Avoid unauthorized testing to prevent legal or ethical issues.
- **Dependencies**: Requires `requests`, `python-cookiejar`.
- **Root**: Not required.
- **Sources**: Built for SQL injection testing, leveraging concepts from OWASP and sqlmap.

## Disclaimer
**Personal Use Only**: SQLBlaze is for educational testing of systems you own or have permission to test. Unauthorized SQL injection may violate laws or terms of service. Ensure compliance with local laws, including cybersecurity and data protection regulations.

**Safe Use**:
- Use in a private lab (e.g., Ubuntu 24.04).
- Secure outputs (`sql_blaze.log`, `sql_blaze-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Testing proprietary systems without permission.
- Sharing extracted data.
- Using in production environments.

## Limitations
- **Scope**: CLI-based; lacks GUI (unlike jSQL).
- **Dependencies**: Relies on `requests` for HTTP handling.
- **Compatibility**: Limited to MySQL, PostgreSQL, SQLite; may miss complex injections.
- **Features**: Basic detection and exploitation; no shell creation or file access.

## Tips
- Use with **PatternSentry** to scan extracted data for vulnerabilities.
- Test on local setups (e.g., DVWA, bWAPP) before real systems.
- Combine with **NetSentry** for network analysis or **IdentityForge** for credential testing.
- Review OWASP SQL Injection Prevention Cheat Sheet for secure coding practices.

## License
For personal educational use; no formal license. Use responsibly.