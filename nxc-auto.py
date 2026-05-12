import subprocess
import argparse
import concurrent.futures
import sys 

def run_nxc(target, protocol, user_arg, pass_arg, use_kerberos=False):
    """
    Launch nxc command
    """
    command = ["nxc", protocol, target]
    command.extend["-u", user_arg]
    command.extend["-p", pass_arg]
    auth_type = "NTLM"
    if use_kerberos:
        command.append("-k")
        auth_type = "KERBEROS"

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)

        return target, protocol, auth_type, result.stdout
    except subprocess.TimeoutExpired:
        return target,protocol,auth_type, "</3 Scan timeout"
    except Exception as e:
        return target,protocol, f"Error: {e}"
    
def main():
    parser = argparse.ArgumentParser(description="Automatisation NXC (NetExec)")
    parser.add_argument("-t", "--target", required=True, help="IP cible, CIDR, ou fichier (ex: 192.168.1.10)")
    parser.add_argument("-u", "--user", required=True, help="Utilisateur ou fichier d'utilisateurs")
    parser.add_argument("-p", "--password", required=True, help="Mot de passe ou fichier de mots de passe")
    parser.add_argument("--protocols", nargs='+', default=["smb"], help="Liste des protocoles (ex: smb ssh winrm)")
    parser.add_argument("--threads", type=int, default=5, help="Nombre de threads simultanés")
    parser.add_argument("-k", "--kerberos", action="store_true", help="Use Kerberos authentication (-k)")
    parser.add_argument("-a", "--auto-auth", action="store_true", help="Test both NTLM and Kerberos automatically")

    args = parser.parse_args()

    tasks = []
  
    for proto in args.protocols:
        if args.auto_auth:
            tasks.append((args.target, proto, args.user, args.password, False)) # NTLM
            tasks.append((args.target, proto, args.user, args.password, True))  # Kerberos
        else:
            tasks.append((args.target, proto, args.user, args.password, args.kerberos))

    total_tasks = len(tasks)
    print(f"[*] Starting scan on {args.target} | Threads: {args.threads} | Total Tasks: {total_tasks}")
    print("-" * 50)

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(run_nxc, t[0], t[1], t[2], t[3]): t for t in tasks}
        
        for future in concurrent.futures.as_completed(futures):
            target, protocol, output = future.result()
            
            print(f"--- Results for {protocol.upper()} ---")
            
            # Filter noise, display only valid creds
            for line in output.split('\n'):
                if "[+]" in line or "Pwn3d!" in line:
                    print(line.strip())

if __name__ == "__main__":
    main()
