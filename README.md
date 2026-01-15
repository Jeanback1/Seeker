
<img width="627" height="245" alt="audit-20260115-012446" src="https://github.com/user-attachments/assets/24fa8a0a-0703-4dc8-83e5-5de8737a79f3" />

-Automated Workspace Setup: Automatically creates a dedicated directory for the target machine to keep your environment organized from minute one.


<img width="349" height="39" alt="audit-20260115-012022" src="https://github.com/user-attachments/assets/07ef025a-8289-46f6-bc7a-64707eb16538" />



-Auto-Logging: Pipe-lined output directly into a structured .txt file, ready for your notes or documentation.


<img width="266" height="34" alt="audit-20260115-012037" src="https://github.com/user-attachments/assets/42b1216c-a23f-42ef-94d0-33e475606926" />



-Laboratory Optimized: Specifically tailored for CTF environments where speed and data volume are more important than stealth.

-Noisy by Design: In a CTF environment, we don't care about EDR or SOC alerts. We want every bit of data as fast as possible.


<img width="765" height="52" alt="audit-20260115-012304" src="https://github.com/user-attachments/assets/5c4528cd-15c4-4437-9b06-1118fe2605b6" />



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



