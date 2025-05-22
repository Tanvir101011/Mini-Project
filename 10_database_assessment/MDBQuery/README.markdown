# MDBQuery

## Description
MDBQuery is a Python-based tool designed for ethical management of Microsoft Access (MDB) databases in your private lab (Ubuntu 24.04, home network). It allows users to query MDB files using SQL, list tables, and export results to CSV or SQLite, without requiring Microsoft Access. The tool features a CLI interface, SQLite logging, JSON output, and compatibility with your tools like **SQLBlaze**, **CodeSentry**, **APKForge**, **Dex2Java**, **SmaliCraft**, **PatternSentry**, **NetSentry**, **IdentityForge**, **IAXStorm**, **SlowStrike**, **SSLBlaze**, **RTPStorm**, and **NetBlitz**.

**Important**: Use MDBQuery only on MDB files you own or have explicit permission to access. Unauthorized database access may violate intellectual property laws, terms of service, or ethical standards. This tool is restricted to your lab for responsible use. Ensure compliance with local laws, including cybersecurity and data protection regulations.

## Features
- **Table Listing**: Displays all tables in an MDB file.
- **SQL Queries**: Executes SQL queries (SELECT, INSERT, UPDATE, DELETE) on MDB files.
- **Data Export**: Saves query results to CSV or SQLite formats.
- **Output Formats**: SQLite database, JSON, and text logs.
- **Logging**: Saves logs to `mdb_query.log` and results to `mdb_query-output/logs/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - MDB Tools and ODBC driver (`mdbtools`, `unixodbc`).
   - Private lab environment.
2. **Install Dependencies**:
   - Save `setup_mdb_query.sh` to a directory (e.g., `/home/user/mdb_query/`).
   - Make executable and run:
     ```bash
     chmod +x setup_mdb_query.sh
     ./setup_mdb_query.sh
     ```
   - Installs Python, MDB Tools, ODBC drivers, and required packages (`pyodbc`, `pandas`).
3. Save `mdb_query.py` to the same directory.
4. Verify:
   ```bash
   python3 mdb_query.py --help
   ```

## Usage
MDBQuery facilitates querying MDB files in a controlled lab setting for educational purposes. Below are examples and expected outcomes.

### Basic Commands
List tables in an MDB file:
```bash
python3 mdb_query.py -f database.mdb -a list
```

Execute a SQL query:
```bash
python3 mdb_query.py -f database.mdb -a query -q "SELECT * FROM users" -o results.csv
```

Export query results to SQLite:
```bash
python3 mdb_query.py -f database.mdb -a query -q "SELECT * FROM orders" -o results.db --format sqlite
```

Run in quiet mode:
```bash
python3 mdb_query.py -f database.mdb -a list --quiet
```

### Options
- `-f, --file`: Path to MDB file (required).
- `-a, --action`: Action to perform (list, query; required).
- `-q, --query`: SQL query to execute (for query action).
- `-o, --output`: Output file for query results.
- `--format`: Output format (csv, sqlite; default: csv).
- `--output-dir`: Output directory (default: mdb_query-output).
- `--quiet`: Log to file only.

### Features

#### Table Listing
- **Purpose**: List all tables in the MDB file.
- **Usage**:
  ```bash
  python3 mdb_query.py -f database.mdb -a list
  ```
- **Output**:
  ```
  2025-05-15 17:29:00 - INFO - Tables found: users, orders, products
  ```
- **JSON File** (`output_dir/logs/mdb_query_20250515_172900.json`):
  ```json
  {
    "mdb_file": "/path/to/database.mdb",
    "output_dir": "output_dir",
    "actions": [
      {
        "mdb_file": "/path/to/database.mdb",
        "action": "List Tables",
        "status": "Tables: users, orders, products",
        "output_path": "",
        "timestamp": "2025-05-15 17:29:00"
      }
    ],
    "timestamp": "2025-05-15 17:29:00"
  }
  ```
- **Tips**: Use to explore MDB file structure before querying.

#### SQL Queries
- **Purpose**: Execute SQL queries and export results.
- **Usage**:
  ```bash
  python3 mdb_query.py -f database.mdb -a query -q "SELECT * FROM users WHERE age > 18" -o users.csv
  ```
- **Output**:
  ```
  2025-05-15 17:29:00 - INFO - Query returned 10 rows
  2025-05-15 17:29:00 - INFO - Results saved to output_dir/users.csv
  ```
- **Result File** (`output_dir/users.csv`):
  ```
  id,name,age
  1,Alice,25
  2,Bob,30
  ...
  ```
- **Tips**: Use `--format sqlite` for SQLite export; combine with **PatternSentry** to analyze results.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  python3 mdb_query.py -f database.mdb -a list --quiet
  ```
- **Tips**: Monitor `mdb_query.log` with `tail -f mdb_query.log`.

### Workflow
1. Set up lab (Ubuntu 24.04 with required packages installed).
2. Install dependencies:
   ```bash
   ./setup_mdb_query.sh
   ```
3. List tables:
   ```bash
   python3 mdb_query.py -f database.mdb -a list
   ```
4. Execute a query:
   ```bash
   python3 mdb_query.py -f database.mdb -a query -q "SELECT * FROM users" -o users.csv
   ```
5. Monitor output in terminal or `mdb_query.log`.
6. Check results in `mdb_query-output/logs/` (text, JSON, SQLite).
7. Secure outputs (`rm -rf mdb_query-output/*`).

## Output
- **Logs**: `mdb_query.log`, e.g.:
  ```
  2025-05-15 17:29:00 - INFO - Connected to MDB file: /path/to/database.mdb
  2025-05-15 17:29:00 - INFO - Tables found: users, orders
  2025-05-15 17:29:01 - INFO - Results saved to output_dir/logs/mdb_query_20250515_172900.json
  ```
- **Results**: `mdb_query-output/logs/mdb_query_<timestamp>.json` and result files.
- **Database**: `mdb_query-output/logs/mdb_query.db` (SQLite).

## Notes
- **Environment**: Use on MDB files you own or have permission to access in your lab.
- **Impact**: Queries and exports data for analysis; requires manual verification.
- **Ethics**: Avoid unauthorized access to prevent legal or ethical issues.
- **Dependencies**: Requires `pyodbc`, `pandas`, `mdbtools`, `unixodbc`.
- **Root**: Not required for execution, but required for installing MDB Tools and ODBC drivers.
- **Sources**: Built for MDB file management, leveraging concepts from MDB Tools and MDB Admin.

## Disclaimer
**Personal Use Only**: MDBQuery is for educational testing of MDB files you own or have permission to access. Unauthorized database access may violate laws or terms of service. Ensure compliance with local laws, including cybersecurity and data protection regulations.

**Safe Use**:
- Use in a private lab (e.g., Ubuntu 24.04).
- Secure outputs (`mdb_query.log`, `mdb_query-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Accessing proprietary databases without permission.
- Sharing extracted data.
- Using in production environments.

## Limitations
- **Scope**: CLI-based; lacks GUI (unlike MDB Admin).
- **Dependencies**: Relies on `mdbtools` and `pyodbc` for MDB access.
- **Compatibility**: Supports MDB files; ACCDB requires additional drivers.
- **Features**: Basic querying and export; no advanced features like forms or reports.

## Tips
- Use with **PatternSentry** to scan exported data for vulnerabilities.
- Test on sample MDB files before real databases.
- Combine with **NetSentry** for network analysis or **IdentityForge** for credential testing.
- Review OWASP Database Security Cheat Sheet for secure database practices.

## License
For personal educational use; no formal license. Use responsibly.