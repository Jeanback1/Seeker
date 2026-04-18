
<img width="627" height="245" alt="audit-20260115-012446" src="https://github.com/user-attachments/assets/24fa8a0a-0dc8-83e5-5de8737a79f3" />

-Automated Workspace Setup: Automatically creates a dedicated directory for the target machine to keep your environment organized from minute one.


<img width="349" height="39" alt="audit-20260115-012022" src="https://github.com/user-attachments/assets/07ef025a-8289-46f6-bc7a-64707eb16538" />



-Auto-Logging: Scan results are automatically saved to structured files, ready for your notes or documentation.


<img width="266" height="34" alt="audit-20260115-012037" src="https://github.com/user-attachments/assets/42b1216c-a23f-42ef-94d0-33e475606926" />



-Laboratory Optimized: Specifically tailored for CTF environments where speed and data volume are more important than stealth.

-Noisy by Design: In a CTF environment, we don't care about EDR or SOC alerts. We want every bit of data as fast as possible.


<img width="765" height="52" alt="audit-20260115-012304" src="https://github.com/user-attachments/assets/5c4528cd-15c4-4437-9b06-1118fe2605b6" />



-Zero Noise-Floor: By utilizing the --open flag, the script ignores closed and filtered ports, keeping your reports clean and focused strictly on viable attack vectors.

-AI-Powered Vulnerability Analysis: After the nmap scan completes, Seeker automatically sends the results to an AI model (Anthropic or OpenRouter) for a structured CTF-focused analysis. The output includes attack surface ranking, specific CVEs, recommended attack order, quick wins, and exact tool commands — saved automatically to `vulnerability_analysis.txt`.


# Installation

    Ensure you have nmap installed on your system.

Clone the repository

    git clone https://github.com/Jeanback1/seeker

Enter the directory

    cd seeker

Install Python dependencies

    pip install -r requirements.txt

Make the script executable

    chmod +x seeker.py


# AI Configuration (optional)

Seeker can automatically analyze nmap results using an AI model. The tool runs fine without it, but configuring a provider unlocks the vulnerability analysis feature.

**Anthropic (default)**

    export ANTHROPIC_API_KEY="sk-ant-..."

**OpenRouter (alternative)**

    export OPENROUTER_API_KEY="sk-or-..."
    export SEEKER_PROVIDER="openrouter"

**Optional overrides**

    export SEEKER_PROVIDER="anthropic"           # default: anthropic
    export SEEKER_MODEL="claude-sonnet-4-6"      # default: claude-sonnet-4-6


# Usage

The script is designed to be simple and efficient.

    python3 seeker.py -n <MachineName> -i <Target_IP> -u <path>

Example:

    python3 seeker.py -n HTB-Lame -i 10.10.10.3 -u /home/user/HTB

**Output structure created:**

    /home/user/HTB/HTB-Lame/
    ├── scans/
    │   ├── general_scan.xml              ← raw nmap XML output
    │   └── vulnerability_analysis.txt    ← AI analysis (if API key configured)
    ├── tools/
    └── info/

The `vulnerability_analysis.txt` file contains a structured report with:
- Open ports & services summary
- Attack surface assessment ranked by CTF likelihood
- Specific vulnerabilities (CVEs, Metasploit modules, ExploitDB IDs)
- Recommended attack order
- Quick wins (common CTF misconfigurations)
- Suggested tools and exact commands for the top attack vectors


🛡 Disclaimer

This tool is intended for educational purposes and authorized security auditing only. It is designed for controlled lab environments (HTB, THM, Proving Grounds). Unauthorized scanning of infrastructure you do not own is illegal.


