#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import signal

# Professional UI Colors
GREEN = "\033[92m"
BLUE = "\033[94m"
RED = "\033[91m"
ENDC = "\033[0m"
BOLD = "\033[1m"

def signal_handler(sig, frame):
    """Exit gracefully on Ctrl+C."""
    print(f"\n{RED}[!] KeyboardInterrupt detected. Exiting...{ENDC}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def print_banner():
    """Display the Seeker banner."""
    banner = f"""
{BLUE}{BOLD}
  _____  ______ ______ _  __ ______ _____  
 / ____||  ____|  ____| |/ /|  ____|  __ \ 
| (___  | |__  | |__  | ' / | |__  | |__) |
 \___ \ |  __| |  __| |  <  |  __| |  _  / 
 ____) || |____| |____| . \ | |____| | \ \ 
|_____/ |______|______|_|\_\|______|_|  \_\
{ENDC}
            {BOLD}Target Intelligence & Lab Setup{ENDC}
    """
    print(banner)

def create_environment(location, machine_name):
    """
    Creates a master folder for the machine inside the location,
    then populates it with scans, tools, and info directories.
    """
    # Define the full path for the machine
    target_path = os.path.join(location, machine_name)
    subfolders = ['scans', 'tools', 'info']
    
    print(f"{BLUE}[*]{ENDC} Setting up workspace for: {BOLD}{machine_name}{ENDC}")
    
    try:
        # Create the machine's main directory if it doesn't exist
        if not os.path.exists(target_path):
            os.makedirs(target_path)
            print(f"{GREEN}[+]{ENDC} Created base directory: {target_path}")
        
        # Create subdirectories
        for folder in subfolders:
            folder_path = os.path.join(target_path, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"{GREEN}[+]{ENDC} Created: {folder_path}")
                
        return target_path # Return the path to be used by the scanner
                
    except OSError as e:
        print(f"{RED}[!] OS Error: {e}{ENDC}")
        sys.exit(1)

def run_initial_scan(target_ip, target_path):
    """Execute Nmap and save results using Nmap's native output flag."""
    output_file = os.path.join(target_path, "scans", "general_scan.txt")
    
    print(f"{BLUE}[*]{ENDC} Launching aggressive Nmap scan on {BOLD}{target_ip}{ENDC}...")
    
    # Corrected Nmap command:
    # -sVC: Version detection and default scripts
    # -p-: All ports
    # --open: Show only open ports
    # --min-rate 5000: Send packets no slower than 5000 per second
    # -oN: Save output in Nmap format to the specified file
    nmap_cmd = [
        "sudo", "nmap", "-sVC", "-p-", "--open", 
        "--min-rate", "5000", "-oN", output_file, target_ip
    ]
    
    try:
        # We don't need shell=True if we use the list format and -oN
        subprocess.run(nmap_cmd, check=True)
        print(f"{GREEN}[+]{ENDC} Scan finished. File saved: {BOLD}{output_file}{ENDC}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{RED}[!] Scanning failed: Check if Nmap is installed or if you have sudo permissions.{ENDC}")

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="Seeker: Automate your pentesting lab structure.")
    
    # Arguments definition
    parser.add_argument("-i", "--ip", help="Target IP address", required=True)
    parser.add_argument("-n", "--name", help="Name of the target machine", required=True)
    parser.add_argument("-u", "--location", help="Base directory (e.g., /home/user/HTB)", required=True)
    
    args = parser.parse_args()
    
    # 1. Build the directory structure
    full_target_path = create_environment(args.location, args.name)
    
    # 2. Run the scan using the new path
    run_initial_scan(args.ip, full_target_path)
    
    print(f"\n{GREEN}{BOLD}[!] Seeker task finished successfully.{ENDC}")

if __name__ == "__main__":
    main()
