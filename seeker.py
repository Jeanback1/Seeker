#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import signal
import anthropic
import openai
import xml.etree.ElementTree as ET

# Professional UI Colors
GREEN = "\033[92m"
BLUE  = "\033[94m"
RED   = "\033[91m"
ENDC  = "\033[0m"
BOLD  = "\033[1m"

def signal_handler(sig, frame):
    """Exit gracefully on Ctrl+C."""
    print(f"\n{RED}[!] KeyboardInterrupt detected. Exiting...{ENDC}")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def load_config():
    """Read seeker.conf from the script's directory and return a key=value dict."""
    conf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seeker.conf")
    config = {}
    if not os.path.exists(conf_path):
        return config
    with open(conf_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            config[key.strip().lower()] = value.strip()
    return config


# --- AI Configuration: defaults → seeker.conf → env vars (highest priority) ---
_conf = load_config()

ANTHROPIC_API_KEY  = os.environ.get("ANTHROPIC_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
SEEKER_PROVIDER    = os.environ.get("SEEKER_PROVIDER") or _conf.get("provider", "anthropic")
SEEKER_MODEL       = os.environ.get("SEEKER_MODEL")    or _conf.get("model", "claude-sonnet-4-6")
SEEKER_LANGUAGE    = os.environ.get("SEEKER_LANGUAGE") or _conf.get("language", "english")

ANALYSIS_PROMPT_TEMPLATE_EN = """\
You are an expert CTF penetration tester and vulnerability researcher. \
Analyze the following nmap scan results and provide a structured attack plan.

TARGET SCAN DATA:
{scan_summary}

Provide your analysis in the following sections:

## 1. Open Ports & Services Summary
List each open port with the service, version, and a one-line description of what it does.

## 2. Attack Surface Assessment
Identify the most promising attack vectors ranked by likelihood of success in a CTF context. \
Consider: default credentials, known exploits for the detected versions, misconfigurations, \
weak authentication, anonymous access.

## 3. Specific Vulnerabilities
For each service, list:
- Known CVEs (if applicable to the detected version)
- Common exploits (Metasploit module names if available, ExploitDB IDs)
- Version-specific weaknesses

## 4. Recommended Attack Order
Provide a numbered step-by-step attack sequence, starting from the most accessible entry points.

## 5. Quick Wins
List any services or configurations that are commonly misconfigured in CTF environments \
and should be checked immediately (e.g., anonymous FTP, SMB null sessions, \
HTTP directory listing, default SSH keys, weak web application credentials).

## 6. Suggested Tools & Commands
For the top 3 attack vectors, provide the exact commands or tool invocations to begin exploitation.
"""

ANALYSIS_PROMPT_TEMPLATE_ES = """\
Eres un experto en pentesting CTF e investigación de vulnerabilidades. \
Analiza los siguientes resultados del escaneo nmap y proporciona un plan de ataque estructurado.

DATOS DEL ESCANEO:
{scan_summary}

Proporciona tu análisis en las siguientes secciones:

## 1. Resumen de Puertos Abiertos y Servicios
Lista cada puerto abierto con el servicio, versión y una descripción breve de su función.

## 2. Evaluación de la Superficie de Ataque
Identifica los vectores de ataque más prometedores ordenados por probabilidad de éxito en un \
contexto CTF. Considera: credenciales por defecto, exploits conocidos para las versiones \
detectadas, configuraciones incorrectas, autenticación débil, acceso anónimo.

## 3. Vulnerabilidades Específicas
Para cada servicio, lista:
- CVEs conocidos (si aplica a la versión detectada)
- Exploits comunes (nombres de módulos Metasploit si están disponibles, IDs de ExploitDB)
- Debilidades específicas de la versión

## 4. Orden de Ataque Recomendado
Proporciona una secuencia de ataque numerada paso a paso, comenzando por los puntos de \
entrada más accesibles.

## 5. Victorias Rápidas
Lista los servicios o configuraciones que suelen estar mal configurados en entornos CTF y \
que deben verificarse de inmediato (ej. FTP anónimo, sesiones nulas SMB, listado de \
directorios HTTP, claves SSH por defecto, credenciales débiles en aplicaciones web).

## 6. Herramientas y Comandos Sugeridos
Para los 3 vectores de ataque principales, proporciona los comandos exactos o invocaciones \
de herramientas para comenzar la explotación.
"""

ANALYSIS_PROMPT_TEMPLATE = (
    ANALYSIS_PROMPT_TEMPLATE_ES
    if SEEKER_LANGUAGE.lower() == "spanish"
    else ANALYSIS_PROMPT_TEMPLATE_EN
)


def print_banner():
    """Display the Seeker banner."""
    art = r"""
  _____  ______ ______ _  __ ______ _____
 / ____||  ____|  ____| |/ /|  ____|  __ \
| (___  | |__  | |__  | ' / | |__  | |__) |
 \___ \ |  __| |  __| |  <  |  __| |  _  /
 ____) || |____| |____| . \ | |____| | \ \
|_____/ |______|______|_|\_\|______|_|  \_\
"""
    print(f"{BLUE}{BOLD}{art}{ENDC}")
    print(f"            {BOLD}Target Intelligence & Lab Setup{ENDC}\n")


def create_environment(location, machine_name):
    """
    Creates a master folder for the machine inside the location,
    then populates it with scans, tools, and info directories.
    """
    target_path = os.path.join(location, machine_name)
    subfolders  = ['scans', 'tools', 'info']

    print(f"{BLUE}[*]{ENDC} Setting up workspace for: {BOLD}{machine_name}{ENDC}")

    try:
        if not os.path.exists(target_path):
            os.makedirs(target_path)
            print(f"{GREEN}[+]{ENDC} Created base directory: {target_path}")

        for folder in subfolders:
            folder_path = os.path.join(target_path, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"{GREEN}[+]{ENDC} Created: {folder_path}")

        return target_path

    except OSError as e:
        print(f"{RED}[!] OS Error: {e}{ENDC}")
        sys.exit(1)


def run_initial_scan(target_ip, target_path):
    """Execute Nmap and save results in XML format."""
    output_file = os.path.join(target_path, "scans", "general_scan.xml")

    print(f"{BLUE}[*]{ENDC} Launching aggressive Nmap scan on {BOLD}{target_ip}{ENDC}...")

    # -sVC: Version detection and default scripts
    # -p-: All ports
    # --open: Show only open ports
    # --min-rate 5000: Send packets no slower than 5000 per second
    # -oX: Save output in XML format to the specified file
    nmap_cmd = [
        "sudo", "nmap", "-sVC", "-p-", "--open",
        "--min-rate", "5000", "-oX", output_file, target_ip
    ]

    try:
        subprocess.run(nmap_cmd, check=True)
        print(f"{GREEN}[+]{ENDC} Scan finished. XML saved: {BOLD}{output_file}{ENDC}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{RED}[!] Scanning failed: Check if Nmap is installed or if you have sudo permissions.{ENDC}")


def _parse_nmap_xml(xml_path):
    """
    Parse nmap XML into a human-readable summary string.
    Extracts hosts, ports, services, versions, and NSE script output.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    lines = []

    for host in root.findall("host"):
        addr_el = host.find("address[@addrtype='ipv4']")
        ip = addr_el.get("addr") if addr_el is not None else "unknown"
        lines.append(f"Host: {ip}")

        hostname_el = host.find("hostnames/hostname")
        if hostname_el is not None:
            lines.append(f"Hostname: {hostname_el.get('name')}")

        os_el = host.find("os/osmatch")
        if os_el is not None:
            lines.append(f"OS (guessed): {os_el.get('name')} ({os_el.get('accuracy')}% accuracy)")

        lines.append("\nOpen Ports:")
        for port in host.findall("ports/port"):
            state_el = port.find("state")
            if state_el is None or state_el.get("state") != "open":
                continue

            portid   = port.get("portid")
            protocol = port.get("protocol")
            svc      = port.find("service")
            svc_name = svc.get("name", "unknown") if svc is not None else "unknown"
            product  = svc.get("product", "")      if svc is not None else ""
            version  = svc.get("version", "")      if svc is not None else ""
            extra    = svc.get("extrainfo", "")    if svc is not None else ""

            svc_line = f"  {portid}/{protocol}  {svc_name}"
            if product: svc_line += f"  {product}"
            if version: svc_line += f" {version}"
            if extra:   svc_line += f" ({extra})"
            lines.append(svc_line)

            for script in port.findall("script"):
                script_id  = script.get("id", "")
                script_out = script.get("output", "").strip()
                if script_out:
                    lines.append(f"    [script: {script_id}]")
                    for sline in script_out.splitlines():
                        lines.append(f"      {sline}")

    return "\n".join(lines)


def analyze_with_ai(target_path):
    """Send nmap XML scan results to the AI for vulnerability analysis."""

    if SEEKER_PROVIDER not in ("anthropic", "openrouter"):
        print(f"{RED}[!]{ENDC} Unknown SEEKER_PROVIDER '{SEEKER_PROVIDER}'. Use 'anthropic' or 'openrouter'.")
        return

    if SEEKER_PROVIDER == "anthropic" and not ANTHROPIC_API_KEY:
        print(f"{RED}[!]{ENDC} ANTHROPIC_API_KEY not set. Skipping AI analysis.")
        print(f"    Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return

    if SEEKER_PROVIDER == "openrouter" and not OPENROUTER_API_KEY:
        print(f"{RED}[!]{ENDC} OPENROUTER_API_KEY not set. Skipping AI analysis.")
        print(f"    Set it with: export OPENROUTER_API_KEY='your-key-here'")
        return

    xml_path    = os.path.join(target_path, "scans", "general_scan.xml")
    output_file = os.path.join(target_path, "scans", "vulnerability_analysis.txt")

    if not os.path.exists(xml_path):
        print(f"{RED}[!]{ENDC} Scan XML not found at {xml_path}. Skipping AI analysis.")
        return

    print(f"{BLUE}[*]{ENDC} Parsing scan results for AI analysis...")

    try:
        scan_summary = _parse_nmap_xml(xml_path)
    except ET.ParseError as e:
        print(f"{RED}[!]{ENDC} Failed to parse nmap XML: {e}. Skipping AI analysis.")
        return

    if not scan_summary.strip():
        print(f"{RED}[!]{ENDC} Scan XML appears empty. Did nmap find any open ports?")
        return

    prompt = ANALYSIS_PROMPT_TEMPLATE.format(scan_summary=scan_summary)

    print(f"{BLUE}[*]{ENDC} Sending scan to AI ({SEEKER_PROVIDER} / {BOLD}{SEEKER_MODEL}{ENDC}) for vulnerability analysis...")

    ai_response = None

    if SEEKER_PROVIDER == "anthropic":
        try:
            client      = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            message     = client.messages.create(
                model      = SEEKER_MODEL,
                max_tokens = 2048,
                messages   = [{"role": "user", "content": prompt}]
            )
            ai_response = message.content[0].text
        except anthropic.AuthenticationError:
            print(f"{RED}[!]{ENDC} AI authentication failed. Check your ANTHROPIC_API_KEY.")
            return
        except anthropic.RateLimitError:
            print(f"{RED}[!]{ENDC} AI rate limit reached. Try again in a moment.")
            return
        except anthropic.APIConnectionError:
            print(f"{RED}[!]{ENDC} Could not reach the Anthropic API. Check your internet connection.")
            return
        except anthropic.APIError as e:
            print(f"{RED}[!]{ENDC} Anthropic API error: {e}. Skipping analysis.")
            return

    elif SEEKER_PROVIDER == "openrouter":
        try:
            client      = openai.OpenAI(
                api_key  = OPENROUTER_API_KEY,
                base_url = "https://openrouter.ai/api/v1"
            )
            completion  = client.chat.completions.create(
                model      = SEEKER_MODEL,
                max_tokens = 2048,
                messages   = [{"role": "user", "content": prompt}]
            )
            ai_response = completion.choices[0].message.content
        except openai.AuthenticationError:
            print(f"{RED}[!]{ENDC} OpenRouter authentication failed. Check your OPENROUTER_API_KEY.")
            return
        except openai.RateLimitError:
            print(f"{RED}[!]{ENDC} OpenRouter rate limit reached. Try again in a moment.")
            return
        except openai.APIConnectionError:
            print(f"{RED}[!]{ENDC} Could not reach OpenRouter. Check your internet connection.")
            return
        except openai.APIError as e:
            print(f"{RED}[!]{ENDC} OpenRouter API error: {e}. Skipping analysis.")
            return

    if ai_response is None:
        return

    try:
        with open(output_file, "w") as f:
            f.write(f"# AI Vulnerability Analysis\n")
            f.write(f"# Provider: {SEEKER_PROVIDER}\n")
            f.write(f"# Model:    {SEEKER_MODEL}\n")
            f.write(f"# Target:   {target_path}\n")
            f.write("=" * 60 + "\n\n")
            f.write(ai_response)
        print(f"{GREEN}[+]{ENDC} AI analysis saved: {BOLD}{output_file}{ENDC}")
    except OSError as e:
        print(f"{RED}[!]{ENDC} OS Error writing analysis file: {e}")


def main():
    print_banner()

    parser = argparse.ArgumentParser(description="Seeker: Automate your pentesting lab structure.")

    parser.add_argument("-i", "--ip",       help="Target IP address",                         required=True)
    parser.add_argument("-n", "--name",     help="Name of the target machine",                required=True)
    parser.add_argument("-u", "--location", help="Base directory (e.g., /home/user/HTB)",     required=True)

    args = parser.parse_args()

    # 1. Build the directory structure
    full_target_path = create_environment(args.location, args.name)

    # 2. Run the nmap scan (XML output)
    run_initial_scan(args.ip, full_target_path)

    # 3. AI vulnerability analysis
    analyze_with_ai(full_target_path)

    print(f"\n{GREEN}{BOLD}[!] Seeker task finished successfully.{ENDC}")


if __name__ == "__main__":
    main()
