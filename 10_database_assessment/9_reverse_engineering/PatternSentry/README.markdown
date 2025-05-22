# PatternSentry

## Description
PatternSentry is a Python-based tool designed for ethical malware analysis in your private lab (Ubuntu 24.04, home network). It enables creating and applying pattern-matching rules to detect specific textual or binary patterns in files, aiding in identifying and classifying malware samples. The tool features a CLI interface, SQLite logging, JSON output, and a modular design, integrating with your tools like **APKForge**, **Dex2Java**, **SmaliCraft**, **NetSentry**, **NatPiercer**, **WiFiCrush**, **IdentityForge**, **IAXStorm**, **SlowStrike**, **SSLBlaze**, **RTPStorm**, and **NetBlitz**.

**Important**: Use PatternSentry only on files you own, have developed, or have explicit permission to analyze. Unauthorized analysis may violate intellectual property laws, terms of service, or ethical standards. This tool is restricted to your lab for responsible use. Ensure compliance with local laws, including copyright and software licensing regulations.

## Features
- **Rule-Based Detection**: Create rules with textual, regex, or binary patterns to match file content.
- **Scanning**: Scan individual files or directories for pattern matches.
- **Flexible Rules**: Supports metadata, text/hex strings, and boolean conditions (e.g., `and`, `or`, `not`).
- **Output Formats**: SQLite database, JSON, and text logs.
- **Logging**: Saves logs to `pattern_sentry.log` and results to `pattern_sentry-output/logs/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Private lab environment.
2. **Install Dependencies**:
   - Save `setup_pattern_sentry.sh` to a directory (e.g., `/home/user/pattern_sentry/`).
   - Make executable and run:
     ```bash
     chmod +x setup_pattern_sentry.sh
     ./setup_pattern_sentry.sh
     ```
   - Installs Python and pip.
3. Save `pattern_sentry.py` to the same directory.
4. Verify:
   ```bash
   python3 pattern_sentry.py --help
   ```

## Usage
PatternSentry facilitates pattern-based file analysis in a controlled lab setting for educational purposes. Below are examples and expected outcomes.

### Basic Commands
Scan a file with a rules file:
```bash
python3 pattern_sentry.py -r rules.yar -t sample.exe -o output_dir
```

Scan a directory:
```bash
python3 pattern_sentry.py -r rules.yar -t samples/ -o output_dir
```

Run in quiet mode:
```bash
python3 pattern_sentry.py -r rules.yar -t sample.exe -o output_dir -q
```

### Options
- `-r, --rules`: Path to rules file (required).
- `-t, --target`: Path to target file or directory (required).
- `-o, --output`: Output directory (default: pattern_sentry-output).
- `-q, --quiet`: Log to file only.

### Rule Syntax
Rules are defined in a `.yar` file with a YARA-like syntax. Example (`rules.yar`):
```
rule silent_banker : banker {
    meta:
        description = "Detects Silent Banker trojan"
        author = "Your Name"
        date = "2025-05-15"
    strings:
        $s1 = "UVODFRYSIHLNWPEJXQZAKCBGMT"
        $s2 = {6A 40 68 00 30 00 00 6A 14 8D 91}
        $s3 = "http://malicious.com" nocase
    condition:
        $s1 or $s2 or ($s3 and not $s1)
}
```
- **meta**: Key-value pairs for rule metadata (e.g., description, author).
- **strings**: Text (`"..."`), hex (`{...}`), or regex patterns with modifiers (e.g., `nocase`).
- **condition**: Boolean expression (e.g., `$s1 or $s2`, `#s1 > 2`, `($s1 and $s2)`).

### Features

τας

#### Scanning
- **Purpose**: Detect patterns in files using custom rules.
- **Usage**:
  ```bash
  python3 pattern_sentry.py -r rules.yar -t sample.exe -o output_dir
  ```
- **Output**:
  ```
  2025-05-15 18:00:00 - INFO - Match for rule silent_banker in sample.exe
  Matches Found:
  - Rule: silent_banker, File: sample.exe
    Matched Strings: s1, s3
    Meta: {'description': 'Detects Silent Banker trojan', 'author': 'Your Name', 'date': '2025-05-15'}
  ```
- **JSON File** (`output_dir/logs/pattern_sentry_20250515_180000.json`):
  ```json
  {
    "target": "sample.exe",
    "rules_file": "rules.yar",
    "output_dir": "output_dir",
    "results": [
      {
        "rule_name": "silent_banker",
        "file": "sample.exe",
        "meta": {
          "description": "Detects Silent Banker trojan",
          "author": "Your Name",
          "date": "2025-05-15"
        },
        "matched_strings": ["s1", "s3"]
      }
    ],
    "actions": [
      {
        "target": "sample.exe",
        "rule_name": "silent_banker",
        "status": "Match for rule silent_banker in sample.exe",
        "output_path": "sample.exe",
        "timestamp": "2025-05-15 18:00:00"
      }
    ],
    "timestamp": "2025-05-15 18:00:00"
  }
  ```
- **Tips**: Combine with **APKForge** to analyze APKs or **SmaliCraft** for .smali pattern matching.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  python3 pattern_sentry.py -r rules.yar -t sample.exe -o output_dir -q
  ```
- **Tips**: Monitor `pattern_sentry.log` with `tail -f pattern_sentry.log`.

### Workflow
1. Set up lab (Ubuntu 24.04 with Python installed).
2. Install dependencies:
   ```bash
   ./setup_pattern_sentry.sh
   ```
3. Create a rules file (`rules.yar`) with desired patterns.
4. Scan a file or directory:
   ```bash
   python3 pattern_sentry.py -r rules.yar -t sample.exe -o output_dir
   ```
5. Monitor output in terminal or `pattern_sentry.log`.
6. Check results in `pattern_sentry-output/logs/` (text, JSON, SQLite).
7. Secure outputs (`rm -rf pattern_sentry-output/*`).

## Output
- **Logs**: `pattern_sentry.log`, e.g.:
  ```
  2025-05-15 18:00:00 - INFO - Match for rule silent_banker in sample.exe
  2025-05-15 18:00:01 - INFO - Results saved to output_dir/logs/pattern_sentry_20250515_180000.json
  ```
- **Results**: `pattern_sentry-output/logs/pattern_sentry_<timestamp>.json` and SQLite database.
- **Database**: `pattern_sentry-output/logs/pattern_sentry.db` (SQLite).

## Notes
- **Environment**: Use on files you own or have permission to analyze in your lab.
- **Impact**: Identifies potential malware for further analysis (e.g., with **Dex2Java** or **SmaliCraft**).
- **Ethics**: Avoid unauthorized analysis to prevent legal/IP issues.
- **Dependencies**: Python-based; no external binaries required.
- **Root**: Not required.
- **Sources**: Built for pattern-based detection, leveraging concepts from malware analysis research.[](https://docs.virustotal.com/docs/what-is-yara)

## Disclaimer
**Personal Use Only**: PatternSentry is for educational analysis of files you own or have permission to study. Unauthorized analysis may violate laws or terms of service. Ensure compliance with local laws, including copyright and software licensing regulations.

**Safe Use**:
- Use in a private lab (e.g., Ubuntu 24.04).
- Secure outputs (`pattern_sentry.log`, `pattern_sentry-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Analyzing proprietary files without permission.
- Distributing scan results or matched files.
- Using in production environments.

## Limitations
- **Scope**: Basic pattern matching; lacks advanced features like PE/ELF parsing or Cuckoo integration.
- **Performance**: Python-based; slower than C-based tools for large datasets.
- **Interface**: CLI-only; lacks GUI or TUI.
- **Compatibility**: May miss complex obfuscated patterns.

## Tips
- Use **APKForge** to extract files from APKs for scanning.
- Combine with **Dex2Java** for Java decompilation or **SmaliCraft** for .smali analysis.
- Test rules with known samples (e.g., EICAR test file) to avoid false positives.
- Review OWASP Malware Analysis guidelines for best practices.
- Share rules responsibly in private lab settings only.

## License
For personal educational use; no formal license. Use responsibly.