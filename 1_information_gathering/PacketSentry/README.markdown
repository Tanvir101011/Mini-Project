# PacketSentry

## Description
PacketSentry is a Python tool you can use to capture and analyze network packets in your own private network. It helps you learn about network traffic, protocols, and packet analysis by capturing live packets or reading from PCAP files, similar to TShark’s command-line packet analysis. Inspired by TShark, PacketSentry is designed for your personal experimentation in a controlled environment, like a home lab with network interfaces you own or have permission to monitor.

**Important**: This tool is for your personal use only with networks and devices you own or have explicit permission to monitor. Capturing packets on networks without clear authorization is illegal and could cause serious issues.

## Features
- Captures live packets from a specified network interface.
- Reads and analyzes packets from PCAP files.
- Filters packets by protocol (e.g., TCP, UDP, HTTP, DNS), IP, or port.
- Displays packet summaries (source, destination, protocol, payload details).
- Saves captured packets to a PCAP file.
- Logs analysis results to a text file.
- Quiet mode to reduce terminal output.
- Simple design for educational use in personal projects.

## Installation
1. **What You Need**:
   - Python 3.12 or later (check with `python3 --version`).
   - Scapy library: Install with `pip install scapy`.
   - A computer on a private network you control (e.g., your home lab).
   - Root/admin privileges for live capture (e.g., `sudo` on Linux).
   - No additional dependencies beyond Scapy.
2. Save the `packetsentry.py` script to a folder (e.g., `/home/user/packetsentry/`).
3. Install Scapy:
   ```bash
   pip install scapy
   ```
4. Run the script:
   ```bash
   python3 packetsentry.py --help
   ```

## How to Use
PacketSentry captures and analyzes network packets, either live from an interface or from a PCAP file, with options to filter by protocol, IP, or port. It displays packet summaries and saves results for review. Below is a guide on how to use each feature with examples and expected results.

### Basic Usage
Capture live packets on an interface:
```bash
sudo python3 packetsentry.py -i eth0
```

Analyze a PCAP file:
```bash
python3 packetsentry.py -r capture.pcap
```

### Options
- `-i, --interface`: Network interface for live capture (e.g., `eth0`).
- `-r, --pcap-file`: PCAP file to read packets from.
- `-f, --filter-protocol`: Filter by protocol (e.g., `tcp`, `udp`, `http`, `dns`).
- `--filter-ip`: Filter by source or destination IP (e.g., `192.168.1.1`).
- `--filter-port`: Filter by source or destination port (e.g., `80`).
- `-o, --output-pcap`: Output PCAP file to save captured packets.
- `-c, --count`: Number of packets to capture (0 for unlimited, default: 0).
- `-q, --quiet`: Run quietly (logs to file only).

### Using Each Feature

#### 1. Live Packet Capture
**What It Does**: Captures packets from a network interface in real-time.
**How to Use**:
1. Find your interface (e.g., on Linux: `ifconfig` or `ip link`).
2. Run with sudo (required for capture):
   ```bash
   sudo python3 packetsentry.py -i eth0 -c 10
   ```
**What Happens**:
- Captures 10 packets and logs them:
  ```
  2025-05-15 10:30:00 - Starting capture on eth0 (filter: none)
  2025-05-15 10:30:01 - TCP 192.168.1.100 -> 8.8.8.8 TCP 12345 -> 80
  2025-05-15 10:30:01 - DNS 192.168.1.100 -> 8.8.8.8 DNS example.com
  2025-05-15 10:30:02 - Results saved to packetsentry_results_20250515_103002.txt
  ```
- Results file example:
  ```
  [2025-05-15 10:30:01] TCP
  Source: 192.168.1.100 -> Destination: 8.8.8.8
  Summary: TCP 12345 -> 80
  --------------------------------------------------
  ```
**Tips**:
- Use `sudo` for live capture.
- Check interfaces with `ifconfig` or `ip link`.
- Use `-c` to limit capture size.

#### 2. Analyzing PCAP Files
**What It Does**: Reads and analyzes packets from a PCAP file.
**How to Use**:
1. Use a PCAP file (e.g., created with `tcpdump` or Wireshark).
2. Run:
   ```bash
   python3 packetsentry.py -r capture.pcap
   ```
**What Happens**:
- Analyzes all packets in the file:
  ```
  2025-05-15 10:35:00 - Reading packets from capture.pcap
  2025-05-15 10:35:01 - TCP 192.168.1.100 -> 8.8.8.8 TCP 12345 -> 80
  2025-05-15 10:35:01 - Results saved to packetsentry_results_20250515_103501.txt
  ```
**Tips**:
- Create a test PCAP with `tcpdump -i eth0 -w test.pcap`.
- Ensure the PCAP file path is correct.

#### 3. Filtering Packets
**What It Does**: Filters packets by protocol, IP, or port.
**How to Use**:
1. Filter by protocol (e.g., HTTP):
   ```bash
   sudo python3 packetsentry.py -i eth0 -f http
   ```
2. Filter by IP:
   ```bash
   sudo python3 packetsentry.py -i eth0 --filter-ip 192.168.1.100
   ```
3. Filter by port:
   ```bash
   sudo python3 packetsentry.py -i eth0 --filter-port 80
   ```
**What Happens**:
- Only matching packets are shown:
  ```
  2025-05-15 10:40:00 - Starting capture on eth0 (filter: tcp port 80 or tcp port 443)
  2025-05-15 10:40:01 - HTTP 192.168.1.100 -> 93.184.216.34 TCP 12345 -> 80 GET
  2025-05-15 10:40:02 - Results saved to packetsentry_results_20250515_104002.txt
  ```
**Tips**:
- Supported protocols: `tcp`, `udp`, `http`, `dns`.
- Combine filters for precision (e.g., `-f tcp --filter-ip 192.168.1.1 --filter-port 80`).

#### 4. Saving Captured Packets
**What It Does**: Saves captured packets to a PCAP file.
**How to Use**:
1. Specify an output PCAP:
   ```bash
   sudo python3 packetsentry.py -i eth0 -o output.pcap -c 10
   ```
**What Happens**:
- Captures packets and saves them:
  ```
  2025-05-15 10:45:00 - Starting capture on eth0 (filter: none)
  2025-05-15 10:45:01 - TCP 192.168.1.100 -> 8.8.8.8 TCP 12345 -> 80
  2025-05-15 10:45:02 - Packets saved to output.pcap
  2025-05-15 10:45:02 - Results saved to packetsentry_results_20250515_104502.txt
  ```
**Tips**:
- Open the output PCAP in Wireshark for detailed analysis.
- Ensure write permissions for the output file.

#### 5. Quiet Mode
**What It Does**: Reduces terminal output, logging only to the file.
**How to Use**:
1. Enable quiet mode:
   ```bash
   sudo python3 packetsentry.py -i eth0 -q
   ```
**What Happens**:
- No terminal output; logs go to `packetsentry.log`:
  ```
  $ sudo python3 packetsentry.py -i eth0 -q
  [No output]
  ```
- Log file example:
  ```
  2025-05-15 10:50:00 - Starting capture on eth0 (filter: none)
  2025-05-15 10:50:01 - TCP 192.168.1.100 -> 8.8.8.8 TCP 12345 -> 80
  ```
**Tips**:
- Check logs with `cat packetsentry.log` or `tail -f packetsentry.log`.
- Useful for background captures.

#### 6. Stopping the Tool
**What It Does**: Stops capturing when the packet count is reached or you press Ctrl+C.
**How to Use**:
1. Start capturing:
   ```bash
   sudo python3 packetsentry.py -i eth0
   ```
2. Press `Ctrl+C` to stop early.
**What Happens**:
- Capture stops, and results are saved:
  ```
  2025-05-15 10:55:00 - Starting capture on eth0 (filter: none)
  ^C
  2025-05-15 10:55:01 - PacketSentry stopped by user
  2025-05-15 10:55:01 - Results saved to packetsentry_results_20250515_105501.txt
  ```
**Tips**:
- Always stop the tool to free resources.
- Results are saved even if stopped early.

### Example Workflow
To experiment with network traffic in your home lab:
1. Set up a test network (e.g., a VM with a web server on `192.168.1.100`).
2. Capture HTTP traffic:
   ```bash
   sudo python3 packetsentry.py -i eth0 -f http -o http_capture.pcap -q
   ```
3. Generate traffic (e.g., `curl http://192.168.1.100`).
4. Review `packetsentry.log` and `packetsentry_results_*.txt`.
5. Open `http_capture.pcap` in Wireshark for detailed inspection.
6. Stop with `Ctrl+C` and delete output files securely.

## Output
- Logs are saved to `packetsentry.log`.
- Analysis results are saved to `packetsentry_results_<timestamp>.txt`.
- Captured packets are saved to the specified PCAP file (if `-o` is used).
- Example results file:
  ```
  [2025-05-15 10:30:01] TCP
  Source: 192.168.1.100 -> Destination: 8.8.8.8
  Summary: TCP 12345 -> 80
  --------------------------------------------------
  ```

## Important Notes
- **Environment**: Use PacketSentry only on networks and devices you own or have explicit permission to monitor (e.g., a local VM or home router).
- **Root Privileges**: Live capture requires root privileges (e.g., `sudo` on Linux) due to raw packet access.
- **Network Safety**: Avoid capturing on public or unauthorized networks to prevent legal issues.

## Disclaimer
**Personal Use Only**: PacketSentry is for your personal learning with networks and devices you own or have explicit permission to monitor. Capturing packets on networks without clear authorization is illegal and could lead to legal consequences, technical issues, or unintended harm. Always ensure you have permission from the network owner before capturing.

**Safe Use**:
- **Controlled Setup**: Use in a private lab (e.g., home network with your devices) to avoid affecting others. For example, capture on `eth0` in a local VM.
- **Data Security**: Output files (`packetsentry.log`, `packetsentry_results_*.txt`, PCAPs) may contain sensitive data (e.g., IPs, payloads). Store them securely and delete them after use (e.g., `rm packetsentry_*.txt`).
- **Legal Compliance**: Follow all applicable laws and regulations in your area, including privacy and data protection laws.
- **No Warranty**: This tool is provided “as is” for educational purposes. You are responsible for its use and any consequences.

**What to Avoid**:
- Do not capture on public networks (e.g., coffee shop Wi-Fi) without permission.
- Do not share output files, as they may contain private data.
- Do not use on corporate networks without explicit authorization.

## Limitations
- Requires root privileges for live capture.
- Supports basic protocols (TCP, UDP, HTTP, DNS); advanced protocols require custom extensions.
- Less detailed than TShark/Wireshark for deep protocol dissection.
- May fail on high-traffic networks due to Scapy’s performance limits.

## Testing Tips
- Generate test traffic: Use `curl`, `ping`, or a web browser in your lab.
- Create PCAPs: Use `tcpdump -i eth0 -w test.pcap` for testing.
- Verify interfaces: Check with `ifconfig` or `ip link`.
- Monitor traffic: Use `tcpdump` (e.g., `sudo tcpdump -i eth0`) to verify captures.
- Secure outputs: Delete files after use (`rm packetsentry_*.txt`).
- Check logs in real-time: `tail -f packetsentry.log`.

## Troubleshooting
- **Permission denied**: Run with `sudo` for live capture.
- **No packets captured**: Ensure the interface is active (`ifconfig`) and traffic is present.
- **PCAP file not found**: Verify the file path and create a test PCAP with `tcpdump`.
- **Scapy errors**: Install Scapy (`pip install scapy`) and ensure Python 3.12+.

## License
This tool is for your personal use. No formal license is provided, but please use it responsibly.