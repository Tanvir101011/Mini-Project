# WiFiLure

## Description
WiFiLure is a Python tool you can use to create a fake Wi-Fi access point (AP) in your own private network to attract connecting devices and log their details. It helps you learn about Wi-Fi protocols, device behavior, and network security by acting as a honeypot, similar to wifi-honey’s functionality. Inspired by wifi-honey, WiFiLure is designed for your personal experimentation in a controlled environment, like a home lab with Wi-Fi adapters and networks you own or have permission to monitor.

**Important**: This tool is for your personal use only with networks and devices you own or have explicit permission to monitor. Creating fake Wi-Fi APs or capturing network traffic without clear authorization is illegal and could cause serious issues. The tool avoids internet connectivity to prevent misuse, ensuring it remains a safe learning tool.[](https://www.linuxjournal.com/content/wi-fi-mini-honeypot)

## Features
- Creates a fake Wi-Fi AP with a user-specified SSID (e.g., “Free_WiFi”).
- Logs client connection attempts (MAC address, timestamp, signal strength).
- Supports open (no encryption) or WPA2-encrypted APs.
- Saves logs to a text file for analysis.
- Quiet mode to reduce terminal output.
- Optional deauthentication attack to encourage clients to connect (with strong ethical warnings).
- Configurable channel and interface settings for flexibility.
- Simple design for educational use in personal projects.

## Installation
1. **What You Need**:
   - Linux OS (e.g., Ubuntu 24.04, check with `uname -a`).
   - Python 3.12 or later (check with `python3 --version`).
   - A Wi-Fi adapter supporting monitor mode and AP creation (e.g., Atheros AR9271, check with `iw list`).
   - Root/admin privileges (e.g., `sudo` on Linux).
   - A computer on a private network you control (e.g., your home lab).
2. Install dependencies:
   - Save the `setup_wifilure.sh` script to a folder (e.g., `/home/user/wifilure/`).
   - Make it executable and run it:
     ```bash
     chmod +x setup_wifilure.sh
     ./setup_wifilure.sh
     ```
   - This installs `hostapd`, `dnsmasq`, `wireless-tools`, `iw`, and `scapy`.
3. Save the `wifilure.py` script to the same folder.
4. Run the script:
   ```bash
   sudo python3 wifilure.py --help
   ```

## How to Use
WiFiLure creates a fake Wi-Fi AP to attract devices and logs their connection attempts (probe and association requests). You specify the interface, SSID, and optional settings like encryption or deauthentication. Below is a guide on how to use each feature with examples and expected results.

### Basic Usage
Create a fake open AP:
```bash
sudo python3 wifilure.py -i wlan0 -s Free_WiFi
```

Create a WPA2-encrypted AP:
```bash
sudo python3 wifilure.py -i wlan0 -s Secure_WiFi -e wpa2 -p mypassword123
```

### Options
- `-i, --interface`: Wi-Fi interface (e.g., `wlan0`, required).
- `-s, --ssid`: SSID for the fake AP (e.g., `Free_WiFi`, required).
- `-c, --channel`: Channel for the AP (e.g., `6`, default: 6).
- `-e, --encryption`: Encryption type (`wpa2`).
- `-p, --password`: Password for WPA2 (required if encryption is `wpa2`).
- `-d, --deauth`: Enable deauthentication attack (use ethically).
- `-t, --deauth-target`: Target BSSID for deauthentication (required if `-d` is used).
- `-q, --quiet`: Run quietly (logs to file only).

### Using Each Feature

#### 1. Creating an Open AP
**What It Does**: Sets up a fake AP with no encryption to attract devices.
**How to Use**:
1. Find your Wi-Fi interface (e.g., `iw dev`).
2. Run:
   ```bash
   sudo python3 wifilure.py -i wlan0 -s Free_WiFi -c 6
   ```
**What Happens**:
- The AP starts, and client connections are logged:
  ```
  2025-05-15 10:30:00 - Starting WiFiLure: SSID=Free_WiFi, Interface=wlan0, Channel=6
  2025-05-15 10:30:01 - Interface wlan0 configured for channel 6
  2025-05-15 10:30:02 - Started fake AP: SSID=Free_WiFi, Channel=6
  2025-05-15 10:30:03 - Probe: MAC=00:11:22:33:44:55, SSID=Free_WiFi, Signal=-60dBm
  2025-05-15 10:30:04 - Association: MAC=00:11:22:33:44:55, SSID=Free_WiFi, Signal=-58dBm
  ```
- Results file example (`wifilure_results_20250515_103004.txt`):
  ```
  [2025-05-15 10:30:03] Probe
  MAC: 00:11:22:33:44:55
  SSID: Free_WiFi
  Signal: -60dBm
  --------------------------------------------------
  ```
**Tips**:
- Use an enticing SSID (e.g., “Free_WiFi”) but avoid common defaults like “linksys” to prevent confusion.[](https://security.stackexchange.com/questions/137777/would-i-create-a-wifi-honeypot-by-setting-up-a-fake-network-with-a-generic-name)
- Test with a phone or laptop in your lab to see connection attempts.
- Check adapter compatibility with `iw list`.

#### 2. Creating a WPA2-Encrypted AP
**What It Does**: Sets up a fake AP with WPA2 encryption to mimic secure networks.
**How to Use**:
1. Run with encryption and password:
   ```bash
   sudo python3 wifilure.py -i wlan0 -s Secure_WiFi -e wpa2 -p mypassword123
   ```
**What Happens**:
- The AP requires a password, and connections are logged:
  ```
  2025-05-15 10:35:00 - Starting WiFiLure: SSID=Secure_WiFi, Interface=wlan0, Channel=6
  2025-05-15 10:35:02 - Started fake AP: SSID=Secure_WiFi, Channel=6
  2025-05-15 10:35:03 - Association: MAC=00:11:22:33:44:55, SSID=Secure_WiFi, Signal=-62dBm
  ```
**Tips**:
- Use a strong password to simulate real networks.
- Verify clients attempt to connect with the correct password.
- Avoid WEP, as it’s outdated and less secure.[](https://www.linuxjournal.com/content/wi-fi-mini-honeypot)

#### 3. Using Deauthentication (Ethical Use Only)
**What It Does**: Sends deauthentication packets to force devices off a target AP, encouraging them to connect to your fake AP.
**How to Use**:
1. Find the target AP’s BSSID (e.g., using `airodump-ng wlan0`).
2. Run with deauth enabled:
   ```bash
   sudo python3 wifilure.py -i wlan0 -s Free_WiFi -d -t 00:11:22:33:44:66
   ```
**What Happens**:
- Deauth packets are sent, and connections to the fake AP are logged:
  ```
  2025-05-15 10:40:00 - Starting WiFiLure: SSID=Free_WiFi, Interface=wlan0, Channel=6
  2025-05-15 10:40:01 - Starting deauthentication attack on BSSID 00:11:22:33:44:66
  2025-05-15 10:40:02 - Association: MAC=00:11:22:33:44:55, SSID=Free_WiFi, Signal=-59dBm
  ```
**Tips**:
- **Ethical Warning**: Only use deauthentication on APs you own or have explicit permission to test. Unauthorized deauthentication is illegal and disruptive.[](https://www.infosecinstitute.com/resources/hacking/hotspot-honeypot/)
- Use `airodump-ng` to find BSSIDs in your lab.
- Test with a second device to verify deauth effectiveness.

#### 4. Quiet Mode
**What It Does**: Reduces terminal output, logging only to the file.
**How to Use**:
1. Enable quiet mode:
   ```bash
   sudo python3 wifilure.py -i wlan0 -s Free_WiFi -q
   ```
**What Happens**:
- No terminal output; logs go to `wifilure.log`:
  ```
  $ sudo python3 wifilure.py -i wlan0 -s Free_WiFi -q
  [No output]
  ```
- Log file example:
  ```
  2025-05-15 10:45:00 - Starting WiFiLure: SSID=Free_WiFi, Interface=wlan0, Channel=6
  2025-05-15 10:45:02 - Probe: MAC=00:11:22:33:44:55, SSID=Free_WiFi, Signal=-60dBm
  ```
**Tips**:
- Check logs with `cat wifilure.log` or `tail -f wifilure.log`.
- Useful for background operation.

#### 5. Stopping the Tool
**What It Does**: Stops the fake AP and saves logs when done or interrupted.
**How to Use**:
1. Start the AP:
   ```bash
   sudo python3 wifilure.py -i wlan0 -s Free_WiFi
   ```
2. Press `Ctrl+C` to stop.
**What Happens**:
- The tool stops, saves logs, and cleans up:
  ```
  2025-05-15 10:50:00 - Starting WiFiLure: SSID=Free_WiFi, Interface=wlan0, Channel=6
  ^C
  2025-05-15 10:50:01 - WiFiLure stopped by user
  2025-05-15 10:50:01 - Results saved to wifilure_results_20250515_105001.txt
  2025-05-15 10:50:01 - Cleaned up processes and configurations
  ```
**Tips**:
- Always stop the tool to free resources.
- Results are saved even if stopped early.

### Example Workflow
To experiment with Wi-Fi in your home lab:
1. Set up a test network (e.g., a VM with a Wi-Fi adapter on `wlan0`).
2. Install dependencies:
   ```bash
   ./setup_wifilure.sh
   ```
3. Create a fake AP:
   ```bash
   sudo python3 wifilure.py -i wlan0 -s Free_WiFi -c 6 -q
   ```
4. Use a phone or laptop to connect to “Free_WiFi” and generate traffic.
5. Optionally, perform a deauth attack on a test AP you own:
   ```bash
   sudo python3 wifilure.py -i wlan0 -s Free_WiFi -d -t 00:11:22:33:44:66
   ```
6. Review `wifilure.log` and `wifilure_results_*.txt` for connection details.
7. Stop with `Ctrl+C` and delete output files securely.

## Output
- Logs are saved to `wifilure.log`.
- Connection results are saved to `wifilure_results_<timestamp>.txt`.
- Example results file:
  ```
  [2025-05-15 10:30:03] Probe
  MAC: 00:11:22:33:44:55
  SSID: Free_WiFi
  Signal: -60dBm
  --------------------------------------------------
  [2025-05-15 10:30:04] Association
  MAC: 00:11:22:33:44:55
  SSID: Free_WiFi
  Signal: -58dBm
  --------------------------------------------------
  ```

## Important Notes
- **Environment**: Use WiFiLure only on networks and devices you own or have explicit permission to monitor (e.g., a local VM or home router).[](https://dev.to/s3cloudhub/honeypot-in-cybersecurity-creating-a-fake-access-point-honeypot-3p15)
- **Root Privileges**: Requires `sudo` for interface configuration and packet sniffing.
- **No Internet**: The tool avoids providing internet access to clients to prevent misuse, as recommended for honeypots.[](https://www.linuxjournal.com/content/wi-fi-mini-honeypot)
- **Adapter Compatibility**: Ensure your Wi-Fi adapter supports monitor mode and AP creation (check with `iw list`).
- **Ethical Use**: Deauthentication is included for learning but must only be used on APs you own or have permission to test. Unauthorized use is illegal.[](https://www.infosecinstitute.com/resources/hacking/hotspot-honeypot/)

## Disclaimer
**Personal Use Only**: WiFiLure is for your personal learning with networks and devices you own or have explicit permission to monitor. Creating fake Wi-Fi APs or capturing network traffic without clear authorization is illegal and could lead to legal consequences, technical issues, or unintended harm. Always ensure you have permission from the network owner before using this tool.[](https://dev.to/s3cloudhub/honeypot-in-cybersecurity-creating-a-fake-access-point-honeypot-3p15)

**Safe Use**:
- **Controlled Setup**: Use in a private lab (e.g., home network with your devices) to avoid affecting others. For example, test on `wlan0` in a local VM.
- **Data Security**: Output files (`wifilure.log`, `wifilure_results_*.txt`) may contain sensitive data (e.g., MAC addresses). Store them securely and delete them after use (e.g., `rm wifilure_*.txt`).[](https://ransomware.org/how-to-prevent-ransomware/threat-hunting/honeypots-and-honeyfiles/)
- **Legal Compliance**: Follow all applicable laws and regulations in your area, including privacy and wireless communication laws.[](https://www.throttlenet.com/blog/cybersecurity/wi-fi-honey-pot/)
- **No Warranty**: This tool is provided “as is” for educational purposes. You are responsible for its use and any consequences.

**What to Avoid**:
- Do not use on public networks (e.g., coffee shop Wi-Fi) without permission.[](https://hackernoon.com/the-security-issues-in-using-public-wi-fi-honeypots-and-pineapples-okt3u5z)
- Do not share output files, as they may contain private data.
- Do not use deauthentication on unauthorized networks, as it’s disruptive and illegal.[](https://www.infosecinstitute.com/resources/hacking/hotspot-honeypot/)
- Avoid default SSIDs like “linksys” or “netgear” to prevent accidental connections by legitimate users.[](https://security.stackexchange.com/questions/137777/would-i-create-a-wifi-honeypot-by-setting-up-a-fake-network-with-a-generic-name)

## Limitations
- Requires a compatible Wi-Fi adapter (monitor mode and AP support).
- Limited to basic logging (MAC, SSID, signal); advanced analysis requires tools like Wireshark.
- Deauthentication is basic and may not work on all devices.
- No internet connectivity for clients to ensure ethical use.
- May fail if NetworkManager interferes or the adapter doesn’t support required modes.

## Testing Tips
- Verify adapter: Use `iw list` to check for “AP” and “monitor” modes.
- Find BSSIDs: Use `airodump-ng wlan0` to identify target APs in your lab.
- Generate traffic: Connect a test device (e.g., phone) to the fake AP.
- Monitor traffic: Use `tcpdump` (e.g., `sudo tcpdump -i wlan0`) to verify activity.
- Secure outputs: Delete files after use (`rm wifilure_*.txt`).
- Check logs in real-time: `tail -f wifilure.log`.
- Test without internet: Ensure the AP is isolated to avoid misuse.[](https://www.linuxjournal.com/content/wi-fi-mini-honeypot)

## Troubleshooting
- **Interface not found**: Verify the interface with `iw dev` and ensure it’s up (`sudo ifconfig wlan0 up`).
- **hostapd fails**: Check adapter compatibility (`iw list`) and ensure no conflicting services (e.g., `sudo systemctl stop NetworkManager`).
- **No clients connect**: Use an enticing SSID and test with a device in range; consider deauth if ethical.
- **Scapy errors**: Ensure Scapy is installed (`pip install scapy`) and run with `sudo`.
- **Deauth not working**: Verify the target BSSID and ensure the adapter supports packet injection.

## License
This tool is for your personal use. No formal license is provided, but please use it responsibly.