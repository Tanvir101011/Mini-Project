# PassCrack

## Description
PassCrack is a Python tool for cracking password hashes in your private lab, inspired by **John the Ripper**. It performs dictionary and brute-force attacks on hashes for algorithms like MD5, SHA1, SHA256, and NTLM, generating results in text and JSON formats. Designed for educational purposes, it integrates with tools like **WordForge** and **HashSnipe** in your lab (e.g., Ubuntu 24.04, home network).

**Important**: Use PassCrack only on hashes from systems you own or have explicit permission to test. Unauthorized hash cracking is illegal and may lead to legal consequences or ethical issues. The tool is restricted to your lab to ensure responsible use.

## Features
- **Hash Cracking**: Supports dictionary and brute-force attacks.
- **Supported Algorithms**: MD5, SHA1, SHA256, NTLM.
- **JSON Output**: Saves results in JSON for parsing/automation.
- **Multi-Threading**: Configurable threads for faster cracking.
- **Configurable**: Supports wordlists, charsets, and length ranges.
- **Logging**: Saves logs to `passcrack.log` and results to `passcrack-output/`.
- **Quiet Mode**: Minimizes terminal output.
- **Educational**: Simple design for learning password cracking.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Private network you control.
2. **Install Dependencies**:
   - Save `setup_passcrack.sh` to a directory (e.g., `/home/user/passcrack/`).
   - Make executable and run:
     ```bash
     chmod +x setup_passcrack.sh
     ./setup_passcrack.sh
     ```
   - Installs Python dependencies (none required for core functionality).
3. Save `passcrack.py` to the same directory.
4. Verify:
   ```bash
   python3 passcrack.py --help
   ```

## Usage
PassCrack cracks password hashes using dictionary or brute-force methods. Below are examples and expected outcomes.

### Basic Commands
Crack a single MD5 hash with a wordlist:
```bash
python3 passcrack.py MD5 -h 098f6bcd4621d373cade4e832627b4f6 -w wordlist.txt
```

Crack multiple hashes with brute-force:
```bash
python3 passcrack.py SHA1 -f hashes.txt -c abc123 -m 1 -M 3 -T 10 -q
```

### Options
- `algorithm`: Hash algorithm (required, e.g., `MD5`, `SHA1`).
- `-h, --hash`: Single hash value.
- `-f, --file`: File with one hash per line.
- `-w, --wordlist`: Wordlist file for dictionary attack.
- `-c, --charset`: Character set for brute-force (default: lowercase + digits).
- `-m, --min-len`: Minimum length for brute-force (default: 1).
- `-M, --max-len`: Maximum length for brute-force (default: 4).
- `-T, --threads`: Number of threads (default: 5).
- `-q, --quiet`: Log to file only.

### Features

#### Dictionary Attack
- **Purpose**: Crack hashes using a wordlist.
- **Usage**:
  ```bash
  python3 passcrack.py MD5 -h 098f6bcd4621d373cade4e832627b4f6 -w wordlist.txt
  ```
- **Output**:
  ```
  2025-05-15 13:10:00 - INFO - Starting PassCrack: algorithm=MD5, output=passcrack-output/results_md5_20250515_131000.txt
  2025-05-15 13:10:01 - INFO - Hash cracked: 098f6bcd4621d373cade4e832627b4f6 -> test
  ```
- **Result File** (`passcrack-output/results_md5_20250515_131000.txt`):
  ```
  [2025-05-15 13:10:01] Hash: 098f6bcd4621d373cade4e832627b4f6 (MD5)
  Cracked: test (Hash: 098f6bcd4621d373cade4e832627b4f6)
  ```
- **JSON File** (`passcrack-output/results_md5_20250515_131000.json`):
  ```json
  {
    "algorithm": "MD5",
    "hashes": [
      {
        "hash": "098f6bcd4621d373cade4e832627b4f6",
        "algorithm": "MD5",
        "results": [
          {"password": "test", "hash": "098f6bcd4621d373cade4e832627b4f6", "status": "success"}
        ]
      }
    ],
    "timestamp": "2025-05-15 13:10:01",
    "total_cracked": 1
  }
  ```
- **Tips**: Generate wordlists with **WordForge** (`python3 wordforge.py -m 4 -M 4 -c test`).

#### Brute-Force Attack
- **Purpose**: Crack hashes by trying all combinations.
- **Usage**:
  ```bash
  python3 passcrack.py SHA1 -h a94a8fe5ccb19ba61c4c0873d391e987982fbbd3 -c abc -m 1 -M 4
  ```
- **Output**:
  ```
  2025-05-15 13:10:02 - INFO - Running brute-force attack on a94a8fe5ccb19ba61c4c0873d391e987982fbbd3
  2025-05-15 13:10:03 - INFO - Hash cracked: a94a8fe5ccb19ba61c4c0873d391e987982fbbd3 -> test
  ```
- **Tips**: Use small charsets/lengths to avoid long runtimes.

### Workflow
1. Set up lab (VM on Ubuntu 24.04).
2. Install dependencies:
   ```bash
   ./setup_passcrack.sh
   ```
3. Create a hash file (e.g., `echo "098f6bcd4621d373cade4e832627b4f6" > hashes.txt`).
4. Run PassCrack:
   ```bash
   python3 passcrack.py MD5 -f hashes.txt -w wordlist.txt
   ```
5. Check logs (`passcrack.log`) and results (`passcrack-output/`).
6. Secure outputs (`rm -rf passcrack-output/*`).

## Output
- **Logs**: `passcrack.log`, e.g.:
  ```
  2025-05-15 13:10:00 - INFO - Starting PassCrack: algorithm=MD5
  2025-05-15 13:10:01 - INFO - Hash cracked: 098f6bcd4621d373cade4e832627b4f6 -> test
  ```
- **Results**: `passcrack-output/results_<algorithm>_<timestamp>.txt` and `.json`.

## Notes
- **Environment**: Use on authorized hashes in your lab.
- **Performance**: Brute-force is slow for large charsets/lengths.
- **Ethics**: Unauthorized cracking is illegal and unethical.

## Disclaimer
**Personal Use Only**: PassCrack is for learning on systems you own or have permission to test. Unauthorized hash cracking is illegal and may lead to legal consequences or ethical issues. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM on home network).
- Secure outputs (`passcrack.log`, `passcrack-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Cracking hashes from unauthorized systems.
- Sharing output files.
- Production environments to prevent misuse.

## Limitations
- Supports fewer algorithms than **John the Ripper** (e.g., no bcrypt).
- Brute-force is basic; no incremental mode or advanced rules.
- Performance depends on system resources and charset size.

## Tips
- Generate test hashes with `echo -n "test" | md5sum`.
- Use **WordForge** for custom wordlists.
- Test in a lab with known hashes.
- Monitor CPU usage (`top`) during brute-force.
- Isolate setup to avoid misuse.

## License
For personal educational use; no formal license. Use responsibly.