# WordForge

## Description
WordForge is a Python tool for generating custom wordlists in your private lab, inspired by Crunch. It creates all possible combinations and permutations of a given character set or pattern for security testing (e.g., brute-forcing passwords). Designed for personal experimentation, it generates wordlists in text and JSON formats, targeting tools like **ForceBreach** or **NetBrute** in your lab setup (e.g., Ubuntu 24.04, home network).

**Important**: Use WordForge only for authorized security testing on systems you own or have explicit permission to test. Generating wordlists for unauthorized use is illegal and may lead to legal consequences or ethical issues. The tool is restricted to your lab to ensure responsible use.

## Features
- **Wordlist Generation**: Creates combinations for specified lengths and charsets.
- **Pattern Support**: Generates words based on patterns (e.g., `@` for letters, `#` for digits).
- **JSON Output**: Saves wordlists in JSON for parsing/automation.
- **Configurable**: Supports min/max lengths, custom charsets, and output files.
- **Logging**: Saves logs to `wordforge.log` and results to specified files.
- **Quiet Mode**: Minimizes terminal output.
- **Educational**: Simple design for learning wordlist generation.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Private network you control.
2. **Install Dependencies**:
   - Save `setup_wordforge.sh` to a directory (e.g., `/home/user/wordforge/`).
   - Make executable and run:
     ```bash
     chmod +x setup_wordforge.sh
     ./setup_wordforge.sh
     ```
   - Installs Python dependencies (none required for core functionality).
3. Save `wordforge.py` to the same directory.
4. Verify:
   ```bash
   python3 wordforge.py --help
   ```

## Usage
WordForge generates wordlists for security testing. Below are examples and expected outcomes.

### Basic Commands
Generate a wordlist with lowercase letters:
```bash
python3 wordforge.py -m 2 -M 3 -c abc -o wordlist.txt
```

Generate a patterned wordlist with JSON output:
```bash
python3 wordforge.py -p @@## -o pattern_list.txt -j -q
```

### Options
- `-m, --min-len`: Minimum word length (default: 1).
- `-M, --max-len`: Maximum word length (default: 4).
- `-c, --charset`: Character set (default: `abcdefghijklmnopqrstuvwxyz`).
- `-p, --pattern`: Pattern (e.g., `@@##` for two letters, two digits).
- `-o, --output`: Output file (default: `wordforge_list_<timestamp>.txt`).
- `-j, --json`: Generate JSON output.
- `-q, --quiet`: Log to file only.

### Features

#### Wordlist Generation
- **Purpose**: Create combinations for brute-forcing.
- **Usage**:
  ```bash
  python3 wordforge.py -m 2 -M 3 -c abc -o wordlist.txt
  ```
- **Output**:
  ```
  2025-05-15 13:01:00 - INFO - Starting WordForge: min_len=2, max_len=3, charset=abc, output=wordlist.txt
  2025-05-15 13:01:01 - INFO - Wordlist generation complete. 39 words saved to wordlist.txt
  ```
- **Result File** (`wordlist.txt`):
  ```
  aa
  ab
  ac
  ba
  ...
  ccc
  ```
- **Tips**: Use with tools like `forcebreach.py` (`python3 forcebreach.py -u wordlist.txt -w wordlist.txt`).

#### Pattern-Based Generation
- **Purpose**: Generate words with specific formats.
- **Usage**:
  ```bash
  python3 wordforge.py -p @@## -o pattern_list.txt -j
  ```
- **Output**:
  ```
  2025-05-15 13:01:02 - INFO - Starting WordForge: min_len=1, max_len=4, charset=abcdefghijklmnopqrstuvwxyz, output=pattern_list.txt
  2025-05-15 13:01:03 - INFO - Wordlist generation complete. 67600 words saved to pattern_list.txt
  ```
- **Result File** (`pattern_list.txt`):
  ```
  aa00
  aa01
  ...
  zz99
  ```
- **JSON File** (`pattern_list.json`):
  ```json
  {
    "min_len": 1,
    "max_len": 4,
    "charset": "abcdefghijklmnopqrstuvwxyz",
    "pattern": "@@##",
    "word_count": 67600,
    "words": ["aa00", "aa01", ..., "zz99"],
    "timestamp": "2025-05-15 13:01:03"
  }
  ```
- **Tips**: Patterns: `@` (letters), `#` (digits), `%` (symbols).

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  python3 wordforge.py -m 2 -M 3 -c abc -q
  ```
- **Tips**: Check `wordforge.log` with `tail -f wordforge.log`.

### Workflow
1. Set up lab (VM on Ubuntu 24.04).
2. Install dependencies:
   ```bash
   ./setup_wordforge.sh
   ```
3. Generate wordlist:
   ```bash
   python3 wordforge.py -m 2 -M 3 -c abc -o wordlist.txt -j
   ```
4. Check logs (`wordforge.log`) and results (`wordlist.txt`, `.json`).
5. Use with brute-force tools (e.g., `forcebreach.py`, `netbrute.py`).
6. Stop with `Ctrl+C`; secure outputs (`rm wordforge_*.txt wordforge_*.json`).

## Output
- **Logs**: `wordforge.log`, e.g.:
  ```
  2025-05-15 13:01:00 - INFO - Starting WordForge: min_len=2, max_len=3
  2025-05-15 13:01:01 - INFO - Wordlist generation complete. 39 words saved
  ```
- **Results**: `<output>.txt` and `.json` (if `-j`), e.g.:
  ```
  aa
  ab
  ...
  ```

## Notes
- **Environment**: Use for authorized testing (e.g., lab brute-forcing).
- **Performance**: Large wordlists may consume disk space; test small sets first.
- **Ethics**: Avoid unauthorized use to prevent legal/ethical issues.

## Disclaimer
**Personal Use Only**: WordForge is for learning on systems you own or have permission to test. Unauthorized use is illegal and may lead to legal consequences or ethical issues. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM on home network).
- Secure outputs (`wordforge.log`, `wordforge_*.txt/json`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Generating wordlists for unauthorized systems.
- Sharing sensitive wordlists.
- Production environments to prevent misuse.

## Limitations
- Supports basic combinations and patterns; Crunch offers more advanced features (e.g., regex).
- JSON output may be large for big wordlists; use sparingly.
- Performance depends on system resources and charset size.

## Tips
- Start with small charsets/lengths (`-c abc -m 1 -M 2`).
- Use patterns for targeted lists (`-p @@##`).
- Test with **ForceBreach** or **NetBrute** in your lab.
- Monitor disk space (`du -sh wordlist.txt`).
- Isolate setup to avoid misuse.

## License
For personal educational use; no formal license. Use responsibly.