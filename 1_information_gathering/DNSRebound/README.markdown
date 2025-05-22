# DNSRebound

## Description
DNSRebound is a Python tool you can use to simulate a DNS rebinding attack in your own private network to learn about how browsers, DNS, and the Same-Origin Policy (SOP) interact. It helps you study network security by creating a malicious webpage that manipulates DNS responses to trick a browser into accessing internal network resources, similar to the **rebind** tool’s functionality. Inspired by **rebind**, DNSRebound is designed for your personal experimentation in a controlled environment, like a home lab with network interfaces and devices you own or have explicit permission to test.

**Important**: This tool is for your personal use only with networks and devices you own or have explicit permission to test. Performing DNS rebinding attacks without clear authorization is illegal and could cause serious issues. The tool avoids external network interactions beyond your lab to prevent misuse, ensuring it remains a safe learning tool.

## Features
- Runs a custom DNS server to serve initial public IP and subsequent internal IPs with short TTLs.
- Hosts a malicious webpage with JavaScript to make repeated requests, exploiting SOP bypass.
- Supports targeting specific internal IPs (e.g., `192.168.1.1` for routers).
- Logs HTTP requests and DNS queries to a file for analysis.
- Includes a sample payload to fetch data from internal web interfaces.
- Quiet mode to reduce terminal output.
- Configurable interface, domain, and ports for flexibility.
- Simple design for educational use in personal projects.

## Installation
1. **What You Need**:
   - Linux OS (e.g., Ubuntu 24.04, check with `uname -a`).
   - Python 3.12 or later (check with `python3 --version`).
   - A network interface (e.g., `eth0`, check with `ip link`).
   - Root/admin privileges (e.g., `sudo` on Linux).
   - A computer on a private network you control (e.g., your home lab).
2. Install dependencies:
   - Save the `setup_dnsrebound.sh` script to a folder (e.g., `/home/user/dnsrebound/`).
   - Make it executable and run it:
     ```bash
     chmod +x setup_dnsrebound.sh
     ./setup_dnsrebound.sh
     ```
   - This installs `dnslib` and `aiohttp`.
3. Save the `dnsrebound.py` and `malicious.html` files to the same folder.
   - Edit `malicious.html` to replace `REBIND_DOMAIN` with your domain (e.g., `rebind.local`).
4. Run the script:
   ```bash
   sudo python3 dnsrebound.py --help
   ```

## How to Use
DNSRebound simulates a DNS rebinding attack by running a DNS server that alternates between a public IP and an internal IP (e.g., a router’s admin page at `192.168.1.1`) and a web server that serves a malicious webpage with JavaScript. The webpage makes repeated requests to exploit the SOP bypass, allowing you to study internal network access. Below is a guide on how to use each feature with examples and expected results.

### Basic Usage
Start a DNS rebinding attack targeting a router:
```bash
sudo python3 dnsrebound.py -i eth0 -d rebind.local -t 192.168.1.1
```

Specify a custom public IP:
```bash
sudo python3 dnsrebound.py -i eth0 -d rebind.local -p 203.0.113.1 -t 192.168.1.1
```

### Options
- `-i, --interface`: Network interface (e.g., `eth0`, required).
- `-d, --domain`: Domain for rebinding (e.g., `rebind.local`, required).
- `-p, --public-ip`: Public IP (default: auto-detected).
- `-t, --target-ip`: Target internal IP (default: `192.168.1.1`).
- `--dns-port`: DNS server port (default: 53).
- `--web-port`: Web server port (default: 80).
- `-q, --quiet`: Run quietly (logs to file only).

### Using Each Feature

#### 1. Running the DNS and Web Servers
**What It Does**: Starts a DNS server to alternate between public and internal IPs and a web server to serve a malicious webpage.
**How to Use**:
1. Find your network interface (e.g., `ip link`).
2. Edit `malicious.html` to set `REBIND_DOMAIN` to your domain (e.g., `rebind.local`).
3. Run:
   ```bash
   sudo python3 dnsrebound.py -i eth0 -d rebind.local -t 192.168.1.1
   ```
4. Configure a test device to use your machine’s IP as the DNS server (e.g., set DNS to your `eth0` IP in a VM).
5. Visit `http://rebind.local` in a browser on the test device.
**What Happens**:
- The DNS server responds with the public IP first, then the target IP:
  ```
  2025-05-15 10:30:00 - Starting DNSRebound: Domain=rebind.local, Public IP=203.0.113.1, Target IP=192.168.1.1
  2025-05-15 10:30:01 - DNS server started on port 53
  2025-05-15 10:30:01 - Web server started on port 80
  2025-05-15 10:30:02 - DNS: rebind.local -> 203.0.113.1 (Request #1)
  2025-05-15 10:30:03 - Web: Served malicious.html to 192.168.1.100
  2025-05-15 10:30:04 - DNS: rebind.local -> 192.168.1.1 (Request #2)
  2025-05-15 10:30:05 - Web: Received data from 192.168.1.100: Attempt 1: <html><title>Router Admin</title>...
  ```
- Results file example (`dnsrebound_results_20250515_103005.txt`):
  ```
  [2025-05-15 10:30:05] Data from 192.168.1.100:
  Attempt 1: <html><title>Router Admin</title>...
  --------------------------------------------------
  ```
**Tips**:
- Use a common router IP like `192.168.1.1` for testing.
- Test with a VM or device in your lab to simulate a victim.
- Ensure port 53 (DNS) and 80 (HTTP) are open (`sudo netstat -tuln`).

#### 2. Targeting a Specific Internal IP
**What It Does**: Rebind to a specific internal IP, like a router or IoT device.
**How to Use**:
1. Identify the target IP (e.g., `192.168.1.254` for a device).
2. Run:
   ```bash
   sudo python3 dnsrebound.py -i eth0 -d rebind.local -t 192.168.1.254
   ```
**What Happens**:
- The DNS server rebinds to the specified IP:
  ```
  2025-05-15 10:35:00 - Starting DNSRebound: Domain=rebind.local, Public IP=203.0.113.1, Target IP=192.168.1.254
  2025-05-15 10:35:02 - DNS: rebind.local -> 192.168.1.254 (Request #2)
  2025-05-15 10:35:03 - Web: Received data from 192.168.1.100: Attempt 1: <html><body>IoT Device</body>...
  ```
**Tips**:
- Use `nmap` or `arp -a` to find device IPs in your lab.
- Verify the target has a web interface (e.g., `curl http://192.168.1.254`).
- Modify `malicious.html` for specific payloads (e.g., fetch `/admin`).

#### 3. Quiet Mode
**What It Does**: Reduces terminal output, logging only to the file.
**How to Use**:
1. Enable quiet mode:
   ```bash
   sudo python3 dnsrebound.py -i eth0 -d rebind.local -q
   ```
**What Happens**:
- No terminal output; logs go to `dnsrebound.log`:
  ```
  $ sudo python3 dnsrebound.py -i eth0 -d rebind.local -q
  [No output]
  ```
- Log file example:
  ```
  2025-05-15 10:40:00 - Starting DNSRebound: Domain=rebind.local, Public IP=203.0.113.1, Target IP=192.168.1.1
  2025-05-15 10:40:01 - DNS: rebind.local -> 203.0.113.1 (Request #1)
  2025-05-15 10:40:02 - Web: Served malicious.html to 192.168.1.100
  ```
**Tips**:
- Check logs with `cat dnsrebound.log` or `tail -f dnsrebound.log`.
- Useful for background testing.

#### 4. Stopping the Tool
**What It Does**: Stops the servers and saves logs when done or interrupted.
**How to Use**:
1. Start the attack:
   ```bash
   sudo python3 dnsrebound.py -i eth0 -d rebind.local
   ```
2. Press `Ctrl+C` to stop.
**What Happens**:
- The tool stops, saves logs, and cleans up:
  ```
  2025-05-15 10:45:00 - Starting DNSRebound: Domain=rebind.local, Public IP=203.0.113.1, Target IP=192.168.1.1
  ^C
  2025-05-15 10:45:01 - DNSRebound stopped by user
  2025-05-15 10:45:01 - Results saved to dnsrebound_results_20250515_104501.txt
  2025-05-15 10:45:01 - Cleaned up servers
  ```
**Tips**:
- Always stop the tool to free ports.
- Results are saved even if stopped early.

### Example Workflow
To experiment with DNS rebinding in your home lab:
1. Set up a test network (e.g., a VM with `eth0` and a router at `192.168.1.1`).
2. Install dependencies:
   ```bash
   ./setup_dnsrebound.sh
   ```
3. Save and edit `malicious.html` to set `REBIND_DOMAIN` to `rebind.local`.
4. Start the attack:
   ```bash
   sudo python3 dnsrebound.py -i eth0 -d rebind.local -t 192.168.1.1 -q
   ```
5. Configure a test device (e.g., a VM) to use your machine’s IP as the DNS server.
6. Open `http://rebind.local` in a browser on the test device.
7. Review `dnsrebound.log` and `dnsrebound_results_*.txt` for request details.
8. Stop with `Ctrl+C` and delete output files securely.

## Output
- Logs are saved to `dnsrebound.log`.
- Request results are saved to `dnsrebound_results_<timestamp>.txt`.
- Example results file:
  ```
  [2025-05-15 10:30:05] Data from 192.168.1.100:
  Attempt 1: <html><title>Router Admin</title>...
  --------------------------------------------------
  [2025-05-15 10:30:06] Total DNS requests: 2
  ```

## Important Notes
- **Environment**: Use DNSRebound only on networks and devices you own or have explicit permission to test (e.g., a local VM or home router).
- **Root Privileges**: Requires `sudo` for binding to ports 53 (DNS) and 80 (HTTP).
- **No External Interaction**: The tool avoids external DNS queries to prevent misuse, as recommended for rebinding tools.
- **Browser Behavior**: Modern browsers may enforce DNS pinning or Local Network Access (e.g., Chrome’s CORS-RFC1918), which can block rebinding. Test with older browsers or disable protections in your lab for learning.[](https://www.nccgroup.com/us/research-blog/state-of-dns-rebinding-in-2023/)
- **Ethical Use**: Do not use on unauthorized networks, as DNS rebinding can bypass firewalls and access sensitive data, which is illegal without permission.[](https://github.com/nccgroup/singularity)

## Disclaimer
**Personal Use Only**: DNSRebound is for your personal learning with networks and devices you own or have explicit permission to test. Performing DNS rebinding attacks without clear authorization is illegal and could lead to legal consequences, technical issues, or unintended harm. Always ensure you have permission from the network owner before using this tool.

**Safe Use**:
- **Controlled Setup**: Use in a private lab (e.g., home network with your devices) to avoid affecting others. For example, test on `eth0` in a local VM.
- **Data Security**: Output files (`dnsrebound.log`, `dnsrebound_results_*.txt`) may contain sensitive data (e.g., HTML from internal pages). Store them securely and delete them after use (e.g., `rm dnsrebound_*.txt`).
- **Legal Compliance**: Follow all applicable laws and regulations in your area, including privacy and network security laws.
- **No Warranty**: This tool is provided “as is” for educational purposes. You are responsible for its use and any consequences.

**What to Avoid**:
- Do not use on public networks (e.g., corporate or public Wi-Fi) without permission.
- Do not share output files, as they may contain private data.
- Do not target devices without explicit authorization, as it’s illegal and disruptive.
- Avoid using real domains; use test domains like `rebind.local`.

## Limitations
- Requires a compatible network interface and root privileges.
- Limited to basic rebinding (one target IP); advanced tools like Singularity support multiple IPs or CNAMEs.[](https://github.com/nccgroup/singularity)
- Browser protections (e.g., DNS pinning, Local Network Access) may block attacks.[](https://www.nccgroup.com/us/research-blog/state-of-dns-rebinding-in-2023/)
- Sample payload is basic; custom payloads require JavaScript knowledge.
- No port scanning or automation, unlike advanced tools like ReDTunnel.[](https://portswigger.net/daily-swig/new-tool-enables-dns-rebinding-tunnel-attacks-without-reconnaissance)

## Testing Tips
- Verify interface: Use `ip link` to check `eth0` is active.
- Test DNS: Use `dig @<your_ip> rebind.local` to verify DNS responses.
- Generate traffic: Open `http://rebind.local` in a test browser.
- Monitor traffic: Use `tcpdump` (e.g., `sudo tcpdump -i eth0 port 53 or port 80`) to verify activity.
- Secure outputs: Delete files after use (`rm dnsrebound_*.txt`).
- Check logs in real-time: `tail -f dnsrebound.log`.
- Test without internet: Ensure the setup is isolated to avoid misuse.

## License
This tool is for your personal use. No formal license is provided, but please use it responsibly.