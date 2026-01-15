# Seeker

-Automated Workspace Setup: Automatically creates a dedicated directory for the target machine to keep your environment organized from minute one.

-Standardized Recon: Runs the essential Nmap scan that every machine requires, ensuring you never miss a common service.

-Auto-Logging: Pipe-lined output directly into a structured .txt file, ready for your notes or documentation.

-Laboratory Optimized: Specifically tailored for CTF environments where speed and data volume are more important than stealth.

-Noisy by Design: In a CTF environment, we don't care about EDR or SOC alerts. We want every bit of data as fast as possible.

-Zero Noise-Floor: By utilizing the --open flag, the script ignores closed and filtered ports, keeping your reports clean and focused strictly on viable attack vectors.


# Installation

    Ensure you have nmap installed on your system.

Clone the repository

    git clone https://github.com/Jeanback1/seeker

Enter the directory

    cd seeker

Make the script executable

    chmod +x seeker.py

# Usage

The script is designed to be simple and efficient.

    python3 seeker.py -n <MachineName> -i <Target_IP> -u <path>


🛡 Disclaimer

This tool is intended for educational purposes and authorized security auditing only. It is designed for controlled lab environments (HTB, THM, Proving Grounds). Unauthorized scanning of infrastructure you do not own is illegal.



