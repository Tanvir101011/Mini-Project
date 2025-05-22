# PacketJester

## Description
PacketJester is a Python tool you can use to simulate network traffic obfuscation in your own private network to learn about how protocol analyzers (e.g., Wireshark, tcpdump) interpret manipulated traffic. It helps you study network security, packet injection, and evasion techniques by injecting fake TCP packets and scrambling sessions to confuse sniffers, similar to the **SniffJoke** tool’s functionality. Inspired by **SniffJoke**, PacketJester is designed for your personal experimentation in a controlled environment, like a home lab with network interfaces and devices you own or have explicit permission to test.

**Important**: This tool is for your personal use only with networks and devices you own or have explicit permission to test. Injecting packets or manipulating traffic without clear authorization is illegal and could cause serious issues, such as network disruption or legal consequences. The tool avoids external network interactions beyond your lab to prevent misuse, ensuring it remains a safe learning tool.

## Features
- Injects fake TCP packets with random payloads to confuse protocol analyzers.
- Scrambles TCP session sequence numbers to disrupt session tracking.
- Spoofs source IPs within your lab network (e.g., `192.168.1.0/24`).
- Supports targeting specific IPs or ports (e.g., HTTP on port 80).
- Logs injected packets and session details to a file for analysis.
- Quiet mode to reduce terminal output.
- Configurable interface, target IP, port, spoof subnet, and injection rate.
- Simple design for educational use in personal projects.

## Installation
1. **What You Need**:
   - Linux OS (e.g., Ubuntu 24.04, check with `uname -a`).
   - Python 3.12 or later (check with `python3 --version`).
   - A network interface (e.g., `eth0`, check with `ip link`).
   - Root/admin privileges (e.g., `sudo` on Linux).
   - A computer on a private network you control (e.g., your home lab).
2. Install dependencies:
   - Save the `setup_packetjester.sh` script to a folder (e.g., `/home/user/packetjester/`).
   - Make it executable and run it:
     ```bash
     chmod +x setup_packetjester.sh
     ./setup_packetjester.sh
     ```
   - This installs `scapy` and `netifaces`.
3. Save the `packetjester.py` file to the same folder.
4. Run the script:
   ```bash
   sudo python3 packetjester.py --help
   ```

## How to Use
PacketJester simulates network traffic obfuscation by injecting fake TCP packets with random payloads and sequence numbers to disrupt protocol analyzers’ ability to track sessions. It spoofs source IPs within your lab network and targets specific IPs/ports, allowing you to study sniffer behavior. Below is a guide on how to use each feature with examples and expected results.

### Basic Usage
Start injecting fake packets targeting a device:
```bash
sudo python3 packetjester.py -i eth0 -t 192.168.1.100
```

Target a specific port with a higher injection rate:
```bash
sudo python3 packetjester.py -i eth0 -t 192.168.1.100 -p 443 -r 5
```

### Options
- `-i, --interface`: Network interface (e.g., `eth0`, required).
- `-t, --target-ip`: Target IP address (e.g., `192.168.1.100`, required).
- `-p, --target-port`: Target port (default: 80).
- `-s, --spoof-subnet`: Subnet for spoofed IPs (default: `192.168.1.0/24`).
- `-r, --rate`: Injection rate (packets/second, default: 1).
- `-q, --quiet`: Run quietly (logs to file only).

### Using Each Feature

#### 1. Injecting Fake Packets
**What It Does**: Sends fake TCP packets with random payloads to confuse sniffers.
**How to Use**:
1. Find your network interface (e.g., `ip link`).
2. Identify a target IP in your lab (e.g., `192.168.1.100`).
3. Run:
   ```bash
   sudo python3 packetjester.py -i eth0 -t 192.168.1.100
   ```
4. Monitor traffic with Wireshark or tcpdump on another device.
**What Happens**:
- PacketJester injects packets, logged to the terminal and file:
  ```
  2025-05-15 10:30:00 - Starting PacketJester: Target=192.168.1.100:80, Spoof Subnet=192.168.1.0/24, Rate=1/s
  2025-05-15 10:30:01 - Injected packet #1: IP / TCP 192.168.1.123:54321 > 192.168.1.100:80 S / Raw
  2025-05-15 10:30:02 - Injected packet #2: IP / TCP 192.168.1.45:12345 > 192.168.1.100:80 A / Raw
  ```
- Results file example (`packetjester_results_20250515_103000.txt`):
  ```
  [2025-05-15 10:30:01] IP / TCP 192.168.1.123:54321 > 192.168.1.100:80 S / Raw
  [2025-05-15 10:30:02] IP / TCP 192.168.1.45:12345 > 192.168.1.100:80 A / Raw
  ```
**Tips**:
- Use a VM or device in your lab as the target.
- Run Wireshark (`sudo wireshark -i eth0`) to observe fake packets.
- Adjust the rate (`-r 10`) for more aggressive injection.

#### 2. Scrambling TCP Sessions
**What It Does**: Disrupts session tracking by randomizing TCP sequence numbers and flags.
**How to Use**:
1. Target a server (e.g., a local HTTP server at `192.168.1.100:80`).
2. Run:
   ```bash
   sudo python3 packetjester.py -i eth0 -t 192.168.1.100 -p 80 -r 2
   ```
**What Happens**:
- Random sequence numbers and flags (SYN, ACK, PUSH, FIN) confuse sniffers:
  ```
  2025-05-15 10:35:00 - Starting PacketJester: Target=192.168.1.100:80, Spoof Subnet=192.168.1.0/24, Rate=2/s
  2025-05-15 10:35:01 - Injected packet #1: IP / TCP 192.168.1.67:45678 > 192.168.1.100:80 F / Raw
  2025-05-15 10:35:01 - Injected packet #2: IP / TCP 192.168.1.89:23456 > 192.168.1.100:80 P / Raw
  ```
- Wireshark shows fragmented or invalid TCP sessions.
**Tips**:
- Test with a local server (e.g., `python3 -m http.server 80`).
- Use `tcpdump -i eth0` to verify scrambled sessions.
- Increase rate for more disruption (`-r 5`).

#### 3. Spoofing Source IPs
**What It Does**: Spoofs source IPs within your lab subnet to mask the injector.
**How to Use**:
1. Specify a subnet (e.g., `192.168.0.0/24`):
   ```bash
   sudo python3 packetjester.py -i eth0 -t 192.168.1.100 -s 192.168.0.0/24
   ```
**What Happens**:
- Packets appear to come from random IPs in the subnet:
  ```
  2025-05-15 10:40:00 - Injected packet #1: IP / TCP 192.168.0.15:54321 > 192.168.1.100:80 S / Raw
  2025-05-15 10:40:01 - Injected packet #2: IP / TCP 192.168.0.200:12345 > 192.168.1.100:80 A / Raw
  ```
**Tips**:
- Match the subnet to your lab network (`ip addr`).
- Verify spoofed IPs in Wireshark.
- Avoid external IPs to prevent misuse.

#### 4. Quiet Mode
**What It Does**: Reduces terminal output, logging only to the file.
**How to Use**:
1. Enable quiet mode:
   ```bash
   sudo python3 packetjester.py -i eth0 -t 192.168.1.100 -q
   ```
**What Happens**:
- No terminal output; logs go to `packetjester.log`:
  ```
  $ sudo python3 packetjester.py -i eth0 -t 192.168.1.100 -q
  [No output]
  ```
- Log file example:
  ```
  2025-05-15 10:45:00 - Starting PacketJester: Target=192.168.1.100:80, Spoof Subnet=192.168.1.0/24, Rate=1/s
  2025-05-15 10:45:01 - Injected packet #1: IP / TCP 192.168.1.123:54321 > 192.168.1.100:80 S / Raw
  ```
**Tips**:
- Check logs with `cat packetjester.log` or `tail -f packetjester.log`.
- Useful for background testing.

#### 5. Stopping the Tool
**What It Does**: Stops packet injection and saves logs when done or interrupted.
**How to Use**:
1. Start the attack:
   ```bash
   sudo python3 packetjester.py -i eth0 -t 192.168.1.100
   ```
2. Press `Ctrl+C` to stop.
**What Happens**:
- The tool stops, saves logs, and cleans up:
  ```
  2025-05-15 10:50:00 - Starting PacketJester: Target=192.168.1.100:80, Spoof Subnet=192.168.1.0/24, Rate=1/s
  ^C
  2025-05-15 10:50:01 - PacketJester stopped. Total packets injected: 2
  2025-05-15 10:50:01 - Results saved to packetjester_results_20250515_105001.txt
  ```
**Tips**:
- Always stop the tool to free resources.
- Results are saved even if stopped early.

### Example Workflow
To experiment with traffic obfuscation in your home lab:
1. Set up a test network (e.g., a VM with `eth0` and a target device at `192.168.1.100`).
2. Install dependencies:
   ```bash
   ./setup_packetjester.sh
   ```
3. Start the attack:
   ```bash
   sudo python3 packetjester.py -i eth0 -t 192.168.1.100 -p 80 -r 2 -q
   ```
4. Monitor traffic with Wireshark or tcpdump on another device.
5. Review `packetjester.log` and `packetjester_results_*.txt` for packet details.
6. Stop with `Ctrl+C` and delete output files securely.

## Output
- Logs are saved to `packetjester.log`.
- Packet details are saved to `packetjester_results_<timestamp>.txt`.
- Example results file:
  ```
  [2025-05-15 10:30:01] IP / TCP 192.168.1.123:54321 > 192.168.1.100:80 S / Raw
  [2025-05-15 10:30:02] IP / TCP 192.168.1.45:12345 > 192.168.1.100:80 A / Raw
  [2025-05-15 10:30:03] Total packets injected: 2
  ```

## Important Notes
- **Environment**: Use PacketJester only on networks and devices you own or have explicit permission to test (e.g., a local VM or home device).
- **Root Privileges**: Requires `sudo` for packet injection via Scapy.
- **No External Interaction**: The tool avoids external network interactions to prevent misuse, as recommended for traffic manipulation tools.
- **Sniffer Behavior**: Modern protocol analyzers (e.g., Wireshark) may filter out invalid packets, but scrambled sessions can still disrupt analysis. Test with multiple sniffers for comparison.
- **Ethical Use**: Do not use on unauthorized networks, as packet injection can disrupt services or trigger security alerts, which is illegal without permission.

## Disclaimer
**Personal Use Only**: PacketJester is for your personal learning with networks and devices you own or have explicit permission to test. Injecting packets or manipulating traffic without clear authorization is illegal and could lead to legal consequences, network disruptions, or unintended harm. Always ensure you have permission from the network owner before using this tool.

**Safe Use**:
- **Controlled Setup**: Use in a private lab (e.g., home network with your devices) to avoid affecting others. For example, test on `eth0` in a local VM.
- **Data Security**: Output files (`packetjester.log`, `packetjester_results_*.txt`) may contain network data. Store them securely and delete them after use (e.g., `rm packetjester_*.txt`).
- **Legal Compliance**: Follow all applicable laws and regulations in your area, including privacy and network security laws.
- **No Warranty**: This tool is provided “as is” for educational purposes. You are responsible for its use and any consequences.

**What to Avoid**:
- Do not use on public networks (e.g., corporate or public Wi-Fi) without permission.
- Do not share output files, as they may contain sensitive data.
- Do not target devices without explicit authorization, as it’s illegal and disruptive.
- Avoid injecting packets to external IPs to prevent unintended consequences.

## Limitations
- Requires a compatible network interface and root privileges.
- Limited to TCP packet injection; does not support UDP or other protocols like **SniffJoke**.
- Basic obfuscation; advanced tools like **SniffJoke** may include encryption or plugin support.
- Effectiveness depends on sniffer configuration (e.g., Wireshark’s filters).
- No real-time traffic analysis or session hijacking, unlike tools like Ettercap.

## Testing Tips
- Verify interface: Use `ip link` to check `eth0` is active.
- Test target: Ping the target IP (`ping 192.168.1.100`) to ensure reachability.
- Monitor traffic: Use `wireshark -i eth0` or `tcpdump -i eth0` to observe injected packets.
- Secure outputs: Delete files after use (`rm packetjester_*.txt`).
- Check logs in real-time: `tail -f packetjester.log`.
- Test without internet: Ensure the setup is isolated to avoid misuse.

## License
This tool is for your personal use. No formal license is provided, but please use it responsibly.