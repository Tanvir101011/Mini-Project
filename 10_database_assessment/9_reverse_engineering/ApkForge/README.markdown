# APKForge

## Description
APKForge is a Python-based tool designed for ethical reverse engineering in your private lab (Ubuntu 24.04, home network). It enables decompiling, analyzing, and rebuilding Android APK files to study their structure, resources, and code (e.g., smali, manifest). The tool features a CLI interface, SQLite logging, JSON output, and a modular design, integrating with your tools like **NetSentry**, **NatPiercer**, **WiFiCrush**, **IdentityForge**, **IAXStorm**, **SlowStrike**, **SSLBlaze**, **RTPStorm**, and **NetBlitz**.

**Important**: Use APKForge only on APKs you own, have developed, or have explicit permission to analyze. Unauthorized reverse engineering or modification of APKs may violate intellectual property laws, terms of service, or ethical standards. This tool is restricted to your lab for responsible use. Ensure compliance with local laws, including copyright and software licensing regulations.

## Features
- **Decompilation**: Extracts APK resources, manifest, and code into readable formats.
- **Rebuilding**: Reconstructs modified APKs with alignment and signing.
- **Analysis**: Dumps APK metadata (e.g., permissions, activities) for inspection.
- **Output Formats**: SQLite database, JSON, and text logs.
- **Logging**: Saves logs to `apkforge.log` and results to `apkforge-output/logs/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - Android SDK tools (`aapt`, `zipalign`, `apksigner`).
   - Debug keystore (default: `/tmp/debug.keystore` with password `android`).
   - Private lab environment.
2. **Install Dependencies**:
   - Save `setup_apkforge.sh` to a directory (e.g., `/home/user/apkforge/`).
   - Make executable and run:
     ```bash
     chmod +x setup_apkforge.sh
     ./setup_apkforge.sh
     ```
   - Installs Python, Android SDK tools, and generates a debug keystore.
3. Save `apkforge.py` to the same directory.
4. Verify:
   ```bash
   python3 apkforge.py --help
   ```

## Usage
APKForge facilitates APK reverse engineering in a controlled lab setting for educational purposes. Below are examples and expected outcomes.

### Basic Commands
Decompile an APK:
```bash
python3 apkforge.py -a decompile -i app.apk -o output_dir
```

Rebuild a decompiled APK:
```bash
python3 apkforge.py -a rebuild -i app.apk -o output_dir -d output_dir/app_decompiled
```

Analyze an APK:
```bash
python3 apkforge.py -a analyze -i app.apk -o output_dir
```

Run in quiet mode:
```bash
python3 apkforge.py -a decompile -i app.apk -o output_dir -q
```

### Options
- `-a, --action`: Action to perform (decompile, rebuild, analyze; required).
- `-i, --input`: Path to input APK file (required).
- `-o, --output`: Output directory (default: apkforge-output).
- `-f, --force`: Force overwrite of output directory for decompile.
- `-d, --decompile-dir`: Decompiled directory path (required for rebuild).
- `-q, --quiet`: Log to file only.

### Features

#### Decompilation
- **Purpose**: Extract APK resources, manifest, and code for analysis.
- **Usage**:
  ```bash
  python3 apkforge.py -a decompile -i app.apk -o output_dir
  ```
- **Output**:
  ```
  2025-05-15 17:00:00 - INFO - Decompiled app to output_dir/app_decompiled
  ```
- **Result Directory** (`output_dir/app_decompiled`):
  - Contains extracted files (e.g., `AndroidManifest.xml`, resources, smali).
- **JSON File** (`output_dir/logs/forge_20250515_170000.json`):
  ```json
  {
    "apk_path": "app.apk",
    "output_dir": "output_dir",
    "actions": [
      {
        "apk_path": "app.apk",
        "action": "Decompile",
        "status": "Decompiled app to output_dir/app_decompiled",
        "output_path": "output_dir/app_decompiled",
        "timestamp": "2025-05-15 17:00:00"
      }
    ],
    "timestamp": "2025-05-15 17:00:00"
  }
  ```
- **Tips**: Modify `smali` files or resources in `output_dir/app_decompiled` before rebuilding.

#### Rebuilding
- **Purpose**: Reconstruct modified APKs with alignment and signing.
- **Usage**:
  ```bash
  python3 apkforge.py -a rebuild -i app.apk -o output_dir -d output_dir/app_decompiled
  ```
- **Output**:
  ```
  2025-05-15 17:00:00 - INFO - Rebuilt and signed app to output_dir/app_rebuilt.apk
  ```
- **Result File** (`output_dir/app_rebuilt.apk`):
  - Aligned and signed APK ready for installation (test on emulator or device).
- **Tips**: Use **IdentityForge** to test modified APKs in a controlled environment.

#### Analysis
- **Purpose**: Extract APK metadata (e.g., permissions, activities).
- **Usage**:
  ```bash
  python3 apkforge.py -a analyze -i app.apk -o output_dir
  ```
- **Output**:
  ```
  2025-05-15 17:00:00 - INFO - Analyzed app, output saved to output_dir/logs/app_analysis.txt
  ```
- **Result File** (`output_dir/logs/app_analysis.txt`):
  ```
  package: name='com.example.app' versionCode='1' versionName='1.0'
  sdkVersion:'21'
  permissions: android.permission.INTERNET
  ...
  ```
- **Tips**: Review permissions for security analysis; cross-reference with OWASP guidelines.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  python3 apkforge.py -a decompile -i app.apk -o output_dir -q
  ```
- **Tips**: Monitor `apkforge.log` with `tail -f apkforge.log`.

### Workflow
1. Set up lab (Ubuntu 24.04 with Android SDK tools installed).
2. Install dependencies:
   ```bash
   ./setup_apkforge.sh
   ```
3. Run APKForge:
   ```bash
   python3 apkforge.py -a decompile -i app.apk -o output_dir
   ```
4. Modify decompiled files (optional).
5. Rebuild APK:
   ```bash
   python3 apkforge.py -a rebuild -i app.apk -o output_dir -d output_dir/app_decompiled
   ```
6. Analyze APK:
   ```bash
   python3 apkforge.py -a analyze -i app.apk -o output_dir
   ```
7. Monitor output in terminal or `apkforge.log`.
8. Check results in `apkforge-output/logs/` (text, JSON, SQLite).
9. Secure outputs (`rm -rf apkforge-output/*`).

## Output
- **Logs**: `apkforge.log`, e.g.:
  ```
  2025-05-15 17:00:00 - INFO - Decompiled app to output_dir/app_decompiled
  2025-05-15 17:00:10 - INFO - Rebuilt and signed app to output_dir/app_rebuilt.apk
  ```
- **Results**: `apkforge-output/logs/forge_<timestamp>.json` and analysis files.
- **Database**: `apkforge-output/logs/apkforge.db` (SQLite).

## Notes
- **Environment**: Use on APKs you own or have permission to analyze in your lab.
- **Impact**: Modifying APKs may violate app terms; rebuilt APKs require testing in emulators/devices.
- **Ethics**: Avoid unauthorized reverse engineering to prevent legal/IP issues.
- **Dependencies**: Requires `aapt`, `zipalign`, `apksigner`, and Python.
- **Root**: Not required, but Android SDK tools must be in PATH.
- **Sources**: Built for APK reverse engineering, leveraging concepts from Apktool and Android security research.

## Disclaimer
**Personal Use Only**: APKForge is for educational analysis of APKs you own or have permission to study. Unauthorized reverse engineering or modification may violate laws or terms of service. Ensure compliance with local laws, including copyright and software licensing regulations.

**Safe Use**:
- Use in a private lab (e.g., Ubuntu 24.04 with emulator).
- Secure outputs (`apkforge.log`, `apkforge-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Analyzing proprietary APKs without permission.
- Distributing modified APKs.
- Using in production environments.

## Limitations
- **Scope**: Basic decompilation/rebuilding; lacks advanced smali editing or dex-to-java decompilation.
- **Dependencies**: Relies on external tools (`aapt`, `zipalign`, `apksigner`).
- **Interface**: CLI-only; lacks GUI or TUI.
- **Compatibility**: May not handle obfuscated or complex APKs.

## Tips
- Test rebuilt APKs on an Android emulator or device in your lab.
- Use tools like **jadx** for dex-to-java decompilation alongside **APKForge**.
- Combine with **IdentityForge** for testing modified APKs in controlled scenarios.
- Review OWASP Mobile Security guidelines for analyzing APK vulnerabilities.
- Secure debug keystore (`/tmp/debug.keystore`) or use a custom one.

## License
For personal educational use; no formal license. Use responsibly.