# Seeker — Contexto del Proyecto

## Propósito

**Seeker** es una herramienta CLI en Python para automatizar la configuración de entornos de trabajo en pentesting y CTF (Capture The Flag). Resuelve un problema concreto: crear la estructura de directorios del laboratorio y lanzar el reconocimiento inicial con Nmap en un solo comando.

Entornos objetivo:
- HackTheBox (HTB)
- TryHackMe (THM)
- Proving Grounds
- Auditorías autorizadas en entornos controlados

> **Disclaimer:** Solo para uso educativo y en entornos con autorización. No para escaneos no autorizados.

---

## Estructura del Proyecto

```
/home/jean/tools/Seeker/
├── seeker.py        # Script principal (~114 líneas)
├── README.md        # Documentación pública
└── context.md       # Este archivo
```

Repositorio: `https://github.com/Jeanback1/Seeker`  
Ramas: `main` (producción), `prueba` (experimental)

---

## Tech Stack

| Componente       | Detalle                                      |
|------------------|----------------------------------------------|
| Lenguaje         | Python 3                                     |
| Dependencias     | Solo stdlib: `argparse`, `os`, `subprocess`, `sys`, `signal` |
| Herramienta ext. | `nmap` (instalado en el sistema)             |
| Sin pip deps     | No hay `requirements.txt` ni paquete PyPI    |

---

## CLI

```bash
python3 seeker.py -n <NombreMáquina> -i <IP_Objetivo> -u <RutaBase>
```

| Flag             | Descripción                                  |
|------------------|----------------------------------------------|
| `-n, --name`     | Nombre de la máquina objetivo (crea carpeta) |
| `-i, --ip`       | IP del objetivo (escaneada con Nmap)         |
| `-u, --location` | Ruta base donde se creará el workspace       |

**Ejemplo:**
```bash
python3 seeker.py -n "HTB-Lame" -i "10.10.10.3" -u "/home/jean/HTB"
```

---

## Flujo de la Aplicación

1. Muestra banner ASCII (logo + tagline *"Target Intelligence & Lab Setup"*)
2. Parsea los argumentos CLI
3. Crea el workspace en `<location>/<name>/`:
   ```
   ├── scans/     # Resultados de Nmap
   ├── tools/     # Herramientas de pentesting
   └── info/      # Información del objetivo
   ```
4. Ejecuta Nmap con flags agresivos:
   - `-sVC` — detección de versiones + scripts por defecto
   - `-p-` — todos los puertos (65535)
   - `--open` — solo puertos abiertos
   - `--min-rate 5000` — escaneo rápido
   - `-oN scans/general_scan.txt` — guarda el resultado
5. Requiere `sudo` para el escaneo

---

## Estructura de seeker.py

| Sección              | Líneas  | Descripción                                     |
|----------------------|---------|-------------------------------------------------|
| Colores ANSI         | 10–14   | GREEN, BLUE, RED, BOLD, ENDC                    |
| `signal_handler()`   | 16–21   | Manejo limpio de Ctrl+C                         |
| `print_banner()`     | 23–36   | ASCII art del logo                              |
| `create_environment()` | 38–66 | Crea la estructura de directorios               |
| `run_initial_scan()` | 68–90   | Ejecuta Nmap y guarda resultados                |
| `main()`             | 92–113  | Punto de entrada, orquesta todo el flujo        |

---

## Instalación

```bash
git clone https://github.com/Jeanback1/Seeker
cd Seeker
chmod +x seeker.py
# Asegurarse de tener nmap instalado
```

---

## Características de Diseño

- **Noisy by design** — Prioriza velocidad y datos sobre sigilo (uso en labs, no en producción real)
- **Zero noise-floor** — `--open` filtra solo puertos con vectores de ataque viables
- **Auto-logging** — Los resultados se guardan automáticamente en archivos `.txt`
- **Sin dependencias externas Python** — Script portable, solo necesita Python 3 + nmap

---

## Estado del Proyecto

- 4 commits en historial
- Herramienta funcional y estable
- Posibles áreas de expansión: más tipos de escaneo, soporte para múltiples IPs, integración con otras herramientas (gobuster, ffuf, etc.)
