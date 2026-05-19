#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess

# ANSI Colors
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def load_targets(target_input):
    """Detects if input is a file or a single target string."""
    if os.path.isfile(target_input):
        with open(target_input, 'r') as f:
            return target_input
    else:
        return target_input

def load_credentials(cred_input):
    """Parses input into a list of (username, password) tuples."""
    creds = []
    if os.path.isfile(cred_input):
        with open(cred_input, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    creds.append((parts[0], parts[1]))
    else:
        # It's a single credential string. Expecting "user pass"
        parts = cred_input.strip().split(maxsplit=1)
        if len(parts) == 2:
            creds.append((parts[0], parts[1]))
        else:
            print(f"{RED}[-]{RESET} Error: Single credential must be in \"user pass\" format.")
            sys.exit(1)
    return creds

def main():
    parser = argparse.ArgumentParser(
        description="Flexible NetExec (NXC) Automation Wrapper for CTFs",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("-t", "--target", required=True, 
                        help="Path to targets.txt OR a single target string (IP/CIDR/Domain)")
    parser.add_argument("-c", "--cred", required=True, 
                        help="Path to creds.txt OR a single 'user pass' string")
    parser.add_argument("-p", "--protocols", required=True, 
                        help="Comma-separated protocols (e.g., smb,ssh,ldap)")
    
    parser.add_argument("--threads", type=int, default=10, help="Number of concurrent NXC threads (Default: 10)")
    parser.add_argument("--port", type=int, help="Force a non-default custom port")
    parser.add_argument("-d", "--domain", help="Domain name to append for authentication context")

    args = parser.parse_args()

    target_payload = load_targets(args.target)
    credentials_list = load_credentials(args.cred)
    protocols_list = [p.strip().lower() for p in args.protocols.split(",")]

    print(f"{BOLD}{CYAN}[*] Initializing Flexible NXC Automation Run...{RESET}")
    print(f"{CYAN}------------------------------------------------------------{RESET}")

    for proto in protocols_list:
        print(f"\n{BOLD}{BLUE}[+] Activating Protocol: {proto.upper()}{RESET}")
        print(f"{BLUE}------------------------------------------------------------{RESET}")

        for username, password in credentials_list:
            print(f"{YELLOW}[~] Queueing Target Auth:{RESET} {BOLD}{username}{RESET} : {BOLD}{password}{RESET}")

            cmd = ["nxc", proto, target_payload, "-t", str(args.threads)]
            cmd.extend(["-u", username, "-p", password])
            
            if args.domain:
                cmd.extend(["-d", args.domain])
            if args.port:
                cmd.extend(["--port", str(args.port)])

            cmd.append("--continue-on-success")

            try:
                subprocess.run(cmd, check=False)
            except FileNotFoundError:
                print(f"{RED}[-]{RESET} Critical Error: 'nxc' command execution failed.")
                sys.exit(1)
            except KeyboardInterrupt:
                print(f"\n{RED}[!] Operational run paused by user interrupt.{RESET}")
                sys.exit(0)

    print(f"\n{CYAN}------------------------------------------------------------{RESET}")
    print(f"{BOLD}{GREEN}[+] Finished testing target matrix!{RESET}")

if __name__ == "__main__":
    main()
