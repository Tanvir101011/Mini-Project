# NetSentry

## Description
NetSentry is a Python tool you can use to explore how networks handle TCP and UDP ports. It sends packets through a gateway (like a router) to a target device to see which ports are allowed or blocked, helping you learn about network behavior in your own private setup. Inspired by tools that probe network rules, NetSentry is built for your personal experimentation in a controlled environment, such as a home lab.

**Important**: This tool is for your personal use only in environments you own or have permission to test. Using it on networks or devices without clear authorization is illegal and could cause problems.

## Features
- Probes specific TCP or UDP ports to check if they pass through a gateway.
- Supports port ranges (e.g., `80-85`) or lists (e.g., `80,443`).
- Allows setting the TTL (Time to Live) for packets.
- Saves results to a text file for easy review.
- Quiet mode to reduce terminal output.
- Simple, single-threaded design for straightforward use.
- Logs all probe attempts to a file (`netsentry.log`).

## Installation
1. **What You Need**:
   - Python 3.12 or later (check with `python3 --version`).
   - Scapy library for packet crafting.
   - A computer with a network you control (e.g., your home network).
   - Administrator access (e.g., `sudo`) for sending network packets.
2. Install Scapy:
   ```bash
   pip3 install scapy
   ```
3. Save the `netsentry.py` script to a folder (e.g., `/home/user/netsentry/`).
4. Run the script with administrator privileges:
   ```bash
   sudo python3 netsentry.py --help
   ```

## How to Use
NetSentry needs a gateway IP (e.g., your router), a target IP (e.g., a device behind the router), and a list or range of ports to check. Below is a guide on how to use each feature with examples and what to expect.

### Basic Usage
Check if ports 80-85 (TCP) are allowed through your gateway (`192.168.1.1`) to a target (`192.168.0.10`):
```bash
sudo python3 netsentry.py -p 80-85 -P TCP 192.168.1.1 192.168.0.10
```

### Options
- `gateway`: The IP of the gateway (e.g., your router).
- `target`: The IP of the device you’re probing.
- `-p, --ports`: Ports to check (e.g., `80-85` or `80,443`).
- `-P, --protocol`: Protocol to use (`TCP` or `UDP`, default: `TCP`).
- `-t, --ttl`: Packet TTL (default: `64`).
- `-q, --quiet`: Run quietly (logs to file only).

### Using Each Feature

#### 1. Probing Ports and Protocols
**What It Does**: Sends TCP or UDP packets to see if ports are allowed through the gateway.
**How to Use**:
1. Run a TCP probe for ports 80-85:
   ```bash
   sudo python3 netsentry.py -p 80-85 -P TCP 192.168.1.1 192.168.0.10
   ```
2. The tool sends packets and checks responses.
**What Happens**:
- Results are shown in the terminal and saved to `netsentry.log` and a text file:
  ```
  2025-05-15 09:53:00 - Starting NetSentry: Gateway=192.168.1.1, Target=192.168.0.10, Ports=[80, 81, 82, 83, 84, 85]
  2025-05-15 09:53:01 - Port 80/TCP: allowed (gateway_passed)
  2025-05-15 09:53:03 - Port 81/TCP: blocked (no_response)
  2025-05-15 09:53:10 - Results saved to netsentry_results_20250515_095310.txt
  ```
- Text file example:
  ```
  Port 80/TCP: allowed (gateway_passed)
  Port 81/TCP: blocked (no_response)
  ```
**Tips**:
- Try UDP with `-P UDP` to test different protocols.
- Check if the gateway and target are reachable first (e.g., `ping 192.168.1.1`).

#### 2. Choosing Ports
**What It Does**: Lets you pick a range of ports or specific ports to probe.
**How to Use**:
1. Probe a range:
   ```bash
   sudo python3 netsentry.py -p 80-85 -P TCP 192.168.1.1 192.168.0.10
   ```
2. Probe specific ports:
   ```bash
   sudo python3 netsentry.py -p 80,443,8080 -P TCP 192.168.1.1 192.168.0.10
   ```
**What Happens**:
- Logs and text file show results for each port:
  ```
  2025-05-15 09:55:00 - Port 80/TCP: allowed (gateway_passed)
  2025-05-15 09:55:02 - Port 443/TCP: blocked (no_response)
  ```
**Tips**:
- Use commas for separate ports (e.g., `80,443`).
- Keep ranges small to avoid slowing down your network.

#### 3. Setting TTL
**What It Does**: Controls how far packets travel before expiring.
**How to Use**:
1. Set a custom TTL:
   ```bash
   sudo python3 netsentry.py -p 80 -P TCP -t 10 192.168.1.1 192.168.0.10
   ```
**What不需要提供翻译，直接提供英文原文即可。