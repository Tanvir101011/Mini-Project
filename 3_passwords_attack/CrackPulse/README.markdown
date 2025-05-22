# CrackPulse

## Description
CrackPulse is a Python tool for cracking password hashes locally in your private lab, inspired by **Hashcat**. It supports dictionary and brute-force attacks for algorithms like MD5, SHA1, SHA256, and NTLM, with multi-threaded performance. Designed for educational purposes, it generates results in text and JSON formats, complementing tools like **HashSnipe** or **WordForge** in your lab (e.g., Ubuntu 24.04, home network).

**Important**: Use CrackPulse only on hashes from systems you own or have explicit permission to test. Unauthorized cracking is illegal and may lead to legal consequences or ethical issues. The tool is restricted to your lab to ensure responsible use.

## Features
- **Hash Cracking**: Performs dictionary and brute-force attacks locally.
- **Supported Algorithms**: MD5, SHA1, SHA256, NTLM.
- **JSON Output**: Saves results in JSON for parsing/automation.
- **Multi-Threading**: Optimizes dictionary attacks with configurable threads.
- **Configurable**: Supports single hashes, files, wordlists, charsets, and length ranges.
- **Logging**: Saves logs to `crackpulse.log` and results to `crackpulse-output/`.
- **Quiet Mode**: Minimizes terminal output.
- **Educational**: Simple design for learning hash cracking.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Private network you control.
2. **Install Dependencies**:
   - Save `setup_crackpulse.sh` to a directory (e.g., `/home/user/crackpulse/`).
   - Make executable and run:
     ```bash
     chmod +x setup_crackpulse.sh
     ./setup_crackpulse.sh
     ```
   - Installs Python and creates sample files.
3. Save `crackpulse.py` to the same directory.
4. Verify:
   ```bash
   python3 crackpulse.py --help
   ```

## Usage
CrackPulse cracks hashes using local dictionary or brute-force attacks. Below are examples and expected outcomes.

### Basic Commands
Crack a single MD5 hash with a wordlist:
```bash
python3 crackpulse.py md5 -h 098f6bcd4621d373cade4e832627b4f6 -w wordlist.txt
```

Crack multiple hashes with brute-force:
```bash
python3 crackpulse.py sha1 -f hashes.txt -c abc123 -m 1 -M 3 -t 8
```

### Options
- `algorithm`: Hash algorithm (required, e.g., `md5`, `sha1`).
- `-h, --hash`: Single hash value.
- `-f, --file`: File with one hash per line.
- `-w, --wordlist`: Wordlist file for dictionary attack.
- `-c, --charset`: Character set for brute-force (default: `abcdefghijklmnopqrstuvwxyz`).
- `-m, --min-len`: Minimum length for brute-force (default: 1).
- `-M, --max-len`: Maximum length for brute-force (default: 4).
- `-t, --threads`: Number of threads (default: 4).
- `-q, --quiet`: Log to file only.

### Features

#### Dictionary Attack
- **Purpose**: Crack hashes using a wordlist.
- **Usage**:
  ```bash
  python3 crackpulse.py md5 -h 098f6bcd4621d373cade4e832627b4f6 -w wordlist.txt
  ```
- **Output**:
  ```
  2025-05-15 13:10:00 - INFO - Starting CrackPulse: algorithm=md5, output=crackpulse-output/results_md5_20250515_131000.txt
  2025-05-15 13:10:01 - INFO - Hash cracked: 098f6bcd4621d373cade4e832627b4f6 -> test
  ```
- **Result File** (`crackpulse-output/results_md5_20250515_131000.txt`):
  ```
  [2025-05-15 13:10:01] Hash: 098f6bcd4621d373cade4e832627b4f6 (md5)
  Cracked: test
  ```
- **JSON File** (`crackpulse-output/results_md5_20250515_131000.json`):
  ```json
  {
    "algorithm": "md5",
    "hashes": [
      {
        "hash": "098f6bcd4621d373cade4e832627b4f6",
        "algorithm": "md5",
        "attempts": [
          {"status": "success", "password": "test", "hash": "098f6bcd4621d373cade4e832627b4f6"}
        ]
      }
    ],
    "timestamp": "2025-05-15 13:10:01",
    "total_cracked": 1
  }
  ```
- **Tips**: Generate wordlists with **WordForge** (`python3 wordforge.py -m 4 -M 4 -c test -o wordlist.txt`).

#### Brute-Force Attack
- **Purpose**: Crack hashes with generated combinations.
- **Usage**:
  ```bash
  python3 crackpulse.py sha1 -h a94a8fe5ccb19ba61c4c0873d391e987982fbbd3 -c ab -m 4 -M 4
  ```
- **Output**:
  ```
  2025-05-15 13:10:02 - INFO - Starting brute-force attack on a94a8fe5ccb19ba61c4c0873d391e987982fbbd3, lengths 4-4
  ```
- **Tips**: Use small charsets/lengths to avoid long runtimes.

### Workflow
1. Set up lab (VM on Ubuntu 24.04).
2. Install dependencies:
   ```bash
   ./setup_crackpulse.sh
   ```
3. Create a hash file (e.g., `echo "098f6bcd4621d373cade4e832627b4f6" > hashes.txt`).
4. Run CrackPulse:
   ```bash
   python3 crackpulse.py md5 -f hashes.txt -w wordlist.txt
   ```
5. Check logs (`crackpulse.log`) and results (`crackpulse-output/`).
6. Secure outputs (`rm -rf crackpulse-output/*`).

## Output
- **Logs**: `crackpulse.log`, e.g.:
  ```
  2025-05-15 13:10:00 - INFO - Starting CrackPulse: algorithm=md5
  2025-05-15 13:10:01 - INFO - Hash cracked: 098f6bcd4621d373cade4e832627b4f6 -> test
  ```
- **Results**: `crackpulse-output/results_<algorithm>_<timestamp>.txt` and `.json`.

## Notes
- **Environment**: Use on authorized hashes in your lab.
- **Performance**: Brute-force is slow for large charsets/lengths; use wordlists for efficiency.
- **Ethics**: Unauthorized cracking is illegal and unethical.

## Disclaimer
**Personal Use Only**: CrackPulse is for learning on systems you own or have permission to test. Unauthorized use is illegal and may lead to legal consequences or ethical issues. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM on home network).
- Secure outputs (`crackpulse.log`, `crackpulse-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Cracking hashes from unauthorized systems.
- Sharing output files.
- Production environments to prevent misuse.

## Limitations
- Supports fewer algorithms than **Hashcat** (e.g., no bcrypt, GPU optimization).
- Brute-force is CPU-based; **Hashcat** uses GPU for speed.
- Limited to unsalted hashes.

## Tips
- Generate test hashes with `echo -n "test" | md5sum`.
- Use **WordForge** for wordlists (`python3 wordforge.py -c abc123 -m 1 -M 4`).
- Test in a lab with known hashes.
- Monitor CPU usage (`top`) during brute-force.
- Isolate setup to avoid misuse.

## License
For personal educational use; no formal license. Use responsibly.