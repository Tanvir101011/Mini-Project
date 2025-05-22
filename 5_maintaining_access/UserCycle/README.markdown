# UserCycle

## Overview
UserCycle is a Python-based tool for enumerating user accounts on Windows systems using RID (Relative Identifier) cycling attacks through SMB null sessions. It mimics the functionality of `ridenum` in Kali Linux, allowing users to discover accounts by cycling through RIDs and optionally brute-forcing passwords using a provided password file.

## Features
- Enumerates the base domain SID using LSA query.
- Cycles through a specified RID range to enumerate user accounts.
- Optionally brute-forces enumerated accounts with a password file.
- Saves enumerated users to an output file if specified.
- Uses null sessions for enumeration, requiring no credentials for initial access.

## Prerequisites
- Python 3.6 or higher
- `impacket` library (install via `pip install impacket`)
- Bash (for the setup script)
- A Windows target system with SMB enabled and null sessions allowed

## Installation

### Setup
1. Clone or download the repository.
2. Run the setup script to create a virtual environment and install dependencies:
   ```bash
   chmod +x set_upfile.sh
   ./set_upfile.sh
   ```
3. Activate the virtual environment:
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows (if using a compatible shell):
     ```bash
     venv\Scripts\activate
     ```

## Usage
Run the tool with:
```bash
python usercycle.py <server_ip> <start_rid> <end_rid> [--password-file <file>] [--output <file>]
```

- **server_ip**: IP address of the target Windows system.
- **start_rid**: Starting RID (e.g., 500).
- **end_rid**: Ending RID (e.g., 50000).
- **--password-file**: Path to a file containing passwords for brute-forcing.
- **--output**: Path to save enumerated users.

### Examples
1. **Enumerate users**:
   ```bash
   python usercycle.py 192.168.1.236 500 50000
   ```
   Output:
   ```
   [*] Successfully enumerated base domain SID: S-1-5-21-...
   [*] Enumerating user accounts (RID 500 to 50000)...
   [+] RID 500: Administrator
   [+] RID 501: Guest
   ```

2. **Enumerate and save to file**:
   ```bash
   python usercycle.py 192.168.1.236 500 50000 --output users.txt
   ```

3. **Enumerate and brute-force**:
   ```bash
   python usercycle.py 192.168.1.236 500 50000 --password-file passwords.txt
   ```

## Limitations
- Requires SMB null sessions to be enabled on the target (common on older Windows systems).
- Brute-forcing is basic and stops after the first successful login for simplicity.
- May fail on modern Windows systems with tightened security policies (e.g., RestrictAnonymous=1).
- Assumes UTF-8 encoded password files.

## License
MIT License

## Warning
This tool is for ethical penetration testing and authorized security assessments only. Unauthorized use against systems you do not own or have permission to test is illegal and unethical.