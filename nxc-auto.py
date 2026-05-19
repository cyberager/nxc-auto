#!/usr/bin/env python3
import sys
import os
import subprocess

# ANSI Escape Codes for Terminal Colors
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def run_nxc_blast(targets_file, creds_file, protocols):
    # Validate that files exist
    if not os.path.exists(targets_file):
        print(f"{RED}[-]{RESET} Error: Targets file '{targets_file}' not found.")
        return
    if not os.path.exists(creds_file):
        print(f"{RED}[-]{RESET} Error: Credentials file '{creds_file}' not found.")
        return

    print(f"{BOLD}{CYAN}[*] Starting Python NXC Automator...{RESET}")
    print(f"{CYAN}--------------------------------------------------{RESET}")

    # Loop through each protocol specified
    for proto in protocols:
        proto = proto.strip().lower()
        print(f"\n{BOLD}{BLUE}[+] Testing Protocol: {proto.upper()}{RESET}")
        print(f"{BLUE}--------------------------------------------------{RESET}")

        # Open and read the credentials file
        with open(creds_file, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines or comments
                if not line or line.startswith('#'):
                    continue

                # Split the line by whitespace into username and password
                parts = line.split(maxsplit=1)
                if len(parts) < 2:
                    print(f"{YELLOW}[!]{RESET} Skipping invalid credential line: '{line}'")
                    continue

                username, password = parts[0], parts[1]
                print(f"{YELLOW}[~] Testing:{RESET} {BOLD}{username}{RESET} : {BOLD}{password}{RESET}")

                # Construct the NetExec command
                cmd = [
                    "nxc", proto, targets_file,
                    "-u", username,
                    "-p", password,
                    "--continue-on-success"
                ]

                try:
                    # Run the command and let it print directly to the terminal
                    # NetExec inherently preserves its own colors when run this way
                    subprocess.run(cmd, check=False)
                except FileNotFoundError:
                    print(f"{RED}[-]{RESET} Error: 'nxc' (NetExec) command not found.")
                    sys.exit(1)
                except KeyboardInterrupt:
                    print(f"\n{YELLOW}[!]{RESET} Script terminated by user.")
                    sys.exit(0)

    print(f"\n{CYAN}--------------------------------------------------{RESET}")
    print(f"{BOLD}{GREEN}[+] Automation complete!{RESET}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"{BOLD}Usage:{RESET} python3 nxc_blast_color.py <targets.txt> <creds.txt> <protocols_comma_separated>")
        print("Example: python3 nxc_blast_color.py targets.txt creds.txt smb,ssh")
        sys.exit(1)

    t_file = sys.argv[1]
    c_file = sys.argv[2]
    proto_list = sys.argv[3].split(",")

    run_nxc_blast(t_file, c_file, proto_list)
