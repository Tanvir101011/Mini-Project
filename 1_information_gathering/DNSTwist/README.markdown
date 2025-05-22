# DNSTwist

**DNSTwist** is a private Python command-line tool that operates as a configurable DNS proxy, designed for network testing, penetration testing, and malware analysis. It intercepts DNS queries, forging responses for specified or wildcard domains (e.g., redirecting `example.com` or `*.example.com` to a fake IP) while proxying other queries to upstream DNS servers (e.g., 8.8.8.8). Built with the `dnslib` library, it supports A and AAAA records and runs as a UDP or TCP DNS server. DNSTwist is for controlled, authorized environments only.

> ⚠️ **For private, authorized use only. Do not share or distribute.**

## Description

DNSTwist functions as a DNS proxy, manipulating DNS responses for targeted domains while forwarding unmatched queries to real DNS servers. It operates at the **Application Layer** (Layer 7), processing DNS queries and crafting custom responses. Users can specify domains (including wildcards like `*.example.com`) to spoof and corresponding fake IPs via command-line arguments, with verbose logging for debugging. The tool is ideal for simulating DNS-based attacks, testing network configurations, or analyzing traffic in a lab setting.

Currently supports:
- Forging A and AAAA DNS records
- Wildcard domain matching (e.g., `*.example.com`)
- UDP and TCP DNS protocols
- Configurable upstream DNS servers

> Future extensibility: Support for MX, CNAME, advanced logging, and response caching.

## Features

### ✅ Forge DNS Responses
- Returns fake IPs for specified or wildcard domains (e.g., `sub.example.com` → `192.168.1.100`).
- Supports A (IPv4) and AAAA (IPv6) records.
- Simulates malicious DNS servers or tests client behavior.

### ✅ Wildcard Domain Support
- Matches subdomains with wildcards (e.g., `*.example.com` covers `sub1.example.com`).
- Simplifies spoofing for multiple subdomains.

### ✅ Proxy Real DNS Queries
- Forwards unmatched queries to upstream servers (e.g., 8.8.8.8).
- Ensures legitimate responses for non-fake domains.
- Configurable upstream server list.

### ✅ UDP and TCP Support
- Runs as a DNS server on UDP (default) or TCP.
- Default port 53 (requires root); customizable ports for testing.

### ✅ Command-Line Interface
- Intuitive arguments for fake IPs, domains, interface, and port.
- Integrates with testing scripts or workflows.

### ✅ Verbose Logging
- Logs query details (domain, type, client IP) and response actions.
- Aids debugging and traffic analysis.

### ✅ Protocol Handling
- Processes DNS queries for A and AAAA records.
- Safely ignores unsupported record types.

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

### 📦 dnslib Library
- Needed for DNS parsing and response crafting.
- Install:
  ```bash
  pip install dnslib
  ```
- Verify:
  ```bash
  python3 -c "import dnslib; print(dnslib.__version__)"
  ```
- Use `--user` for permission issues:
  ```bash
  pip install dnslib --user
  ```

### 💻 Operating System
- Runs on Linux, macOS, or Windows with Python and dnslib.
- Linux preferred for network testing (e.g., port 53 access).

### 🔍 Optional Testing Tools
- `dig` for sending DNS queries:
  ```bash
  sudo apt install dnsutils  # Ubuntu
  brew install bind          # macOS
  ```
- Wireshark for capturing DNS traffic ([wireshark.org](https://www.wireshark.org/)).
- `tcpdump` for command-line packet analysis:
  ```bash
  sudo apt install tcpdump  # Ubuntu
  brew install tcpdump      # macOS
  ```

---

## Installation

### 📥 Save the Script
- Store `dnstwist.py` in a private directory:
  ```bash
  mkdir ~/dnstwist
  mv dnstwist.py ~/dnstwist/
  cd ~/dnstwist
  ```
- Keep confidential; avoid public storage.

### 📦 Install dnslib
- Install dnslib via pip:
  ```bash
  pip install dnslib
  ```
- Confirm:
  ```bash
  python3 -c "import dnslib; print(dnslib.__version__)"
  ```
- If you encountered `ModuleNotFoundError`, use:
  ```bash
  sudo pip install dnslib
  ```
  Or, for user-only:
  ```bash
  pip install dnslib --user
  ```

### 🔧 Make Executable (Optional)
- On Linux/macOS:
  ```bash
  chmod +x dnstwist.py
  ```
- Run as `./dnstwist.py` (else use `python3 dnstwist.py`).

### ✅ Verify Setup
- Ensure Python, dnslib, and permissions are correct.
- Test with a command from Examples.

---

## Examples

### 🛠️ Forge DNS Responses for Specific Domains
  ```bash
  sudo ./dnstwist.py --fakeip 192.168.1.100 --fakedomains example.com,test.com --verbose
  ```
- Redirects `example.com` and `test.com` to `192.168.1.100` (A records).
- Proxies other queries to 8.8.8.8.
- Use for testing client behavior; requires root for port 53.

### 🛠️ Forge Responses for Wildcard Domains
  ```bash
  sudo ./dnstwist.py --fakeip 192.168.1.100 --fakedomains *.example.com --verbose
  ```
- Spoofs all subdomains (e.g., `sub1.example.com`, `sub2.example.com`) to `192.168.1.100`.
- Proxies unmatched queries.

### 🛠️ Run on Non-Privileged Port
  ```bash
  ./dnstwist.py --port 5353 --fakeip 192.168.1.100 --fakedomains example.com --verbose
  ```
- Uses port 5353 (no root needed).
- Spoofs `example.com` responses; proxies others.

### 🛠️ Use TCP and Custom Upstream
  ```bash
  sudo ./dnstwist.py --tcp --fakeip 2001:db8::1 --fakedomains *.test.com --nameservers 1.1.1.1 --verbose
  ```
- Runs over TCP, spoofs `*.test.com` to `2001:db8::1` (AAAA records).
- Proxies to 1.1.1.1.

### 🛠️ Proxy All Queries
  ```bash
  sudo ./dnstwist.py
  ```
- Forwards all DNS queries to 8.8.8.8 without forging.
- Tests proxy functionality.

---

## Expected Output

### 🖥️ Console Output
- **Startup**:
  ```
  [09:10:00] 🚀 Starting DNSTwist on 127.0.0.1:53 (UDP)
  [09:10:00] 📍 Fake domains: example.com,*.test.com -> 192.168.1.100
  [09:10:00] 🌐 Upstream: 8.8.8.8
  ```
  Shows server status and configuration.
- **Verbose Mode**:
  - Logs queries and responses:
    ```
    [09:10:05] 📥 Query: sub1.example.com (A) from 127.0.0.1
    [09:10:05] ✅ Forged response for sub1.example.com: 192.168.1.100
    [09:10:10] 📥 Query: google.com (A) from 127.0.0.1
    [09:10:10] 🔄 Proxied response for google.com
    ```
- **Errors**:
  - Permission issue:
    ```
    [09:10:00] ⚠️ Port 53 requires root privileges. Run with sudo or use --port
    ```
  - Invalid arguments:
    ```
    [09:10:00] ⚠️ --fakeip requires --fakedomains to specify target domains
    ```

### 📄 DNS Responses
- Fake domains return specified IP (e.g., `dig sub1.example.com` returns `192.168.1.100`).
- Other domains return real responses from upstream server.
- Test with:
  ```bash
  dig @127.0.0.1 sub1.example.com
  dig @127.0.0.1 google.com
  ```

### 🔍 Verification
- Capture traffic with Wireshark or:
  ```bash
  sudo tcpdump -i lo port 53
  ```
  Confirm fake IPs for specified/wildcard domains.
- Check logs for query/response details.
- Compare `dig` outputs for fake vs. real domains.

### 📝 Notes
- Port 53 requires `sudo`; use `--port 5353` for testing.
- Large query volumes may increase latency.
- Unsupported record types (e.g., MX) are ignored.

---

## Disclaimer

> ⚠️ **DNSTwist is for private, authorized use only.** Do not share or use on networks/systems without explicit permission. Unauthorized use, such as DNS spoofing on production networks, may violate laws or policies (e.g., computer misuse, data protection). Users must ensure compliance and verify responses to prevent network disruptions. Provided as-is, with no warranties.