# Dex2Java

## Description
Dex2Java is a Python-based tool designed for ethical reverse engineering in your private lab (Ubuntu 24.04, home network). It converts Android Dalvik Executable (.dex) files, or .dex files extracted from APKs, into Java Archive (.jar) files for further analysis or decompilation into Java source code. The tool features a CLI interface, SQLite logging, JSON output, and a modular design, integrating with your tools like **APKForge**, **NetSentry**, **NatPiercer**, **WiFiCrush**, **IdentityForge**, **IAXStorm**, **SlowStrike**, **SSLBlaze**, **RTPStorm**, and **NetBlitz**.

**Important**: Use Dex2Java only on .dex or .apk files you own, have developed, or have explicit permission to analyze. Unauthorized reverse engineering or modification may violate intellectual property laws, terms of service, or ethical standards. This tool is restricted to your lab for responsible use. Ensure compliance with local laws, including copyright and software licensing regulations.

## Features
- **DEX Conversion**: Converts .dex files (or .dex from APKs) to .jar files.
- **APK Support**: Extracts .dex files from APKs for conversion.
- **Analysis**: Lists contents of generated .jar files (e.g., class files).
- **Output Formats**: SQLite database, JSON, and text logs.
- **Logging**: Saves logs to `dex2java.log` and results to `dex2java-output/logs/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - dex2jar tools (`d2j-dex2jar` binary).
   - Java Development Kit (JDK) for `jar` command.
   - Private lab environment.
2. **Install Dependencies**:
   - Save `setup_dex2java.sh` to a directory (e.g., `/home/user/dex2java/`).
   - Make executable and run:
     ```bash
     chmod +x setup_dex2java.sh
     ./setup_dex2java.sh
     ```
   - Installs Python, dex2jar, and JDK.
3. Save `dex2java.py` to the same directory.
4. Verify:
   ```bash
   python3 dex2java.py --help
   ```

## Usage
Dex2Java facilitates .dex to .jar conversion in a controlled lab setting for educational purposes. Below are examples and expected outcomes.

### Basic Commands
Convert a .dex file to .jar:
```bash
python3 dex2java.py -a convert -i classes.dex -o output_dir
```

Convert .dex files from an APK:
```bash
python3 dex2java.py -a convert -i app.apk -o output_dir
```

Analyze a .jar file:
```bash
python3 dex2java.py -a analyze -i classes.dex -o output_dir -j output_dir/classes.jar
```

Run in quiet mode:
```bash
python3 dex2java.py -a convert -i classes.dex -o output_dir -q
```

### Options
- `-a, --action`: Action to perform (convert, analyze; required).
- `-i, --input`: Path to input .dex or .apk file (required).
- `-o, --output`: Output directory (default: dex2java-output).
- `-j, --jar-file`: Path to .jar file (required for analyze).
- `-q, --quiet`: Log to file only.

### Features

#### DEX Conversion
- **Purpose**: Convert .dex files to .jar for Java decompilation.
- **Usage**:
  ```bash
  python3 dex2java.py -a convert -i classes.dex -o output_dir
  ```
- **Output**:
  ```
  2025-05-15 18:00:00 - INFO - Converted 1 .dex files to .jar in output_dir
  ```
- **Result File** (`output_dir/classes.jar`):
  - JAR file containing Java class files.
- **JSON File** (`output_dir/logs/dex2java_20250515_180000.json`):
  ```json
  {
    "input_path": "classes.dex",
    "output_dir": "output_dir",
    "actions": [
      {
        "input_path": "classes.dex",
        "action": "Convert",
        "status": "Converted 1 .dex files to .jar in output_dir",
        "output_path": "output_dir",
        "timestamp": "2025-05-15 18:00:00"
      }
    ],
    "timestamp": "2025-05-15 18:00:00"
  }
  ```
- **Tips**: Use **APKForge** to extract .dex files from APKs first, then convert with **Dex2Java**.

#### APK DEX Extraction
- **Purpose**: Extract and convert .dex files from APKs.
- **Usage**:
  ```bash
  python3 dex2java.py -a convert -i app.apk -o output_dir
  ```
- **Output**:
  ```
  2025-05-15 18:00:00 - INFO - Extracted 2 .dex files to output_dir/app_extracted
  2025-05-15 18:00:01 - INFO - Converted 2 .dex files to .jar in output_dir
  ```
- **Result Files** (`output_dir/classes.jar`, `output_dir/classes2.jar`):
  - JAR files for each .dex file.
- **Tips**: Combine with **IdentityForge** for testing converted code in a mobile environment.

#### JAR Analysis
- **Purpose**: List contents of generated .jar files.
- **Usage**:
  ```bash
  python3 dex2java.py -a analyze -i classes.dex -o output_dir -j output_dir/classes.jar
  ```
- **Output**:
  ```
  2025-05-15 18:00:00 - INFO - Analyzed classes.jar, output saved to output_dir/logs/classes_analysis.txt
  ```
- **Result File** (`output_dir/logs/classes_analysis.txt`):
  ```
  === JAR Contents ===
  META-INF/MANIFEST.MF
  com/example/MainActivity.class
  ...
  ```
- **Tips**: Use **jadx** or **JD-GUI** to decompile .jar files into Java source code.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  python3 dex2java.py -a convert -i classes.dex -o output_dir -q
  ```
- **Tips**: Monitor `dex2java.log` with `tail -f dex2java.log`.

### Workflow
1. Set up lab (Ubuntu 24.04 with dex2jar and JDK installed).
2. Install dependencies:
   ```bash
   ./setup_dex2java.sh
   ```
3. Convert .dex or .apk to .jar:
   ```bash
   python3 dex2java.py -a convert -i classes.dex -o output_dir
   ```
4. Analyze .jar file:
   ```bash
   python3 dex2java.py -a analyze -i classes.dex -o output_dir -j output_dir/classes.jar
   ```
5. Monitor output in terminal or `dex2java.log`.
6. Check results in `dex2java-output/logs/` (text, JSON, SQLite).
7. Secure outputs (`rm -rf dex2java-output/*`).

## Output
- **Logs**: `dex2java.log`, e.g.:
  ```
  2025-05-15 18:00:00 - INFO - Converted 1 .dex files to .jar in output_dir
  2025-05-15 18:00:01 - INFO - Analyzed classes.jar, output saved to output_dir/logs/classes_analysis.txt
  ```
- **Results**: `dex2java-output/logs/dex2java_<timestamp>.json` and analysis files.
- **Database**: `dex2java-output/logs/dex2java.db` (SQLite).

## Notes
- **Environment**: Use on .dex or .apk files you own or have permission to analyze in your lab.
- **Impact**: Converted .jar files require further decompilation (e.g., with **jadx**) for readable Java code.
- **Ethics**: Avoid unauthorized reverse engineering to prevent legal/IP issues.
- **Dependencies**: Requires `d2j-dex2jar` and JDK.
- **Root**: Not required, but dex2jar tools must be in PATH.
- **Sources**: Built for DEX conversion, leveraging concepts from dex2jar and Android security research.

## Disclaimer
**Personal Use Only**: Dex2Java is for educational analysis of .dex or .apk files you own or have permission to study. Unauthorized reverse engineering or modification may violate laws or terms of service. Ensure compliance with local laws, including copyright and software licensing regulations.

**Safe Use**:
- Use in a private lab (e.g., Ubuntu 24.04).
- Secure outputs (`dex2java.log`, `dex2java-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Analyzing proprietary files without permission.
- Distributing converted .jar files.
- Using in production environments.

## Limitations
- **Scope**: Converts .dex to .jar; requires external tools for Java decompilation.
- **Dependencies**: Relies on `d2j-dex2jar` for core conversion.
- **Interface**: CLI-only; lacks GUI or TUI.
- **Compatibility**: May not handle heavily obfuscated .dex files.

## Tips
- Use **APKForge** to extract .dex files from APKs before conversion.
- Decompile .jar files with **jadx** or **JD-GUI** for Java source code.
- Combine with **IdentityForge** for testing converted code in mobile scenarios.
- Review OWASP Mobile Security guidelines for analyzing app vulnerabilities.
- Verify `d2j-dex2jar` version for compatibility with modern .dex files.

## License
For personal educational use; no formal license. Use responsibly.