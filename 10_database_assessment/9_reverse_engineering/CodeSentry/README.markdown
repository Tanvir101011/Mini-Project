# CodeSentry

## Description
CodeSentry is a Python-based tool designed for ethical bytecode analysis in your private lab (Ubuntu 24.04, home network). It enables decompiling and analyzing Android bytecode (.dex, .apk) and Java bytecode (.class, .jar) files, producing readable Java or smali code, viewing bytecode, and exporting analysis results. The tool features a CLI interface, SQLite logging, JSON output, and a modular design, integrating with your tools like **APKForge**, **Dex2Java**, **SmaliCraft**, **PatternSentry**, **NetSentry**, **NatPiercer**, **WiFiCrush**, **IdentityForge**, **IAXStorm**, **SlowStrike**, **SSLBlaze**, **RTPStorm**, and **NetBlitz**.

**Important**: Use CodeSentry only on files you own, have developed, or have explicit permission to analyze. Unauthorized reverse engineering or modification may violate intellectual property laws, terms of service, or ethical standards. This tool is restricted to your lab for responsible use. Ensure compliance with local laws, including copyright and software licensing regulations.

## Features
- **Java Decompilation**: Converts .dex, .apk, .class, or .jar to Java source code using jadx.
- **Smali Disassembly**: Disassembles .dex or .apk to smali code using baksmali.
- **Bytecode Viewing**: Displays Java bytecode for .class or .jar files using javap.
- **Analysis**: Extracts metadata (e.g., APK permissions, class info) using aapt or javap.
- **Output Formats**: SQLite database, JSON, and text logs.
- **Logging**: Saves logs to `code_sentry.log` and results to `code_sentry-output/logs/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Tools: `jadx`, `smali`, `baksmali`, `aapt`, `javap` (via OpenJDK).
   - Private lab environment.
2. **Install Dependencies**:
   - Save `setup_code_sentry.sh` to a directory (e.g., `/home/user/code_sentry/`).
   - Make executable and run:
     ```bash
     chmod +x setup_code_sentry.sh
     ./setup_code_sentry.sh
     ```
   - Installs Python, jadx, smali/baksmali, Android SDK tools, and OpenJDK.
3. Save `code_sentry.py` to the same directory.
4. Verify:
   ```bash
   python3 code_sentry.py --help
   ```

## Usage
CodeSentry facilitates bytecode analysis in a controlled lab setting for educational purposes. Below are examples and expected outcomes.

### Basic Commands
Decompile to Java source:
```bash
python3 code_sentry.py -a decompile-java -i classes.dex -o output_dir
```

Disassemble to smali code:
```bash
python3 code_sentry.py -a decompile-smali -i app.apk -o output_dir
```

View Java bytecode:
```bash
python3 code_sentry.py -a view-bytecode -i example.jar -o output_dir
```

Analyze file metadata:
```bash
python3 code_sentry.py -a analyze -i sample.class -o output_dir
```

Run in quiet mode:
```bash
python3 code_sentry.py -a decompile-java -i classes.dex -o output_dir -q
```

### Options
- `-a, --action`: Action to perform (decompile-java, decompile-smali, view-bytecode, analyze; required).
- `-i, --input`: Path to input .dex, .apk, .class, or .jar file (required).
- `-o, --output`: Output directory (default: code_sentry-output).
- `-f, --force`: Force overwrite of output directory for decompilation.
- `-q, --quiet`: Log to file only.

### Features

#### Java Decompilation
- **Purpose**: Convert bytecode to readable Java source code.
- **Usage**:
  ```bash
  python3 code_sentry.py -a decompile-java -i classes.dex -o output_dir
  ```
- **Output**:
  ```
  2025-05-15 17:29:00 - INFO - Decompiled to Java source in output_dir/classes_java
  ```
- **Result Directory** (`output_dir/classes_java`):
  - Contains Java source files (.java).
- **JSON File** (`output_dir/logs/code_sentry_20250515_172900.json`):
  ```json
  {
    "input_path": "classes.dex",
    "output_dir": "output_dir",
    "actions": [
      {
        "input_path": "classes.dex",
        "action": "Decompile Java",
        "status": "Decompiled to Java source in output_dir/classes_java",
        "output_path": "output_dir/classes_java",
        "timestamp": "2025-05-15 17:29:00"
      }
    ],
    "timestamp": "2025-05-15 17:29:00"
  }
  ```
- **Tips**: Use with **Dex2Java** for .dex-to-.jar conversion or **APKForge** for APK extraction.

#### Smali Disassembly
- **Purpose**: Disassemble .dex or .apk to smali code for low-level analysis.
- **Usage**:
  ```bash
  python3 code_sentry.py -a decompile-smali -i app.apk -o output_dir
  ```
- **Output**:
  ```
  2025-05-15 17:29:00 - INFO - Disassembled to smali in output_dir/app_smali
  ```
- **Result Directory** (`output_dir/app_smali`):
  - Contains smali files (.smali).
- **Tips**: Combine with **SmaliCraft** for smali editing and reassembly.

#### Bytecode Viewing
- **Purpose**: Display Java bytecode for .class or .jar files.
- **Usage**:
  ```bash
  python3 code_sentry.py -a view-bytecode -i example.jar -o output_dir
  ```
- **Output**:
  ```
  2025-05-15 17:29:00 - INFO - Bytecode saved to output_dir/logs/example_bytecode.txt
  ```
- **Result File** (`output_dir/logs/example_bytecode.txt`):
  ```
  === Bytecode for example.jar/com/example/Main.class ===
  public class com.example.Main {
    public com.example.Main();
      Code:
         0: aload_0
         1: invokespecial #1
         4: return
  }
  ```
- **Tips**: Use for low-level bytecode analysis without decompilation.

#### Analysis
- **Purpose**: Extract metadata from .dex, .apk, .class, or .jar files.
- **Usage**:
  ```bash
  python3 code_sentry.py -a analyze -i app.apk -o output_dir
  ```
- **Output**:
  ```
  2025-05-15 17:29:00 - INFO - Analysis saved to output_dir/logs/app_analysis.txt
  ```
- **Result File** (`output_dir/logs/app_analysis.txt`):
  ```
  === APK/DEX Info ===
  package: name='com.example.app' versionCode='1' versionName='1.0'
  permissions: android.permission.INTERNET
  ...
  ```
- **Tips**: Cross-reference with **PatternSentry** for pattern-based detection.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  python3 code_sentry.py -a decompile-java -i classes.dex -o output_dir -q
  ```
- **Tips**: Monitor `code_sentry.log` with `tail -f code_sentry.log`.

### Workflow
1. Set up lab (Ubuntu 24.04 with required tools installed).
2. Install dependencies:
   ```bash
   ./setup_code_sentry.sh
   ```
3. Decompile to Java or smali:
   ```bash
   python3 code_sentry.py -a decompile-java -i classes.dex -o output_dir
   ```
4. View bytecode:
   ```bash
   python3 code_sentry.py -a view-bytecode -i example.jar -o output_dir
   ```
5. Analyze file metadata:
   ```bash
   python3 code_sentry.py -a analyze -i app.apk -o output_dir
   ```
6. Monitor output in terminal or `code_sentry.log`.
7. Check results in `code_sentry-output/logs/` (text, JSON, SQLite).
8. Secure outputs (`rm -rf code_sentry-output/*`).

## Output
- **Logs**: `code_sentry.log`, e.g.:
  ```
  2025-05-15 17:29:00 - INFO - Decompiled to Java source in output_dir/classes_java
  2025-05-15 17:29:01 - INFO - Results saved to output_dir/logs/code_sentry_20250515_172900.json
  ```
- **Results**: `code_sentry-output/logs/code_sentry_<timestamp>.json` and analysis/bytecode files.
- **Database**: `code_sentry-output/logs/code_sentry.db` (SQLite).

## Notes
- **Environment**: Use on files you own or have permission to analyze in your lab.
- **Impact**: Decompiled code aids in analysis but requires further processing for modification (e.g., via **SmaliCraft**).
- **Ethics**: Avoid unauthorized reverse engineering to prevent legal/IP issues.
- **Dependencies**: Requires `jadx`, `smali`, `baksmali`, `aapt`, `javap`.
- **Root**: Not required, but tools must be in PATH.
- **Sources**: Built for bytecode analysis, leveraging concepts from Android and Java reverse engineering.

## Disclaimer
**Personal Use Only**: CodeSentry is for educational analysis of files you own or have permission to study. Unauthorized reverse engineering or modification may violate laws or terms of service. Ensure compliance with local laws, including copyright and software licensing regulations.

**Safe Use**:
- Use in a private lab (e.g., Ubuntu 24.04).
- Secure outputs (`code_sentry.log`, `code_sentry-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Analyzing proprietary files without permission.
- Distributing decompiled code or files.
- Using in production environments.

## Limitations
- **Scope**: CLI-based; lacks GUI (unlike Bytecode Viewer).
- **Dependencies**: Relies on external tools (`jadx`, `baksmali`, `javap`, `aapt`).
- **Compatibility**: May struggle with heavily obfuscated code.
- **Features**: Basic decompilation and viewing; no built-in code editing or debugging.

## Tips
- Use **APKForge** to extract .dex files from APKs before analysis.
- Combine with **Dex2Java** for .jar conversion or **SmaliCraft** for smali editing.
- Use **PatternSentry** to scan decompiled code for malicious patterns.
- Test decompiled code in an Android emulator or device via **IdentityForge**.
- Review OWASP Mobile Security guidelines for analyzing app vulnerabilities.

## License
For personal educational use; no formal license. Use responsibly.