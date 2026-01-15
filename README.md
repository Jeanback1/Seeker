Nmap-Report-Gen (or your tool name)

A streamlined automation tool designed to execute and organize Nmap scans specifically for laboratory environments and CTF platforms like Hack The Box (HTB) or TryHackMe.
🚀 Purpose & Philosophy

Unlike real-world engagements where stealth is paramount, this tool is built for speed and maximum information gathering.

    Noisy by Design: In a CTF environment, we don't care about EDR or SOC alerts. We want every bit of data as fast as possible.

    Zero Noise-Floor: By utilizing the --open flag, the script ignores closed and filtered ports, keeping your reports clean and focused strictly on viable attack vectors.

✨ Key Features

    Automated Directory Structuring: Use the -n flag to create a dedicated folder for the target machine, keeping your workspace organized.

    Focused Results: Filters out irrelevant data by only reporting Open Ports.

    HTB Optimized: Pre-configured to handle the aggressive scanning often required for complex lab machines.

    Clean Output: Generates a structured summary ready for documentation or further exploitation phases.

🛠 Installation

Ensure you have nmap installed on your system.

# Clone the repository
git clone https://github.com/Jeanback1/seeker

# Enter the directory
cd seeker

# Make the script executable
chmod +x seeker.py

📖 Usage

The script is designed to be simple and efficient.

python3 seeker.py -n <MachineName> -i <Target_IP> -u <path>


🛡 Disclaimer

This tool is intended for educational purposes and authorized security auditing only. It is designed for controlled lab environments (HTB, THM, Proving Grounds). Unauthorized scanning of infrastructure you do not own is illegal.



