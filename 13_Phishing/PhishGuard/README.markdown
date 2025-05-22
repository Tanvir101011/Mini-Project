# PhishGuard

## Overview
PhishGuard is a command-line phishing database management tool for ethical cybersecurity researchers and incident responders, designed for Kali Linux. It collects, stores, and analyzes phishing-related data (URLs, emails, domains, IPs) using an SQLite database. PhishGuard supports importing data from CSV files, scraping open-source feeds like PhishTank, querying threats, and generating reports and visualizations for threat analysis.

## Features
- Stores phishing data (URLs, emails, domains, IPs, timestamps, sources) in SQLite.
- Imports data from CSV files or scrapes real-time phishing feeds (e.g., PhishTank).
- Queries data by URL, domain, IP, or date range with flexible filtering.
- Exports query results to CSV for further analysis.
- Categorizes threats (active, mitigated, suspicious) with manual or automated tagging.
- Generates summary reports with statistics (e.g., total entries, top domains).
- Visualizes trends (e.g., phishing domains over time) as PNG plots.
- Logs operations for auditability.
- Optimized for Kali Linux.

## Prerequisites
- Kali Linux (or similar environment)
- Python 3.6 or higher
- Python libraries: `requests`, `beautifulsoup4`, `matplotlib`, `pandas` (installed via setup script)
- Input: Internet connection for scraping, optional CSV files for import
- SQLite (included with Python)

## Installation

### Setup
1. Clone or download the repository.
2. Run the setup script to create a virtual environment and install dependencies:
   ```bash
   chmod +x set_upfile.sh
   ./set_upfile.sh
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

## Usage
Run the tool with:
```bash
python phishguard.py -a <action> [-c <csv>] [-u <url>] [-d <domain>] [-i <ip>] [--date-from <date>] [--date-to <date>] [-s <status>] [-o <output-dir>] [--db <db>] [--verbose]
```

- **-a, --action**: Action to perform (`import`, `scrape`, `query`, `update`, `report`, `plot`).
- **-c, --csv**: CSV file to import (for `import` action).
- **-u, --url**: URL to query or update.
- **-d, --domain**: Domain to query.
- **-i, --ip**: IP to query.
- **--date-from**: Start date for query (YYYY-MM-DD).
- **--date-to**: End date for query (YYYY-MM-DD).
- **-s, --status**: Status to update (`active`, `mitigated`, `suspicious`; for `update` action).
- **-o, --output-dir**: Output directory (default: `phishguard_output`).
- **--db**: Database file (default: `phishguard.db`).
- **--verbose**: Print detailed logs.

### CSV Import Format
```csv
url,domain,ip,email,source,status
http://phish.example.com,phish.example.com,192.168.1.1,phish@bad.com,manual,active
```

### Examples
1. **Import phishing data from CSV**:
   ```bash
   python phishguard.py -a import -c phishing_data.csv -o results --verbose
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Imported data from phishing_data.csv
   ```

2. **Scrape PhishTank for phishing URLs**:
   ```bash
   python phishguard.py -a scrape -o results
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Scraped 10 URLs from PhishTank
   ```

3. **Query phishing data by domain**:
   ```bash
   python phishguard.py -a query -d example.com -o results --verbose
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - URL: http://phish.example.com, Domain: phish.example.com, Status: active
   2025-05-15 18:30:00 - INFO - Exported results to results/query_results.csv
   ```

4. **Update status of a phishing URL**:
   ```bash
   python phishguard.py -a update -u http://phish.example.com -s mitigated
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Updated status of http://phish.example.com to mitigated
   ```

5. **Generate a summary report**:
   ```bash
   python phishguard.py -a report -o results
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Summary saved to results/summary.txt
   ```

6. **Plot phishing domain trends**:
   ```bash
   python phishguard.py -a plot -o results
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Trend plot saved to results/trends.png
   ```

### Output Files
- **Query Results CSV** (`query_results.csv`):
  ```csv
  id,url,domain,ip,email,source,status,added_at
  1,http://phish.example.com,phish.example.com,192.168.1.1,phish@bad.com,csv_import,active,2025-05-15T18:30:00
  ```
- **Summary Report** (`summary.txt`):
  ```
  PhishGuard Summary Report - 2025-05-15T18:30:00
  --------------------------------------------------
  Total Entries: 100
  Status Counts:
    active: 80
    mitigated: 15
    suspicious: 5
  Top 5 Domains:
    phish.example.com: 20
    fake.site: 15
    scam.net: 10
    bad.org: 8
    fraud.com: 5
  --------------------------------------------------
  ```
- **Trend Plot** (`trends.png`): Line graph of top 5 phishing domains over time.

## Limitations
- PhishTank scraping is limited to publicly available data and may face rate-limiting.
- CSV imports require specific column names (url, domain, ip, email, source, status).
- Visualization is basic; advanced analytics may require external tools (e.g., Power BI).
- No automated IP or email validation; manual verification needed for accuracy.
- SQLite is single-user; for multi-user setups, use PostgreSQL or MySQL.
- Assumes stable internet for scraping; offline use requires pre-imported data.

## License
MIT License

## Warning
PhishGuard is for ethical security research and authorized incident response only. Unauthorized use to collect, analyze, or exploit data from systems you do not own or have permission to investigate is illegal and unethical. Always verify the legality of data sources and obtain explicit permission before analyzing systems. The author is not responsible for misuse.

## Recommendations
- Use open-source feeds like PhishTank or OpenPhish for data collection.
- Validate scraped data manually to ensure accuracy.
- Combine with OSINT tools (e.g., Maltego) for deeper analysis.
- Test with controlled datasets in a lab environment.
- Use a VPN for anonymity during scraping.
- Backup the SQLite database regularly.