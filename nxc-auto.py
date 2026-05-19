#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess

GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def main():
    parser = argparse.ArgumentParser(
        description="Advanced Colorized NetExec (NXC) Automation Wrapper for CTFs",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("-t", "--targets", required=True, help="Path to targets.txt (IPs, ranges, or domains)")
    parser.add_argument("-c", "--creds", required=True, help="Path to creds.txt (Format: 'user pass' per line)")
    parser.add_argument("-p", "--protocols", required=True, help="Comma-separated protocols (e.g., smb,ssh,ldap)")
    parser.add_argument("--threads", type=int, default=10, help="Number of concurrent NXC threads (Default: 10)")
    parser.add_argument("--jitter", type=str, help="Random delay interval between connections (e.g., '2-5' or '3')")
    parser.add_argument("--timeout", type=int, help="Max timeout in seconds for each thread")
    parser.add_argument("--port", type=int, help="Force a non-default custom port for the protocols")
    parser.add_argument("-k", "--kerberos", action="store_true", help="Use Kerberos authentication instead of NTLM")
    parser.add_argument("--kdc", help="KDC IP or Hostname (Required if using --kerberos)")
    parser.add_argument("-d", "--domain", help="Domain name to append for authentication context")
    args = parser.parse_args()

    if not os.path.exists(args.targets):
        print(f"{RED}[-]{RESET} Error: Targets file '{args.targets}' not found.")
        sys.exit(1)
    if not os.path.exists(args.creds):
        print(f"{RED}[-]{RESET} Error: Credentials file '{args.creds}' not found.")
        sys.exit(1)

    protocols_list = [p.strip().lower() for p in args.protocols.split(",")]

    print(f"{BOLD}{CYAN}[*] Initializing Advanced NXC Automation Run...{RESET}")
    print(f"{CYAN}------------------------------------------------------------{RESET}")

    for proto in protocols_list:
        print(f"\n{BOLD}{BLUE}[+] Activating Protocol: {proto.upper()}{RESET}")
        print(f"{BLUE}------------------------------------------------------------{RESET}")

        with open(args.creds, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                parts = line.split(maxsplit=1)
                if len(parts) < 2:
                    print(f"{YELLOW}[!]{RESET} Skipping invalid credential line: '{line}'")
                    continue

                username, password = parts[0], parts[1]
                print(f"{YELLOW}[~] Queueing Base Auth:{RESET} {BOLD}{username}{RESET} : {BOLD}{password}{RESET}")

                cmd = ["nxc", proto, args.targets, "-t", str(args.threads)]
                
                if args.jitter:
                    cmd.extend(["--jitter", args.jitter])
                if args.timeout:
                    cmd.extend(["--timeout", str(args.timeout)])
                
                cmd.extend(["-u", username, "-p", password])
                
                if args.domain:
                    cmd.extend(["-d", args.domain])

                if args.port:
                    cmd.extend(["--port", str(args.port)])
                elif proto == "ldap" and args.port == 636:
                    cmd.extend(["--simple-bind"])

                if args.kerberos:
                    cmd.append("-k")
                    if args.kdc:
                        cmd.extend(["--kdcHost", args.kdc])
                    else:
                        print(f"{RED}[-]{RESET} Warning: Kerberos enabled (-k) but --kdc host wasn't provided.")

                cmd.append("--continue-on-success")

                try:
                    subprocess.run(cmd, check=False)
                except FileNotFoundError:
                    print(f"{RED}[-]{RESET} Critical Error: 'nxc' command execution failed. Ensure NetExec is installed.")
                    sys.exit(1)
                except KeyboardInterrupt:
                    print(f"\n{RED}[!] Operational run paused by user interrupt.{RESET}")
                    sys.exit(0)

    print(f"\n{CYAN}------------------------------------------------------------{RESET}")
    print(f"{BOLD}{GREEN}[+] Finished checking all specified matrices!{RESET}")

if __name__ == "__main__":
    main()
