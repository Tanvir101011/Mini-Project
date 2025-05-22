# PacketCraft

## Description
PacketCraft is a Python tool you can use to explore network packets in your own private network. It lets you capture raw packets and see their data in hexadecimal format or inject custom packets you define as hex strings or text. This tool is designed for your personal experimentation in a controlled environment, like a home lab with devices you own, to learn about how networks handle packets.

**Important**: This tool is for your personal use only in networks and devices you own or have explicit permission to analyze. Using it on networks or devices without clear authorization is illegal and could cause serious issues.

## Features
- Captures raw network packets and logs them in hexadecimal format.
- Injects custom packets defined as hex strings (e.g., `0x414243`) or ASCII text.
- Filters packets by source/destination IP or port.
- Saves captured packets to a text file with timestamps and IP details.
- Quiet mode to reduce terminal output.
- Limits packet capture to a set number for controlled experiments.
- Simple design for easy use in personal projects.

## Installation
1. **What You Need**:
   - Python 3.12 or later (check with `python3 --version`).
   - Scapy library for packet handling.
   - A computer on a private network you control (e.g., your home Wi-Fi).
   - Administrator access (e.g., `sudo`) to capture and send packets.
2. Install Scapy:
   ```bash
   pip3 install scapy
   ```
3. Save the `packetcraft.py` script to a folder (e.g., `/home/user/packetcraft/`).
4. Run the script with administrator privileges:
   ```bash
   sudo python3 packetcraft.py --help
   ```

## How to Use
PacketCraft can either sniff packets or inject them. For sniffing, you specify options like the network interface, filters, and how many packets to capture. For injecting, you provide a payload (hex or text) and the number of packets to send. Below is a guide on how to use each feature with examples and expected results.

### Basic Usage
Capture up to 100 packets on any interface:
```bash
sudo python3 packetcraft.py -m 100
```

Inject a simple text payload once:
```bash
sudo python3 packetcraft.py -j "Hello" -c 1
```

### Options
- `-i, --interface`: Network interface (e.g., `eth0`, `wlan0`).
- `-f, --filter-ip`: Filter by source or destination IP (e.g., `192.168.1.100`).
- `-p, --filter-port`: Filter by source or destination port (e.g., `80`).
- `-m, --max-packets`: Maximum packets to capture (default: `100`).
- `-j, --inject-payload`: Payload to inject (hex with `0x` prefix or ASCII text).
- `-c, --inject-count`: Number of packets to inject (default: `1`).
- `-q, --quiet`: Run quietly (logs to file only).

### Using Each Feature

#### 1. Capturing Packets
**What It Does**: Sniffs raw packets and logs their hexadecimal data.
**How to Use**:
1. Run a basic capture:
   ```bash
   sudo python3 packetcraft.py -m 100
   ```
2. Generate traffic in your network (e.g., browse a website or ping a device).
**What Happens**:
- Packets are logged to `packetcraft.log` and a results file:
  ```
  2025-05-15 10:30:00 - Starting PacketCraft: Interface=any, FilterIP=all, FilterPort=all, MaxPackets=100
  2025-05-15 10:30:05 - Captured packet: 192.168.1.100 -> 8.8.8.8, 84 bytes
  2025-05-15 10:30:10 - Results saved to packetcraft_results_20250515_103010.txt
  ```
- Results file example:
  ```
  [2025-05-15 10:30:05] 192.168.1.100 -> 8.8.8.8
  Hex: 45000054abcd40004001c0a801648080808...
  --------------------------------------------------
  ```
**Tips**:
- Generate traffic with `ping 8.8.8.8` or a web browser.
- Use a small `max-packets` value for quick tests.

#### 2. Injecting Custom Packets
**What It Does**: Sends packets with a user-defined payload (hex or ASCII).
**How to Use**:
1. Inject an ASCII payload:
   ```bash
   sudo python3 packetcraft.py -j "Hello" -c 3
   ```
2. Inject a hex payload:
   ```bash
   sudo python3 packetcraft.py -j "0x414243" -c 1
   ```
**What Happens**:
- Packets are sent to `127.0.0.1:80` (localhost for safety):
  ```
  2025-05-15 10:35:00 - Starting PacketCraft: Interface=any, FilterIP=all, FilterPort=all, MaxPackets=100
  2025-05-15 10:35:01 - Injected packet: 5 bytes to 127.0.0.1:80
  2025-05-15 10:35:01 - Injected packet: 5 bytes to 127.0.0.1:80
  2025-05-15 10:35:01 - Injected packet: 5 bytes to 127.0.0.1:80
  ```
**Tips**:
- Hex payloads must use `0x` prefix (e.g., `0x414243` for `ABC`).
- Test injection in a loopback interface (`lo`) to avoid external impact.
- Use a packet sniffer (e.g., `tcpdump`) to verify sent packets.

#### 3. Filtering by IP or Port
**What It Does**: Limits captured packets to a specific IP or port.
**How to Use**:
1. Filter by IP:
   ```bash
   sudo python3 packetcraft.py -f 192.168.1.100 -m 50
   ```
2. Filter by port:
   ```bash
   sudo python3 packetcraft.py -p 80 -m 50
   ```
**What Happens**:
- Only matching packets are logged:
  ```
  2025-05-15 10:40:00 - Starting PacketCraft: Interface=any, FilterIP=192.168.1.100, FilterPort=all, MaxPackets=50
  2025-05-15 10:40:03 - Captured packet: 192.168.1.100 -> 93.184.216.34, 92 bytes
  ```
**Tips**:
- Find your device’s IP with `ifconfig` or `ip addr`.
- Use port `80` for HTTP traffic or `53` for DNS.

#### 4. Limiting Packet Capture
**What It Does**: Stops sniffing after a set number of packets.
**How to Use**:
1. Set a packet limit:
   ```bash
   sudo python3 packetcraft.py -m 200
   ```
**What Happens**:
- Sniffing stops after 200 packets:
  ```
  2025-05-15 10:45:00 - Starting PacketCraft: Interface=any, FilterIP=all, FilterPort=all, MaxPackets=200
  2025-05-15 10:45:15 - Results saved to packetcraft_results_20250515_104515.txt
  ```
**Tips**:
- Use a small limit (e.g., `50`) for quick experiments.
- Increase for longer captures.

#### 5. Quiet Mode
**What It Does**: Reduces terminal output, logging only to the file.
**How to Use**:
1. Enable quiet mode:
   ```bash
   sudo python3 packetcraft.py -q -m 100
   ```
**What Happens**:
- No terminal output; logs go to `packetcraft.log`:
  ```
  $ sudo python3 packetcraft.py -q -m 100
  [No output]
  ```
- Log file example:
  ```
  2025-05-15 10:50:00 - Starting PacketCraft: Interface=any, FilterIP=all, FilterPort=all, MaxPackets=100
  2025-05-15 10:50:05 - Captured packet: 192.168.1.100 -> 8.8.8.8, 84 bytes
  ```
**Tips**:
- Check logs with `cat packetcraft.log` or `tail -f packetcraft.log`.
- Useful for running in the background.

#### 6. Stopping the Tool
**What It Does**: Stops sniffing or injecting when the packet limit is reached or you press Ctrl+C.
**How to Use**:
1. Start a capture:
   ```bash
   sudo python3 packetcraft.py -m 100
   ```
2. Press `Ctrl+C` to stop early.
**What Happens**:
- Sniffing stops, and results are saved:
  ```
  2025-05-15 10:55:00 - Starting PacketCraft: Interface=any, FilterIP=all, FilterPort=all, MaxPackets=100
  ^C
  2025-05-15 10:55:05 - PacketCraft stopped
  ```
**Tips**:
- Always stop the tool to free network resources.
- Results are saved even if stopped early.

### Example Workflow
To experiment with packets in your home network:
1. Set up a test server (e.g., `python3 -m http.server 80`) on a device.
2. Sniff packets:
   ```bash
   sudo python3 packetcraft.py -i wlan0 -f 192.168.1.100 -p 80 -m 50 -q
   ```
3. Generate traffic by visiting `http://192.168.1.100:80` in a browser.
4. Check `packetcraft.log` and `packetcraft_results_*.txt` for captured packets.
5. Inject a test packet:
   ```bash
   sudo python3 packetcraft.py -j "0x414243" -c 1
   ```
6. Stop with `Ctrl+C` and delete output files securely.

## Output
- Logs are saved to `packetcraft.log`.
- Captured packets are saved to `packetcraft_results_<timestamp>.txt`.
- Example results file:
  ```
  [2025-05-15 10:30:05] 192.168.1.100 -> 8.8.8.8
  Hex: 45000054abcd40004001c0a801648080808...
  --------------------------------------------------
  ```

## Important Notes
- **Environment**: Use PacketCraft only in a private network you own (e.g., your home Wi-Fi) with devices you control.
- **Injection Safety**: The tool sends packets to `127.0.0.1:80` by default to avoid external impact. Modify the code carefully if targeting other IPs.
- **Testing**: Use a local server or loopback interface (`lo`) for safe experiments.

## Disclaimer
**Personal Use Only**: PacketCraft is for your personal learning in environments you own or have explicit permission to analyze. Using it on networks or devices without clear authorization is illegal and could lead to legal consequences, technical issues, or unintended harm. Always ensure you have permission from the network owner before capturing or sending packets.

**Safe Use**:
- **Controlled Setup**: Use in a private lab (e.g., home network with your devices) to avoid affecting others.
- **Data Security**: Output files (`packetcraft.log`, `packetcraft_results_*.txt`) may contain sensitive data. Store them securely and delete them after use (e.g., `rm packetcraft_*.txt`).
- **Legal Compliance**: Follow all applicable laws and regulations in your area.
- **No Warranty**: This tool is provided “as is” for educational purposes. You are responsible for its use and any consequences.

**What to Avoid**:
- Do not use on public networks (e.g., public Wi-Fi) or devices you don’t own.
- Do not send packets to external IPs without permission.
- Do not share output files, as they may contain private data.

## Limitations
- Requires administrator privileges and Scapy.
- Only supports basic IP/TCP/UDP packets for injection.
- May miss packets if filters are too strict or traffic is low.
- Simple design; does not support advanced packet crafting like some tools.

## Testing Tips
- List interfaces: `ifconfig` or `ip link`.
- Generate traffic: Use `ping`, a web browser, or `python3 -m http.server 80`.
- Verify injection: Run `tcpdump` (e.g., `sudo tcpdump -i lo port 80`) to see sent packets.
- Secure outputs: Delete files after use (`rm packetcraft_*.txt`).
- Check logs in real-time: `tail -f packetcraft.log`.

## Troubleshooting
- **No packets captured**: Ensure traffic is present, the correct interface is used, and filters aren’t too strict.
- **Permission errors**: Run with `sudo`.
- **Scapy errors**: Verify Scapy is installed (`pip3 install scapy`).
- **Invalid hex payload**: Ensure hex strings use `0x` prefix and valid characters (e.g., `0x414243`).

## License
This tool is for your personal use. No formal license is provided, but please use it responsibly.