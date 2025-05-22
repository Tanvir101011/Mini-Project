# HashSnipe

## Description
HashSnipe is a Python tool for cracking password hashes in your private lab, inspired by **findmyhash**. It queries free online hash-cracking services (e.g., CrackStation, Hashes.com) to identify and crack hashes for algorithms like MD5, SHA1, SHA256, and NTLM. Designed for educational purposes, it generates results in text and JSON formats, suitable for use with tools like **WordForge** or **ForceBreach** in your lab (e.g., Ubuntu 24.04, home network).

**Important**: Use HashSnipe only on hashes from systems you own or have explicit permission to test. Submitting hashes to online services may expose sensitive data and is illegal without authorization. The tool is restricted to your lab to ensure ethical use.

## Features
- **Hash Cracking**: Queries online services for hash lookups.
- **Supported Algorithms**: MD4, MD5, SHA1, SHA224, SHA256, SHA384, SHA512, NTLM, MySQL, LDAP_MD5, LDAP_SHA1.
- **JSON Output**: Saves results in JSON for parsing/automation.
- **Google Search**: Searches uncracked hashes on Google (single hash only).
- **Configurable**: Supports single hashes or files, with quiet mode.
- **Logging**: Saves logs to `hashsnipe.log` and results to `hashsnipe-output/`.
- **Educational**: Simple design for learning hash cracking.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Internet access for API queries.
   - Private network you control.
2. **Install Dependencies**:
   - Save `setup_hashsnipe.sh` to a directory (e.g., `/home/user/hashsnipe/`).
   - Make executable and run:
     ```bash
     chmod +x setup_hashsnipe.sh
     ./setup_hashsnipe.sh
     ```
   - Installs `requests` and creates sample hash files.
3. Save `hashsnipe.py` to the same directory.
4. Verify:
   ```bash
   python3 hashsnipe.py --help
   ```

## Usage
HashSnipe cracks hashes by querying online services. Below are examples and expected outcomes.

### Basic Commands
Crack a single MD5 hash:
```bash
python3 hashsnipe.py MD5 -h 098f6bcd4621d373cade4e832627b4f6
```

Crack multiple hashes from a file with Google search:
```bash
python3 hashsnipe.py SHA1 -f hashes.txt -g -q
```

### Options
- `algorithm`: Hash algorithm (required, e.g., `MD5`, `SHA1`).
- `-h, --hash`: Single hash value.
- `-f, --file`: File with one hash per line.
- `-g, --google`: Search uncracked hash on Google (single hash only).
- `-q, --quiet`: Log to file only.

### Features

#### Hash Cracking
- **Purpose**: Crack hashes using online services.
- **Usage**:
  ```bash
  python3 hashsnipe.py MD5 -h 098f6bcd4621d373cade4e832627b4f6
  ```
- **Output**:
  ```
  2025-05-15 13:05:00 - INFO - Starting HashSnipe: algorithm=MD5, output=hashsnipe-output/results_md5_20250515_130500.txt
  2025-05-15 13:05:01 - INFO - Hash cracked: 098f6bcd4621d373cade4e832627b4f6 -> test (CrackStation)
  ```
- **Result File** (`hashsnipe-output/results_md5_20250515_130500.txt`):
  ```
  [2025-05-15 13:05:01] Hash: 098f6bcd4621d373cade4e832627b4f6 (MD5)
  CrackStation: SUCCESS - Password: test - Hash cracked
  Hashes.com: FAILED - Hash not found
  ```
- **JSON File** (`hashsnipe-output/results_md5_20250515_130500.json`):
  ```json
  {
    "algorithm": "MD5",
    "hashes": [
      {
        "hash": "098f6bcd4621d373cade4e832627b4f6",
        "algorithm": "MD5",
        "results": [
          {"service": "CrackStation", "status": "success", "password": "test", "message": "Hash cracked"},
          {"service": "Hashes.com", "status": "failed", "password": null, "message": "Hash not found"}
        ]
      }
    ],
    "timestamp": "2025-05-15 13:05:01",
    "total_hashes": 1
  }
  ```
- **Tips**: Generate test hashes with **WordForge** (`python3 wordforge.py -m 4 -M 4 -c test`).

#### Google Search
- **Purpose**: Search uncracked hashes on Google.
- **Usage**:
  ```bash
  python3 hashsnipe.py SHA1 -h a94a8fe5ccb19ba61c4c0873d391e987982fbbd3 -g
  ```
- **Output**:
  ```
  2025-05-15 13:05:02 - INFO - Google results for a94a8fe5ccb19ba61c4c0873d391e987982fbbd3: Mock Google result
  ```
- **Tips**: Requires internet; results vary by hash.

### Workflow
1. Set up lab (VM on Ubuntu 24.04).
2. Install dependencies:
   ```bash
   ./setup_hashsnipe.sh
   ```
3. Create a hash file (e.g., `echo "098f6bcd4621d373cade4e832627b4f6" > hashes.txt`).
4. Run HashSnipe:
   ```bash
   python3 hashsnipe.py MD5 -f hashes.txt
   ```
5. Check logs (`hashsnipe.log`) and results (`hashsnipe-output/`).
6. Secure outputs (`rm -rf hashsnipe-output/*`).

## Output
- **Logs**: `hashsnipe.log`, e.g.:
  ```
  2025-05-15 13:05:00 - INFO - Starting HashSnipe: algorithm=MD5
  2025-05-15 13:05:01 - INFO - Hash cracked: 098f6bcd4621d373cade4e832627b4f6 -> test
  ```
- **Results**: `hashsnipe-output/results_<algorithm>_<timestamp>.txt` and `.json`.

## Notes
- **Environment**: Use on authorized hashes in your lab.
- **Privacy**: Online APIs may log hashes; avoid sensitive data.
- **Ethics**: Unauthorized use is illegal and risky.
- **API Limits**: Services may have rate limits or require registration.

## Disclaimer
**Personal Use Only**: HashSnipe is for learning on systems you own or have permission to test. Submitting hashes to online services may expose data and is illegal without authorization. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM on home network).
- Secure outputs (`hashsnipe.log`, `hashsnipe-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Submitting sensitive or corporate hashes to online services.
- Sharing output files.
- Production environments to prevent misuse.

## Limitations
- Depends on online services; **findmyhash** queries more sites.
- Google search is a placeholder; implement a real API for full functionality.
- Limited to unsalted hashes for most services.

## Tips
- Generate test hashes with `echo -n "test" | md5sum`.
- Use with **WordForge** for custom wordlists.
- Test in a lab with known hashes.
- Monitor network traffic with Wireshark.
- Isolate setup to avoid misuse.

## License
For personal educational use; no formal license. Use responsibly.