# VoIPFlood

## Description
VoIPFlood is a Python tool you can use to simulate VoIP traffic by sending a high volume of UDP packets with an IAX-like payload to a target in your own private network. It helps you learn how VoIP servers handle heavy traffic in a controlled environment, like a home lab with devices you own. Inspired by tools that test network resilience, VoIPFlood is designed for your personal experimentation to study packet behavior.

**Important**: This tool is for your personal use only in networks and devices you own or have explicit permission to test. Using it on networks or devices without clear authorization is illegal and could cause serious issues.

## Features
- Sends UDP packets with a simplified IAX-like payload to a target IP and port.
- Configurable packet count, size, and sending rate for controlled experiments.
- Optional source IP filtering to simulate specific clients.
- Logs sent packets to a text file with timestamps and details.
- Quiet mode to reduce terminal output.
- Supports custom hex payloads or a default IAX-like payload.
- Simple design for easy use in personal projects.

## Installation
1. **What You Need**:
   - Python 3.12 or later (check with `python3 --version`).
   - A computer on a private network you control (e.g., your home Wi-Fi).
   - Administrator access (e.g., `sudo`) may be needed for binding to specific source IPs.
2. Save the `voipflood.py` script to a folder (e.g., `/home/user/voipflood/`).
3. Run the script:
   ```bash
   python3 voipflood.py --help
   ```

## How to Use
VoIPFlood sends UDP packets to a target IP and port to simulate VoIP traffic. You specify the target, packet details, and optional settings like source IP or custom payload. Below is a guide on how to use each feature with examples and expected results.

### Basic Usage
Send 100 packets to a target IP on the default IAX port (4569):
```bash
python3 voipflood.py 192.168.1.100
```

### Options
- `target_ip`: Target IP address (e.g., `192.168.1.100`).
- `-p, --port`: Target port (default: `4569` for IAX).
- `-c, --count`: Number of packets to send (default: `100`).
- `-s, --size`: Packet size in bytes (default: `100`).
- `-r, --rate`: Seconds between packets (default: `0.01`).
- `-i, --source-ip`: Source IP address (optional, e.g., `192.168.1.200`).
- `-l, --payload`: Custom hex payload (e.g., `0x414243` for `ABC`).
- `-q, --quiet`: Run quietly (logs to file only).

### Using Each Feature

#### 1. Sending Packets
**What It Does**: Sends UDP packets with an IAX-like payload to a target.
**How to Use**:
1. Send 100 packets to a VoIP server:
   ```bash
   python3 voipflood.py 192.168.1.100 -c 100
   ```
2. Use a different port:
   ```bash
   python3 voipflood.py 192.168.1.100 -p 5060 -c 50
   ```
**What Happens**:
- Packets are sent and logged to `voipflood.log` and a results file:
  ```
  2025-05-15 10:30:00 - Starting VoIPFlood: Target=192.168.1.100:4569, Packets=100, Rate=0.01s
  2025-05-15 10:30:01 - Sent packet 1 to 192.168.1.100:4569, 100 bytes
  ...
  2025-05-15 10:30:03 - Sent 100 packets. Results saved to voipflood_results_20250515_103003.txt
  ```
- Results file example:
  ```
  [2025-05-15 10:30:01] Sent to 192.168.1.100:4569, 100 bytes
  ...
  ```
**Tips**:
- Set up a test VoIP server (e.g., Asterisk on a VM) to receive packets.
- Use a small `count` for quick tests.

#### 2. Customizing Packet Size and Rate
**What It Does**: Adjusts the size of packets and the sending rate.
**How to Use**:
1. Send larger packets:
   ```bash
   python3 voipflood.py 192.168.1.100 -s 200 -c 50
   ```
2. Slow down the rate:
   ```bash
   python3 voipflood.py 192.168.1.100 -r 0.1 -c 20
   ```
**What Happens**:
- Packets are sent with the specified size and rate:
  ```
  2025-05-15 10:35:00 - Starting VoIPFlood: Target=192.168.1.100:4569, Packets=50, Rate=0.01s
  2025-05-15 10:35:01 - Sent packet 1 to 192.168.1.100:4569, 200 bytes
  ```
**Tips**:
- Larger packets (`-s`) increase traffic; smaller rates (`-r`) slow sending.
- Test different combinations to observe server behavior.

#### 3. Using a Source IP
**What It Does**: Sends packets from a specific source IP.
**How to Use**:
1. Specify a source IP:
   ```bash
   sudo python3 voipflood.py 192.168.1.100 -i 192.168.1.200 -c 50
   ```
**What Happens**:
- Packets appear to come from the source IP:
  ```
  2025-05-15 10:40:00 - Starting VoIPFlood: Target=192.168.1.100:4569, Packets=50, Rate=0.01s
  2025-05-15 10:40:01 - Sent packet 1 to 192.168.1.100:4569, 100 bytes
  ```
**Tips**:
- Use `sudo` for binding to a source IP.
- Ensure the source IP is valid on your network.

#### 4. Using a Custom Payload
**What It Does**: Sends packets with a user-defined hex payload.
**How to Use**:
1. Specify a hex payload:
   ```bash
   python3 voipflood.py 192.168.1.100 -l 0x414243 -c 10
   ```
**What Happens**:
- Packets use the custom payload:
  ```
  2025-05-15 10:45:00 - Starting VoIPFlood: Target=192.168.1.100:4569, Packets=10, Rate=0.01s
  2025-05-15 10:45:01 - Sent packet 1 to 192.168.1.100:4569, 3 bytes
  ```
**Tips**:
- Use `0x` prefix for hex (e.g., `0x414243` for `ABC`).
- Ensure the payload fits the packet size or adjust `-s`.

#### 5. Quiet Mode
**What It Does**: Reduces terminal output, logging only to the file.
**How to Use**:
1. Enable quiet mode:
   ```bash
   python3 voipflood.py 192.168.1.100 -q -c 100
   ```
**What Happens**:
- No terminal output; logs go to `voipflood.log`:
  ```
  $ python3 voipflood.py 192.168.1.100 -q -c 100
  [No output]
  ```
- Log file example:
  ```
  2025-05-15 10:50:00 - Starting VoIPFlood: Target=192.168.1.100:4569, Packets=100, Rate=0.01s
  2025-05-15 10:50:01 - Sent packet 1 to 192.168.1.100:4569, 100 bytes
  ```
**Tips**:
- Check logs with `cat voipflood.log` or `tail -f voipflood.log`.
- Useful for running in the background.

#### 6. Stopping the Tool
**What It Does**: Stops sending packets when the count is reached or you press Ctrl+C.
**How to Use**:
1. Start flooding:
   ```bash
   python3 voipflood.py 192.168.1.100 -c 100
   ```
2. Press `Ctrl+C` to stop early.
**What Happens**:
- Flooding stops, and results are saved:
  ```
  2025-05-15 10:55:00 - Starting VoIPFlood: Target=192.168.1.100:4569, Packets=100, Rate=0.01s
  ^C
  2025-05-15 10:55:02 - VoIPFlood stopped by user
  2025-05-15 10:55:02 - Sent 20 packets. Results saved to voipflood_results_20250515_105502.txt
  ```
**Tips**:
- Always stop the tool to free network resources.
- Results are saved even if stopped early.

### Example Workflow
To experiment with VoIP traffic in your home network:
1. Set up a test VoIP server (e.g., Asterisk on a VM at `192.168.1.100:4569`).
2. Send 50 packets:
   ```bash
   python3 voipflood.py 192.168.1.100 -c 50 -s 150 -r 0.05 -q
   ```
3. Monitor the server’s response (e.g., CPU usage, logs).
4. Try a custom payload:
   ```bash
   python3 voipflood.py 192.168.1.100 -l 0x80000001 -c 20
   ```
5. Check `voipflood.log` and `voipflood_results_*.txt` for sent packet details.
6. Stop with `Ctrl+C` and delete output files securely.

## Output
- Logs are saved to `voipflood.log`.
- Packet details are saved to `voipflood_results_<timestamp>.txt`.
- Example results file:
  ```
  [2025-05-15 10:30:01] Sent to 192.168.1.100:4569, 100 bytes
  ...
  ```

## Important Notes
- **Environment**: Use VoIPFlood only in a private network you own (e.g., your home Wi-Fi) with devices you control.
- **Target Safety**: The tool sends packets to a specified IP/port (default: `4569` for IAX). Use a test server (e.g., `127.0.0.1` or a local VM) to avoid external impact.
- **Testing**: Set up a local VoIP server (e.g., Asterisk) for safe experiments.

## Disclaimer
**Personal Use Only**: VoIPFlood is for your personal learning in environments you own or have explicit permission to test. Using it on networks or devices without clear authorization is illegal and could lead to legal consequences, technical issues, or unintended harm. Always ensure you have permission from the network owner before sending packets.

**Safe Use**:
- **Controlled Setup**: Use in a private lab (e.g., home network with your devices) to avoid affecting others. For example, target `127.0.0.1` or a VM you control.
- **Data Security**: Output files (`voipflood.log`, `voipflood_results_*.txt`) may contain network details. Store them securely and delete them after use (e.g., `rm voipflood_*.txt`).
- **Legal Compliance**: Follow all applicable laws and regulations in your area.
- **No Warranty**: This tool is provided “as is” for educational purposes. You are responsible for its use and any consequences.

**What to Avoid**:
- Do not use on public networks (e.g., public Wi-Fi) or devices you don’t own.
- Do not target external IPs or servers without permission.
- Do not share output files, as they may contain private data.

## Limitations
- Requires administrator privileges for binding to source IPs.
- Uses a simplified IAX-like payload; not a full IAX protocol implementation.
- May not stress modern servers significantly due to simple design.
- Limited to UDP packets; no support for other protocols.

## Testing Tips
- Set up Asterisk: Install Asterisk on a VM and configure it to listen on `4569`.
- Monitor traffic: Use `tcpdump` (e.g., `sudo tcpdump -i eth0 udp port 4569`) to verify packets.
- Secure outputs: Delete files after use (`rm voipflood_*.txt`).
- Check logs in real-time: `tail -f voipflood.log`.
- Test locally: Use `127.0.0.1` as the target for safe experiments.

## Troubleshooting
- **No packets sent**: Ensure the target IP/port is reachable and no firewall blocks UDP.
- **Permission errors**: Run with `sudo` for source IP binding.
- **Invalid payload**: Use `0x` prefix and valid hex for custom payloads.
- **Server unaffected**: Increase `count`, `size`, or decrease `rate` to simulate heavier traffic.

## License
This tool is for your personal use. No formal license is provided, but please use it responsibly.