# CookieSniff

## Description
CookieSniff is a Python tool you can use to capture HTTP cookies from network traffic in your own private network. It helps you learn how web sessions work by logging cookies sent over unencrypted HTTP connections. Inspired by tools that analyze network data, CookieSniff is designed for your personal experimentation in a controlled environment, like a home lab with devices you own.

**Important**: This tool is for your personal use only in networks and devices you own or have explicit permission to analyze. Using it on networks or devices without clear authorization is illegal and could cause serious issues.

## Features
- Captures HTTP cookies (Cookie and Set-Cookie headers) from unencrypted traffic.
- Filters by network interface or specific host IP.
- Limits capture to a set number of packets for controlled experiments.
- Logs cookies to a text file with timestamps and IP addresses.
- Quiet mode to reduce terminal output.
- Optional raw packet saving for detailed analysis.
- Simple design for easy use in personal projects.

## Installation
1. **What You Need**:
   - Python 3.12 or later (check with `python3 --version`).
   - Scapy library for packet sniffing.
   - A computer on a private network you control (e.g., your home Wi-Fi).
   - Administrator access (e.g., `sudo`) to capture network packets.
2. Install Scapy:
   ```bash
   pip3 install scapy
   ```
3. Save the `cookiesniff.py` script to a folder (e.g., `/home/user/cookiesniff/`).
4. Run the script with administrator privileges:
   ```bash
   sudo python3 cookiesniff.py --help
   ```

## How to Use
CookieSniff captures HTTP cookies from network traffic. You need to specify options like the network interface, target host (optional), and how many packets to capture. Below is a guide on how to use each feature with examples and expected results.

### Basic Usage
Capture cookies from HTTP traffic on any interface, up to 100 packets:
```bash
sudo python3 cookiesniff.py -m 100
```

### Options
- `-i, --interface`: Network interface (e.g., `eth0`, `wlan0`).
- `-H, --host`: Filter cookies for a specific IP (e.g., `192.168.1.100`).
- `-m, --max-packets`: Maximum packets to capture (default: `100`).
- `-q, --quiet`: Run quietly (logs to file only).
- `-r, --save-raw`: Save raw packet data to a separate file.

### Using Each Feature

#### 1. Capturing HTTP Cookies
**What It Does**: Sniffs HTTP traffic to extract cookies from unencrypted connections.
**How to Use**:
1. Run a basic capture:
   ```bash
   sudo python3 cookiesniff.py -m 100
   ```
2. Visit an HTTP website (not HTTPS) on a device in your network to generate traffic.
**What Happens**:
- Cookies are logged to `cookiesniff.log` and a results file:
  ```
  2025-05-15 10:00:00 - Starting CookieSniff: Interface=any, Host=all, MaxPackets=100
  2025-05-15 10:00:05 - Cookie captured: 192.168.1.100 -> 93.184.216.34, ['Cookie: session=abc123']
  2025-05-15 10:00:10 - Results saved to cookiesniff_results_20250515_100010.txt
  ```
- Results file example:
  ```
  [2025-05-15 10:00:05] 192.168.1.100 -> 93.184.216.34
  Cookie: session=abc123
  --------------------------------------------------
  ```
**Tips**:
- Use a test HTTP server (e.g., `python3 -m http.server`) to generate traffic.
- Cookies are only captured from unencrypted HTTP traffic, not HTTPS.

#### 2. Filtering by Interface or Host
**What It Does**: Limits sniffing to a specific network interface or IP address.
**How to Use**:
1. Specify an interface:
   ```bash
   sudo python3 cookiesniff.py -i eth0 -m 50
   ```
2. Filter by a host IP:
   ```bash
   sudo python3 cookiesniff.py -H 192.168.1.100 -m 50
   ```
**What Happens**:
- Only packets from the specified interface or host are processed:
  ```
  2025-05-15 10:05:00 - Starting CookieSniff: Interface=eth0, Host=192.168.1.100, MaxPackets=50
  2025-05-15 10:05:03 - Cookie captured: 192.168.1.100 -> 93.184.216.34, ['Set-Cookie: id=xyz789']
  ```
**Tips**:
- Find interfaces with `ifconfig` or `ip link`.
- Use your device’s IP to focus on its traffic.

#### 3. Limiting Packet Capture
**What It Does**: Stops sniffing after a set number of packets.
**How to Use**:
1. Set a packet limit:
   ```bash
   sudo python3 cookiesniff.py -m 200
   ```
**What Happens**:
- Sniffing stops after 200 packets:
  ```
  2025-05-15 10:10:00 - Starting CookieSniff: Interface=any, Host=all, MaxPackets=200
  2025-05-15 10:10:15 - Results saved to cookiesniff_results_20250515_101015.txt
  ```
**Tips**:
- Use a small limit (e.g., `50`) for quick tests.
- Increase for longer experiments.

#### 4. Quiet Mode
**What It Does**: Reduces terminal output, logging only to the file.
**How to Use**:
1. Enable quiet mode:
   ```bash
   sudo python3 cookiesniff.py -q -m 100
   ```
**What Happens**:
- No terminal output; logs go to `cookiesniff.log`:
  ```
  $ sudo python3 cookiesniff.py -q -m 100
  [No output]
  ```
- Log file example:
  ```
  2025-05-15 10:15:00 - Starting CookieSniff: Interface=any, Host=all, MaxPackets=100
  2025-05-15 10:15:05 - Cookie captured: 192.168.1.100 -> 93.184.216.34, ['Cookie: session=abc123']
  ```
**Tips**:
- Check logs with `cat cookiesniff.log` or `tail -f cookiesniff.log`.
- Useful for running in the background.

#### 5. Saving Raw Packets
**What It Does**: Saves full packet data for detailed analysis.
**How to Use**:
1. Enable raw packet saving:
   ```bash
   sudo python3 cookiesniff.py -r -m 50
   ```
**What Happens**:
- Raw packets are saved to a separate file:
  ```
  2025-05-15 10:20:00 - Starting CookieSniff: Interface=any, Host=all, MaxPackets=50
  2025-05-15 10:20:05 - Cookie captured: 192.168.1.100 -> 93.184.216.34, ['Cookie: session=abc123']
  2025-05-15 10:20:10 - Raw packets saved to cookiesniff_raw_20250515_102010.txt
  ```
- Raw file example:
  ```
  [2025-05-15 10:20:05] 192.168.1.100 -> 93.184.216.34
  GET / HTTP/1.1
  Host: example.com
  Cookie: session=abc123
  ...
  --------------------------------------------------
  ```
**Tips**:
- Use raw data to study full HTTP requests.
- Keep raw files secure as they contain detailed traffic.

#### 6. Stopping the Tool
**What It Does**: Stops sniffing when the packet limit is reached or you press Ctrl+C.
**How to Use**:
1. Start a capture:
   ```bash
   sudo python3 cookiesniff.py -m 100
   ```
2. Press `Ctrl+C` to stop early.
**What Happens**:
- Sniffing stops, and results are saved:
  ```
  2025-05-15 10:25:00 - Starting CookieSniff: Interface=any, Host=all, MaxPackets=100
  ^C
  2025-05-15 10:25:05 - CookieSniff stopped
  2025-05-15 10:25:05 - Results saved to cookiesniff_results_20250515_102505.txt
  ```
**Tips**:
- Always stop the tool to free network resources.
- Results are saved even if stopped early.

### Example Workflow
To learn about cookies in your home network:
1. Set up a test HTTP server on a device (e.g., `python3 -m http.server 80`).
2. Run CookieSniff on another device:
   ```bash
   sudo python3 cookiesniff.py -i wlan0 -H 192.168.1.100 -m 50 -q -r
   ```
3. Visit the test server’s IP in a browser (e.g., `http://192.168.1.100:80`).
4. Check `cookiesniff.log`, `cookiesniff_results_*.txt`, and `cookiesniff_raw_*.txt` for captured cookies.
5. Stop with `Ctrl+C` and delete output files securely.

## Output
- Logs are saved to `cookiesniff.log`.
- Cookie results are saved to `cookiesniff_results_<timestamp>.txt`.
- Raw packets (if enabled) are saved to `cookiesniff_raw_<timestamp>.txt`.
- Example results file:
  ```
  [2025-05-15 10:00:05] 192.168.1.100 -> 93.184.216.34
  Cookie: session=abc123
  --------------------------------------------------
  ```

## Important Notes
- **Environment**: Use CookieSniff only in a private network you own (e.g., your home Wi-Fi) with devices you control.
- **HTTPS Limitation**: CookieSniff only captures cookies from unencrypted HTTP traffic, as HTTPS encrypts data.
- **Testing**: Set up a local HTTP server for safe experiments, as public websites typically use HTTPS.

## Disclaimer
**Personal Use Only**: CookieSniff is for your personal learning in environments you own or have explicit permission to analyze. Using it on networks or devices without clear authorization is illegal and could lead to legal consequences, technical issues, or unintended harm. Always ensure you have permission from the network owner before capturing traffic.

**Safe Use**:
- **Controlled Setup**: Use in a private lab (e.g., home network with your devices) to avoid affecting others.
- **Data Security**: Output files (`cookiesniff.log`, `cookiesniff_results_*.txt`, `cookiesniff_raw_*.txt`) may contain sensitive data. Store them securely and delete them after use (e.g., `rm cookiesniff_*.txt`).
- **Legal Compliance**: Follow all applicable laws and regulations in your area.
- **No Warranty**: This tool is provided “as is” for educational purposes. You are responsible for its use and any consequences.

**What to Avoid**:
- Do not use on public networks (e.g., coffee shop Wi-Fi) or devices you don’t own.
- Do not attempt to capture or use cookies from real websites without permission.
- Do not share output files with others, as they may contain private data.

## Limitations
- Only captures cookies from unencrypted HTTP traffic (not HTTPS).
- Requires administrator privileges and Scapy.
- May miss cookies if traffic is low or misconfigured.
- Simple design; does not proxy or reuse cookies like some advanced tools.

## Testing Tips
- List interfaces: `ifconfig` or `ip link`.
- Test with an HTTP server: `python3 -m http.server 80` on a device.
- Secure outputs: Delete files after use (`rm cookiesniff_*.txt`).
- Check logs in real-time: `tail -f cookiesniff.log`.

## Troubleshooting
- **No cookies captured**: Ensure HTTP (not HTTPS) traffic is present and the correct interface/host is set.
- **Permission errors**: Run with `sudo`.
- **Scapy errors**: Verify Scapy is installed (`pip3 install scapy`).

## License
This tool is for your personal use. No formal license is provided, but please use it responsibly.