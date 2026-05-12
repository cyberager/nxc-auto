import subprocess
import argparse
import concurrent.futures
import sys
import os
import ipaddress

def parse_targets(target_input):
    """
    Parses a single IP, a CIDR subnet, a hostname, or a file.
    Returns a list of target strings.
    """
    targets = []
    
    if os.path.isfile(target_input):
        with open(target_input, 'r') as f:
            for line in f:
                clean_line = line.strip()
                if clean_line:
                    targets.append(clean_line)
        return targets

    try:
        net = ipaddress.ip_network(target_input, strict=False)
        
        if net.num_addresses == 1:
            targets.append(str(net.network_address))
        else:
            for ip in net.hosts():
                targets.append(str(ip))
        return targets
        
    except ValueError:
        targets.append(target_input)
        return targets

def run_nxc(target, protocol, user_arg, pass_arg, use_kerberos=False):
    """
    Executes the NXC command for a single target.
    """
    command = ["nxc", protocol, target, "-u", user_arg, "-p", pass_arg]
    
    auth_type = "NTLM"
    if use_kerberos:
        command.append("-k")
        auth_type = "KERBEROS"

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        return target, protocol, auth_type, result.stdout
        
    except subprocess.TimeoutExpired:
        return target, protocol, auth_type, "[!] Scan timeout."
    except Exception as e:
        return target, protocol, auth_type, f"[!] Error: {e}"

def main():
    parser = argparse.ArgumentParser(description="Automated NXC (NetExec) Wrapper")
    parser.add_argument("-t", "--target", required=True, help="Target IP, CIDR (e.g., 10.0.0.0/24), hostname, or file")
    parser.add_argument("-u", "--user", required=True, help="Username or users file")
    parser.add_argument("-p", "--password", required=True, help="Password or passwords file")
    parser.add_argument("--protocols", nargs='+', default=["smb"], help="List of protocols (e.g., smb ssh winrm)")
    parser.add_argument("--threads", type=int, default=10, help="Number of concurrent threads")
    parser.add_argument("-k", "--kerberos", action="store_true", help="Use Kerberos authentication (-k)")
    parser.add_argument("-a", "--auto-auth", action="store_true", help="Test both NTLM and Kerberos automatically")
    
    args = parser.parse_args()
    target_list = parse_targets(args.target)
    
    if not target_list:
        print("[-] No valid targets found. Exiting.")
        sys.exit(1)

    print(f"[*] Loaded {len(target_list)} target(s).")

    tasks = []
    for target in target_list:
        for proto in args.protocols:
            if args.auto_auth:
                tasks.append((target, proto, args.user, args.password, False)) # NTLM
                tasks.append((target, proto, args.user, args.password, True))  # Kerberos
            else:
                tasks.append((target, proto, args.user, args.password, args.kerberos))

    total_tasks = len(tasks)
    print(f"[*] Starting scan | Threads: {args.threads} | Total Tasks: {total_tasks}")
    print("-" * 50)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(run_nxc, t[0], t[1], t[2], t[3], t[4]): t for t in tasks}
        
        for future in concurrent.futures.as_completed(futures):
            target, protocol, auth_type, output = future.result()
            
            # Print logic: Only show blocks where we actually found something
            interesting_lines = [line.strip() for line in output.split('\n') if "[+]" in line or "Pwn3d!" in line]
            
            if interesting_lines:
                print(f"\n--- [ {target} | {protocol.upper()} | {auth_type} ] ---")
                for line in interesting_lines:
                    print(line)

if __name__ == "__main__":
    main()
