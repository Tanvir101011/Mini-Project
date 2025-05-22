# SmaliCraft

## Description
SmaliCraft is a Python-based tool designed for ethical reverse engineering in your private lab (Ubuntu 24.04, home network). It disassembles Android Dalvik Executable (.dex) files into .smali code, allows editing of .smali files, and assembles them back into .dex files for further analysis or modification. The tool features a CLI interface, SQLite logging, JSON output, and a modular design, integrating with your tools like **APKForge**, **Dex2Java**, **NetSentry**, **NatPiercer**, **WiFiCrush**, **IdentityForge**, **IAXStorm**, **SlowStrike**, **SSLBlaze**, **RTPStorm**, and **NetBlitz**.

**Important**: Use SmaliCraft only on .dex or .apk files you own, have developed, or have explicit permission to analyze. Unauthorized reverse engineering or modification may violate intellectual property laws, terms of service, or ethical standards. This tool is restricted to your lab for responsible use. Ensure compliance with local laws, including copyright and software licensing regulations.

## Features
- **Disassembly**: Converts .dex files (or .dex from APKs) to .smali code.
- **Assembly**: Rebuilds .smali files into .dex files.
- **Analysis**: Provides basic statistics on .smali files (e.g., file count, lines).
- **APK Support**: Extracts .dex files from APKs for processing.
- **Output Formats**: SQLite database, JSON, and text logs.
- **Logging**: Saves logs to `smali_craft.log` and results to `smali_craft-output/logs/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Smali/Baksmali tools (`smali`, `baksmali` binaries).
   - Private lab environment.
2. **Install Dependencies**:
   - Save `setup_smali_craft.sh` to a directory (e.g., `/home/user/smali_craft/`).
   - Make executable and run:
     ```bash
     chmod +x setup_smali_craft.sh
     ./setup_smali_craft.sh
     ```
   - Installs Python, Smali/Baksmali.
3. Save `smali_craft.py` to the same directory.
4. Verify:
   ```bash
   python3 smali_craft.py --help
   ```

## Usage
SmaliCraft facilitates .smali file processing in a controlled lab setting for educational purposes. Below are examples and expected outcomes.

### Basic Commands
Disassemble a .dex file to .smali:
```bash
python3 smali_craft.py -a disassemble -i classes.dex -o output_dir
```

Disassemble .dex files from an APK:
```bash
python3 smali_craft.py -a disassemble -i app.apk -o output_dir
```

Assemble .smali files to .dex:
```bash
python3 smali_craft.py -a assemble -i classes.dex -o output_dir -s output_dir/classes_smali
```

Analyze .smali files:
```bash
python3 smali_craft.py -a analyze -i classes.dex -o output_dir -s output_dir/classes_smali
```

Run in quiet mode:
```bash
python3 smali_craft.py -a disassemble -i classes.dex -o output_dir -q
```

### Options
- `-a, --action`: Action to perform (disassemble, assemble, analyze; required).
- `-i, --input`: Path to input .dex or .apk file (required).
- `-o, --output`: Output directory (default: smali_craft-output).
- `-f, --force`: Force overwrite of output directory for disassemble.
- `-s, --smali-dir`: Smali directory path (required for assemble or analyze).
- `-q, --quiet`: Log to file only.

### Features

#### Disassembly
- **Purpose**: Convert .dex files to .smali for analysis or modification.
- **Usage**:
  ```bash
  python3 smali_craft.py -a disassemble -i classes.dex -o output_dir
  ```
- **Output**:
  ```
  2025-05-15 18:30:00 - INFO - Disassembled .dex files to output_dir/classes_smali
  ```
- **Result Directory** (`output_dir/classes_smali`):
  - Contains .smali files representing Dalvik bytecode.
- **JSON File** (`output_dir/logs/smali_craft_20250515_183000.json`):
  ```json
  {
    "input_path": "classes.dex",
    "output_dir": "output_dir",
    "actions": [
      {
        "input_path": "classes.dex",
        "action": "Disassemble",
        "status": "Disassembled .dex files to output_dir/classes_smali",
        "output_path": "output_dir/classes_smali",
        "timestamp": "2025-05-15 18:30:00"
      }
    ],
    "timestamp": "2025-05-15 18:30:00"
  }
  ```
- **Tips**: Use **APKForge** to extract .dex files from APKs, then disassemble with **SmaliCraft**.

#### Assembly
- **Purpose**: Rebuild .smali files into .dex for APK modification.
- **Usage**:
  ```bash
  python3 smali_craft.py -a assemble -i classes.dex -o output_dir -s output_dir/classes_smali
  ```
- **Output**:
  ```
  2025-05-15 18:30:00 - INFO - Assembled smali to output_dir/classes.dex
  ```
- **Result File** (`output_dir/classes.dex`):
  - Rebuilt .dex file for use in APKs.
- **Tips**: Edit .smali files in `output_dir/classes_smali` before assembly; integrate with **APKForge** for APK rebuilding.

#### Analysis
- **Purpose**: Provide statistics on .smali files.
- **Usage**:
  ```bash
  python3 smali_craft.py -a analyze -i classes.dex -o output_dir -s output_dir/classes_smali
  ```
- **Output**:
  ```
  2025-05-15 18:30:00 - INFO - Analyzed smali, output saved to output_dir/logs/classes_analysis.txt
  ```
- **Result File** (`output_dir/logs/classes_analysis.txt`):
  ```
  === Smali Analysis ===
  Total .smali files: 50
  Total lines of smali code: 5000
  Smali directory: output_dir/classes_smali
  ```
- **Tips**: Use analysis to assess code complexity before editing.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  python3 smali_craft.py -a disassemble -i classes.dex -o output_dir -q
  ```
- **Tips**: Monitor `smali_craft.log` with `tail -f smali_craft.log`.

### Workflow
1. Set up lab (Ubuntu 24.04 with Smali/Baksmali installed).
2. Install dependencies:
   ```bash
   ./setup_smali_craft.sh
   ```
3. Disassemble .dex or .apk to .smali:
   ```bash
   python3 smali_craft.py -a disassemble -i classes.dex -o output_dir
   ```
4. Edit .smali files in `output_dir/classes_smali` (optional).
5. Assemble .smali to .dex:
   ```bash
   python3 smali_craft.py -a assemble -i classes.dex -o output_dir -s output_dir/classes_smali
   ```
6. Analyze .smali files:
   ```bash
   python3 smali_craft.py -a analyze -i classes.dex -o output_dir -s output_dir/classes_smali
   ```
7. Monitor output in terminal or `smali_craft.log`.
8. Check results in `smali_craft-output/logs/` (text, JSON, SQLite).
9. Secure outputs (`rm -rf smali_craft-output/*`).

## Output
- **Logs**: `smali_craft.log`, e.g.:
  ```
  2025-05-15 18:30:00 - INFO - Disassembled .dex files to output_dir/classes_smali
  2025-05-15 18:30:01 - INFO - Assembled smali to output_dir/classes.dex
  ```
- **Results**: `smali_craft-output/logs/smali_craft_<timestamp>.json` and analysis files.
- **Database**: `smali_craft-output/logs/smali_craft.db` (SQLite).

## Notes
- **Environment**: Use on .dex or .apk files you own or have permission to analyze in your lab.
- **Impact**: Modified .dex files require integration into APKs (via **APKForge**) for testing.
- **Ethics**: Avoid unauthorized reverse engineering to prevent legal/IP issues.
- **Dependencies**: Requires `smali` and `baksmali` binaries.
- **Root**: Not required, but Smali/Baksmali tools must be in PATH.
- **Sources**: Built for .smali processing, leveraging concepts from Smali/Baksmali and Android security research.

## Disclaimer
**Personal Use Only**: SmaliCraft is for educational analysis of .dex or .apk files you own or have permission to study. Unauthorized reverse engineering or modification may violate laws or terms of service. Ensure compliance with local laws, including copyright and software licensing regulations.

**Safe Use**:
- Use in a private lab (e.g., Ubuntu 24.04).
- Secure outputs (`smali_craft.log`, `smali_craft-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Analyzing proprietary files without permission.
- Distributing modified .dex files or APKs.
- Using in production environments.

## Limitations
- **Scope**: Disassembles/assembles .smali; requires manual .smali editing.
- **Dependencies**: Relies on `smali` and `baksmali` for core functionality.
- **Interface**: CLI-only; lacks GUI or TUI.
- **Compatibility**: May not handle heavily obfuscated .dex files.

## Tips
- Use **APKForge** to extract .dex files from APKs and rebuild modified APKs.
- Combine with **Dex2Java** for parallel Java decompilation.
- Test modified .dex files in an Android emulator or device via **IdentityForge**.
- Review OWASP Mobile Security guidelines for analyzing app vulnerabilities.
- Verify `smali`/`baksmali` versions for compatibility with modern .dex files.

## License
For personal educational use; no formal license. Use responsibly.