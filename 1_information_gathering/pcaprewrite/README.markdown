# PcapRewrite

**PcapRewrite** is a private Python command-line tool for editing PCAP files, enabling users to modify network packet headers for network testing, debugging, and analysis. It processes PCAP files from tools like `tcpdump` or Wireshark, supporting changes to Ethernet MAC addresses, IPv4/IPv6 addresses, and TCP/UDP ports. Built with Scapy, it ensures checksums are recalculated for valid packets.

> ⚠️ **For private, authorized use only. Do not share or distribute.**

## Description

PcapRewrite allows precise editing of packet headers in PCAP files, targeting:

- **Layer 2** (Data Link): Ethernet MAC addresses.
- **Layer 3** (Network): IPv4/IPv6 addresses.
- **Layer 4** (Transport): TCP/UDP ports.

It reads an input PCAP file, applies user-specified modifications via a command-line interface, and generates a new PCAP file. A verbose mode displays modified packet details for debugging. The tool is designed for personal use in controlled environments, such as simulating traffic or anonymizing data.

Currently supports:
- Ethernet
- IPv4/IPv6
- TCP/UDP

> Future extensibility: VLAN tagging, TTL adjustments, additional protocols.

## Features

### ✅ Modify Ethernet MAC Addresses
- Updates source and destination MAC addresses.
- Uses 48-bit format (e.g., `00:01:02:03:04:05`).
- Simulates device-specific traffic or adapts packets for interfaces.

### ✅ Edit IPv4/IPv6 Addresses
- Changes source/destination IPs (e.g., `192.168.1.100`, `2001:db8::1`).
- Maintains packet validity with header updates.
- Ideal for anonymizing data or testing routing.

### ✅ Adjust TCP/UDP Ports
- Modifies source/destination ports (1–65535).
- Tests services on non-standard ports (e.g., web server on `8080`).

### ✅ Recalculate Checksums
- Auto-updates IPv4, TCP, and UDP checksums via Scapy.
- Ensures packets are valid for replay or analysis.

### ✅ Verbose Debugging
- Shows modified packet details (MAC, IP, ports).
- Helps verify changes or troubleshoot issues.

### ✅ Command-Line Interface
- Clear arguments for input/output files and modifications.
- Easily integrates into scripts or workflows.

### ✅ Protocol Support
- Handles Ethernet, IPv4, IPv6, TCP, and UDP packets.
- Skips unsupported protocols without errors.

---

## Requirements

### 🐍 Python 3.6+
- Required for running the script.
- Check version:
  ```bash
  python3 --version
  ```
- Install if needed:
  ```bash
  sudo apt install python3  # Ubuntu
  brew install python3      # macOS
  ```
- Download from [python.org](https://www.python.org/downloads/) for Windows.

### 📦 Scapy Library
- Needed for packet parsing and manipulation (version 2.4.5+).
- Install:
  ```bash
  pip install scapy
  ```
- Verify:
  ```bash
  python3 -c "import scapy; print(scapy.__version__)"
  ```
- Use `--user` for permission issues:
  ```bash
  pip install scapy --user
  ```

### 💻 Operating System
- Runs on Linux, macOS, or Windows with Python/Scapy.
- Linux preferred for network tools.

### 📄 Input PCAP Files
- Valid PCAPs from `tcpdump`, Wireshark, etc.
- Ensure read/write permissions for files/directories.

### 🔍 Optional Verification Tools
- `tcpdump` for command-line PCAP checks:
  ```bash
  sudo apt install tcpdump  # Linux
  brew install tcpdump      # macOS
  ```
- Wireshark for graphical analysis ([wireshark.org](https://www.wireshark.org/)).

---

## Installation

### 📥 Save the Script
- Store `pcap_rewrite.py` in a private directory:
  ```bash
  mkdir ~/pcaprewrite
  mv pcap_rewrite.py ~/pcaprewrite/
  cd ~/pcaprewrite
  ```
- Keep it confidential; avoid public storage.

### 📦 Install Scapy
- Install Scapy via pip:
  ```bash
  pip install scapy
  ```
- Confirm installation:
  ```bash
  python3 -c "import scapy; print(scapy.__version__)"
  ```

### 🔧 Make Executable (Optional)
- On Linux/macOS, enable direct execution:
  ```bash
  chmod +x pcap_rewrite.py
  ```
- Run as `./pcap_rewrite.py` (else use `python3 pcap_rewrite.py`).

### 📄 Prepare Test PCAP
- Create a sample PCAP:
  ```bash
  sudo tcpdump -i eth0 -w input.pcap -c 10
  ```
- Or use Wireshark to capture and save a PCAP.

### ✅ Verify Setup
- Confirm Python, Scapy, and permissions are correct.
- Test with a command from Examples.

---

## Examples

### 🛠️ Modify MAC and IP Addresses
  ```bash
  ./pcap_rewrite.py --infile input.pcap --outfile output.pcap \
                    --src-mac 00:01:02:03:04:05 --dst-mac 06:07:08:09:10:11 \
                    --src-ip 192.168.1.100 --dst-ip 192.168.1.200
  ```
- Updates MACs and IPs.
- Use for routing tests or device simulation.
- Notes: Use valid MAC (`XX:XX:XX:XX:XX:XX`) and IP formats.

### 🛠️ Change TCP/UDP Port with Verbose
  ```bash
  ./pcap_rewrite.py --infile input.pcap --outfile output.pcap \
                    --dst-port 8080 --verbose
  ```
- Sets TCP/UDP destination port to `8080`.
- Shows packet details.
- Use for service testing; redirect verbose output if needed (`> log.txt`).

### 🛠️ Edit IPv6 Addresses
  ```bash
  ./pcap_rewrite.py --infile input.pcap --outfile output.pcap \
                    --src-ip 2001:db8::1 --dst-ip 2001:db8::2
  ```
- Modifies IPv6 source/destination IPs.
- Use for IPv6 testing.
- Notes: Ensure valid IPv6 format.

### 🛠️ Copy PCAP Unchanged
  ```bash
  ./pcap_rewrite.py --infile input.pcap --outfile output.pcap
  ```
- Copies input PCAP without changes.
- Tests tool functionality.

---

## Expected Output

### 🖥️ Console Output
- **Success**:
  ```
  Modified PCAP written to output.pcap
  ```
  Confirms output file creation.
- **Verbose Mode**:
  - Displays packet details:
    ```
    Packet 1:
    ###[ Ethernet ]###
      dst       = 06:07:08:09:10:11
      src       = 00:01:02:03:04:05
      type      = 0x800
    ###[ IP ]###
      version   = 4
      src       = 192.168.1.100
      dst       = 192.168.1.200
    ###[ TCP ]###
      sport     = 12345
      dport     = 8080
    ```
  - Useful for debugging; may be long for large PCAPs.
- **Errors**:
  - File issues:
    ```
    Error reading PCAP file: [details]
    ```
  - Argument errors:
    ```
    error: argument --src-mac: invalid MAC address format
    ```

### 📄 File Output
- Creates `output.pcap` with modified headers.
- Unsupported packets copied unchanged.
- Compatible with `tcpdump`, Wireshark.

### 🔍 Verification
- Check with `tcpdump`:
  ```bash
  tcpdump -r output.pcap
  ```
  Example:
  ```
  12:34:56.789012 IP 192.168.1.100.12345 > 192.168.1.200.8080: TCP, length 64
  ```
- Use Wireshark to confirm MAC, IP, port changes.
- Compare input/output PCAPs.

### 📝 Notes
- Large PCAPs process slowly.
- Corrupted packets skipped or copied.

---

## Disclaimer

> ⚠️ **PcapRewrite is for private, authorized use only.** Do not share or use on networks/systems without permission. Unauthorized use may violate laws or policies (e.g., computer misuse, data protection). Users must ensure compliance and verify output to prevent network issues. Provided as-is, with no warranties.