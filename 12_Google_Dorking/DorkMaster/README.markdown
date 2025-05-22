# DorkMaster

## Overview
DorkMaster is a command-line tool for cybersecurity researchers and OSINT analysts to automate Google Dork searches from the Linux terminal, designed for Kali Linux. It facilitates advanced search query construction using Google's search operators to identify sensitive data, vulnerabilities, or specific web content, suitable for security assessments and reconnaissance.

## Features
- Supports predefined dork categories (e.g., exposed files, login pages, CCTV cameras, FTP servers, SQL dumps).
- Allows custom dork query construction with operators like `intitle:`, `inurl:`, `site:`, `filetype:`.
- Scrapes Google search results (up to 10 per query) for URLs, titles, and snippets.
- Outputs results to CSV for further analysis.
- Includes optional proxy support to avoid IP bans.
- Logs queries and results with timestamps for auditability.
- Handles CAPTCHA detection and rate-limiting with random delays.
- Optimized for Kali Linux.

## Prerequisites
- Kali Linux (or similar environment)
- Python 3.6 or higher
- Python libraries: `requests`, `beautifulsoup4` (installed via setup script)
- Input: Internet connection and valid Google search access
- Optional: Proxy server for anonymity

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
python dorkmaster.py [-c <category> | -q <query>] [-o <output-dir>] [-p <proxy>] [--verbose]
```

- **-c, --category**: Predefined dork category (`files`, `login`, `cameras`, `ftp`, `sql`, `exposed`).
- **-q, --query**: Custom dork query (e.g., `inurl:login site:*.edu`).
- **-o, --output-dir**: Output directory (default: `dorkmaster_output`).
- **-p, --proxy**: Proxy URL (e.g., `http://proxy:port`).
- **--verbose**: Print detailed results.

### Examples
1. **Search for exposed PDF files on educational sites**:
   ```bash
   python dorkmaster.py -c files -o results --verbose
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Executing query: filetype:pdf site:*.edu confidential
   2025-05-15 18:30:00 - INFO - URL: https://example.edu/confidential.pdf
   2025-05-15 18:30:00 - INFO - Title: Confidential Report
   2025-05-15 18:30:00 - INFO - Snippet: This document contains sensitive information...
   2025-05-15 18:30:00 - INFO - Results saved to results/results_20250515_183000.csv
   2025-05-15 18:30:00 - INFO - Summary appended to results/summary.txt
   2025-05-15 18:30:00 - INFO - Search complete. Results in results
   ```

2. **Search for custom query (admin panels on government sites)**:
   ```bash
   python dorkmaster.py -q "inurl:admin site:*.gov" -o results -p http://proxy:8080
   ```
   Output:
   ```
   2025-05-15 18:30:00 - INFO - Executing query: inurl:admin site:*.gov
   2025-05-15 18:30:00 - INFO - Results saved to results/results_20250515_183000.csv
   2025-05-15 18:30:00 - INFO - Summary appended to results/summary.txt
   2025-05-15 18:30:00 - INFO - Search complete. Results in results
   ```

### Output Files
- **Results CSV** (e.g., `results_20250515_183000.csv`):
  ```csv
  url,title,snippet,query,timestamp
  https://example.edu/confidential.pdf,Confidential Report,This document contains sensitive information...,filetype:pdf site:*.edu confidential,2025-05-15T18:30:00
  ```
- **Summary Report** (`summary.txt`):
  ```
  DorkMaster Summary Report - 2025-05-15T18:30:00
  --------------------------------------------------
  Query: filetype:pdf site:*.edu confidential
  Results Found: 8
  URL: https://example.edu/confidential.pdf
  Title: Confidential Report
  Snippet: This document contains sensitive information...
  ...
  --------------------------------------------------
  ```

## Limitations
- Limited to 10 results per query due to Google’s scraping restrictions.
- May encounter CAPTCHAs or rate-limiting; use proxies or Tor for heavy usage.
- Scraping-based; results depend on Google’s indexing and availability.
- No support for other search engines (e.g., Bing, DuckDuckGo) in this version.
- Simplified parsing; complex pages may require manual inspection.
- Assumes stable internet and Google access; blocks may require VPN/Tor.

## License
MIT License

## Warning
DorkMaster is for ethical security research and authorized OSINT only. Unauthorized use to access or exploit systems you do not own or have permission to analyze is illegal and unethical. Always obtain explicit permission before querying or accessing systems. The author is not responsible for misuse.

## Recommendations
- Use Tor or a VPN for anonymity (see Tor Browser or Tails documentation).
- Rotate proxies to avoid IP bans.
- Test with benign queries to avoid triggering Google’s anti-bot measures.
- Combine with manual analysis for sensitive investigations.