# SignalSnare

## Description
SignalSnare is a Python-based digital radio signal decoder inspired by **multimon-ng**, designed for decoding transmission modes like POCSAG (512, 1200, 2400 baud) and DTMF on VHF/UHF bands. It supports input from RTL-SDR via `rtl_fm` or audio files (e.g., WAV), built for ethical security testing in your private lab (Ubuntu 24.04, home network). Using `numpy`, `scipy`, and `sounddevice`, it features a CLI interface, SQLite logging, JSON output, and multi-threading, integrating with your tools like **WiFiCrush**, **CredSnare**, and **NetPhantom**.

**Important**: Use SignalSnare only on frequencies/systems you have explicit permission to monitor. Decoding commercial or private communications may be illegal in some jurisdictions. This tool is restricted to your lab for responsible use, such as testing amateur radio or authorized signals.

## Features
- **Decoding Modes**: POCSAG (512, 1200, 2400 baud) and DTMF.
- **Input Sources**: RTL-SDR via `rtl_fm` or audio files (WAV, etc., via `sox`).
- **Output Formats**: SQLite database, JSON, and text logs.
- **Multi-Threading**: Concurrent demodulation for efficiency.
- **Quiet Mode**: Minimizes terminal output.
- **Logging**: Saves logs to `signalsnare.log` and results to `signalsnare-output/`.
- **Ethical Design**: Built for lab use with legal compliance warnings.

## Installation
1. **Requirements**:
   - Linux (e.g., Ubuntu 24.04, verify with `uname -a`).
   - Python 3.12+ (verify with `python3 --version`).
   - RTL-SDR dongle (optional for real-time input).
   - Root privileges (`sudo`) for SDR operations.
   - Private network/lab you control.
2. **Install Dependencies**:
   - Save `setup_signalsnare.sh` to a directory (e.g., `/home/user/signalsnare/`).
   - Make executable and run:
     ```bash
     chmod +x setup_signalsnare.sh
     ./setup_signalsnare.sh
     ```
   - Installs `numpy`, `scipy`, `sounddevice`, `rtl-sdr`, `sox`, and `libpulse-dev`.
3. Save `signalsnare.py` to the same directory.
4. Verify:
   ```bash
   python3 signalsnare.py --help
   ```

## Usage
SignalSnare decodes digital radio signals in a controlled lab setting, supporting POCSAG and DTMF. Below are examples and expected outcomes.

### Basic Commands
Decode POCSAG from an SDR at 148.5565 MHz:
```bash
sudo python3 signalsnare.py -f 148.5565 -d POCSAG1200 -d DTMF
```

Decode DTMF from a WAV file:
```bash
python3 signalsnare.py -i message.wav -d DTMF
```

Run in quiet mode with multiple demodulators:
```bash
sudo python3 signalsnare.py -f 148.5565 -d POCSAG512 -d POCSAG1200 -d POCSAG2400 -q
```

### Options
- `-i, --input-file`: Input audio file (e.g., WAV).
- `-f, --frequency`: Frequency in MHz for SDR input (e.g., 148.5565).
- `-s, --sample-rate`: Sample rate (default: 22050).
- `-d, --demodulator`: Demodulator (POCSAG512, POCSAG1200, POCSAG2400, DTMF; can specify multiple).
- `-T, --threads`: Number of threads (default: 5).
- `-q, --quiet`: Log to file only.

### Features

#### POCSAG Decoding
- **Purpose**: Decode pager messages (512, 1200, 2400 baud).
- **Usage**:
  ```bash
  sudo python3 signalsnare.py -f 148.5565 -d POCSAG1200
  ```
- **Output**:
  ```
  2025-05-15 14:00:00 - INFO - Starting SignalSnare
  2025-05-15 14:00:02 - INFO - POCSAG1200: Address: 123456
  ```
- **Result File** (`signalsnare-output/snare_20250515_140000.txt`):
  ```
  === SignalSnare Results ===
  Timestamp: 2025-05-15 14:00:02
  [2025-05-15 14:00:02] POCSAG1200: Address: 123456
  ```
- **JSON File** (`signalsnare-output/snare_20250515_140000.json`):
  ```json
  {
    "frequency": 148.5565,
    "sample_rate": 22050,
    "demodulators": ["POCSAG1200"],
    "messages": [
      {
        "protocol": "POCSAG1200",
        "message": "Address: 123456",
        "timestamp": "2025-05-15 14:00:02"
      }
    ],
    "timestamp": "2025-05-15 14:00:02"
  }
  ```
- **Tips**: Use **NetPhantom** to scan for active POCSAG frequencies.

#### DTMF Decoding
- **Purpose**: Decode telephone dial tones.
- **Usage**:
  ```bash
  python3 signalsnare.py -i dtmf.wav -d DTMF
  ```
- **Output**:
  ```
  2025-05-15 14:00:03 - INFO - DTMF: 1234
  ```
- **Tips**: Generate test tones with Audacity for lab testing.

#### Quiet Mode
- **Purpose**: Reduce terminal output.
- **Usage**:
  ```bash
  sudo python3 signalsnare.py -f 148.5565 -d POCSAG1200 -q
  ```
- **Tips**: Monitor `signalsnare.log` with `tail -f signalsnare.log`.

### Workflow
1. Set up lab (VM with RTL-SDR or audio files).
2. Install dependencies:
   ```bash
   ./setup_signalsnare.sh
   ```
3. Run SignalSnare:
   ```bash
   sudo python3 signalsnare.py -f 148.5565 -d POCSAG1200 -d DTMF
   ```
4. Monitor output in terminal or `signalsnare.log`.
5. Check results in `signalsnare-output/` (text, JSON, SQLite).
6. Stop with `Ctrl+C`; secure outputs (`rm -rf signalsnare-output/*`).

## Output
- **Logs**: `signalsnare.log`, e.g.:
  ```
  2025-05-15 14:00:00 - INFO - Starting SignalSnare
  2025-05-15 14:00:02 - INFO - POCSAG1200: Address: 123456
  ```
- **Results**: `signalsnare-output/snare_<timestamp>.txt` and `.json`.
- **Database**: `signalsnare-output/signalsnare.db` (SQLite).

## Notes
- **Environment**: Use on authorized frequencies in your lab.
- **Impact**: Decoding may require careful frequency tuning; test with caution.
- **Ethics**: Avoid unauthorized monitoring to prevent legal/security issues.
- **Dependencies**: Requires `numpy`, `scipy`, `sounddevice`, `rtl-sdr`, `sox`, `libpulse-dev`.
- **Root**: Requires `sudo` for SDR operations.
- **Sources**: Inspired by multimon-ng documentation and usage examples (Ubuntu manpages, Kali Linux tools, GitHub discussions).

## Disclaimer
**Personal Use Only**: SignalSnare is for learning on frequencies/systems you have permission to monitor. Unauthorized decoding of commercial/private communications is illegal and may lead to legal consequences or ethical issues. Ensure compliance with local laws.

**Safe Use**:
- Use in a private lab (e.g., VM with RTL-SDR).
- Secure outputs (`signalsnare.log`, `signalsnare-output/*`); delete after use.
- No warranty; use at your own risk.

**Avoid**:
- Monitoring commercial/private services without permission.
- Sharing sensitive output files.
- Production environments to prevent disruptions.

## Limitations
- **Modes**: Supports POCSAG and DTMF; lacks FLEX, AFSK, or MORSE_CW (unlike multimon-ng).
- **Simplified Decoding**: POCSAG decoder is basic (address detection only); lacks full message parsing.
- **Hardware**: Requires RTL-SDR for real-time input or compatible audio files.
- **CLI-Only**: No GUI, unlike some SDR tools (e.g., SDR# plugins).

## Tips
- Use GQRX/CubicSDR to find active frequencies before decoding.
- Test with sample WAV files generated via Audacity.
- Combine with **WiFiCrush** for Wi-Fi security testing or **CredSnare** for phishing simulations.
- Monitor traffic with Wireshark for deeper analysis.
- Extend with additional demodulators (e.g., FLEX) using `scipy` signal processing.

## License
For personal educational use; no formal license. Use responsibly.