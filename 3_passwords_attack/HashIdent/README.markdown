# HashIDent

## Description
HashIDent is a Python tool for identifying hash algorithms in your private lab, inspired by **Hash Identifier**. It analyzes hashes based on length, character set, and patterns to determine likely types (e.g., MD5, SHA1, SHA256, NTLM). Designed for educational purposes, it generates results in text and JSON formats, suitable for use with tools like **HashSnipe** or **WordForge** in your lab (e.g., Ubuntu 24.04, home network).

**Important**: Use HashIDent only on hashes from systems you own or have explicit permission to test. Analyzing unauthorized hashes may be illegal or unethical. The tool is restricted to your lab to ensure responsible use.

## Features
- **Hash Identification**: Detects algorithms like MD4, MD5, SHA1, SHA256, NTLM, bcrypt, and more.
- **JSON Output**: Saves results in JSON for parsing/automation.
- **Configurable**: Supports single hashes or files, with quiet mode.
- **Logging**: Saves logs to `hashident.log` and results to `hashident-output/`.
- **Educational**: Simple design for learning hash formats.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Private network you control.
2. **Install Dependencies**:
   - Save `setup_hashident.sh` to a directory (e.g., `/home/user/hashident/`).
   - Make executable and run:
     ```bash
     chmod +x setup_hashident.sh
     ./setup_hashident.sh
     ```
   - Installs Python dependencies (none required for core functionality).
3. Save `hashident.py` to the same directory.
4. Verify:
   ```bash
   python3 hashident.py --help
   ```

## Usage
HashIDent identifies hash types based on their format. Below are examples and expected outcomes.

### Basic Commands
Identify a single hash:
```bash
python3 hashident.py -h 098f6bcd4621d373cade4e832627b4f6
```

Identify multiple hashes from a file in quiet mode:
```bash
python3 hashident.py -f hashes.txt -j -q
```

### Options
- `-h, --hash`: Single hash value.
- `-f, --file`: File with one hash per line.
- `-j, --json`: Generate JSON output.
- `-q, --quiet`: Log to file only.

### Features

#### Hash Identification
- **Purpose**: Determine hash algorithms.
- **Usage**:
  ```bash
  python3 hashident.py -h 098f6bcd4621d373cade4e832627b4f6
  ```
- **Output**:
  ```
  2025-05-15 13:10:00 - INFO - Starting HashIDent: output=hashident-output/results_20250515_131000.txt
  2025-05-15 13:10:00 - INFO - Hash: 098f6bcd4621d373cade4e832627b4f6
    Possible: MD5 (Confidence: 90.00%) - Length: 32, Regex: ^[0-9a-fA-F]{32}$
    Possible: MD4 (Confidence: 90.00%) - Length: 32, Regex: ^[0-9a-fA-F]{32}$
    Possible: NTLM (Confidence: 80.00%) - Length: 32, Regex: ^[0-9a-fA-F]{32}$
    Possible: LM (Confidence: 70.00%) - Length: 32, Regex: ^[0-9a-fA-F]{32}$
  ```
- **Result File** (`hashident-output/results_20250515_131000.txt`):
  ```
  [2025-05-15 13:10:00] Hash: 098f6bcd4621d373cade4e832627b4f6
    MD5: Confidence 90.00% - Length: 32, Regex: ^[0-9a-fA-F]{32}$
    MD4: Confidence 90.00% - Length: 32, Regex: ^[0-9a-fA-F]{32}$
    NTLM: Confidence 80.00% - Length: 32, Regex: ^[0-9a-fA-F]{32}$
    LM: Confidence 70.00% - Length: 32, Regex: ^[0-9a-fA-F]{32}$
  ```
- **JSON File** (`hashident-output/results_20250515_131000.json`, if `-j`):
  ```json
  {
    "results": [
      {
        "hash": "098f6bcd4621d373cade4e832627b4f6",
        "possible_types": [
          {"algorithm": "MD5", "confidence": 0.9, "details": "Length: 32, Regex: ^[0-9a-fA-F]{32}$"},
          {"algorithm": "MD4", "confidence": 0.9, "details": "Length: 32, Regex: ^[0-9a-fA-F]{32}$"},
          {"algorithm": "NTLM", "confidence": 0.8, "details": "Length: 32, Regex: ^[0-9a-fA-F]{32}$"},
          {"algorithm": "LM", "confidence": 0.7, "details": "Length: 32, Regex: ^[0-9a-fA-F]{32}$"}
        ]
      }
    ],
    "timestamp": "2025-05-15 13:10:00",
    "total_hashes": 1
  }
  ```
- **Tips**: Use with **HashSnipe** (`python3 hashsnipe.py MD5 -h 098f6bcd4621d373cade4e832627b4f6`).

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  python3 hashident.py -h 098f6bcd4621d373cade4e832627b4f6 -q
  ```
- **Tips**: Check `hashident.log` with `tail -f hashident.log`.

### Workflow
1. Set up lab (VM on Ubuntu 24.04).
2. Install dependencies:
   ```bash
   ./setup_hashident.sh
   ```
3. Create a hash file (e.g., `echo "098f6bcd4621d373cade4e832627b4f6" > hashes.txt`).
4. Run HashIDent:
   ```bash
   python3 hashident.py -f hashes.txt -j
   ```
5. Check logs (`hashident.log`) and results (`hashident-output/`).
6. Use results with **HashSnipe** or **ForceBreach**.
7. Secure outputs (`rm -rf hashident-output/*`).

## Output
- **Logs**: `hashident.log`, e.g.:
  ```
  2025-05-15 13:10:00 - INFO - Starting HashIDent: output=hashident-output/results_20250515_131000.txt
  2025-05-15 13:10:00 - INFO - Hash: 098f6bcd4621d373cade4e832627b4f6
  ```
- **Results**: `hashident-output/results_<timestamp>.txt` and `.json` (if `-j`).

## Notes
- **Environment**: Use on authorized hashes in your lab.
- **Accuracy**: Identification is heuristic; some hashes (e.g., MD5 vs. NTLM) may overlap.
- **Ethics**: Avoid analyzing unauthorized hashes to prevent legal/ethical issues.

## Disclaimer
**Personal Use Only**: HashIDent is for learning on systems you own or have permission to test. Analyzing unauthorized hashes may be illegal or unethical. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM on home network).
- Secure outputs (`hashident.log`, `hashident-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Analyzing sensitive or corporate hashes.
- Sharing output files.
- Production environments to prevent misuse.

## Limitations
- Heuristic-based; **Hash Identifier** may use additional checks (e.g., context).
- Limited to common algorithms; extend `hash_patterns` for more types.
- Overlapping formats (e.g., MD5/NTLM) reduce confidence.

## Tips
- Generate test hashes with `echo -n "test" | md5sum`.
- Use with **HashSnipe** for cracking identified hashes.
- Test in a lab with known hashes.
- Monitor results with `cat hashident-output/*.txt`.
- Isolate setup to avoid misuse.

## License
For personal educational use; no formal license. Use responsibly.