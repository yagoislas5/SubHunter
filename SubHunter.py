#!/usr/bin/env python3
import argparse
import os
import subprocess
import json
# =============================
# ===== COLORES TERMINAL =====
# =============================
RED = "\033[91m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RESET = "\033[0m"
# =============================
# ===== ASCII BANNER ==========
# =============================
BANNER = f"""
{CYAN}                                                                               
 @@@@@@ @@@  @@@ @@@@@@@  @@@  @@@ @@@  @@@ @@@  @@@ @@@@@@@ @@@@@@@@ @@@@@@@  
!@@     @@!  @@@ @@!  @@@ @@!  @@@ @@!  @@@ @@!@ @@@   @!!   @@!      @@!  @@@ 
 !@@!!  @!@  !@! @!@!@!@  @!@!@!@! @!@  !@! @!@@!!@!   @!!   @!!!:!   @!@!!@!  
    !:! !!:  !!! !!:  !!! !!:  !!! !!:  !!! !!:  '!!   !!:   !!:      !!: :!!  
::.: :   :.::.:  :::::::  :.   : :  :.::.:  ::    ':    :    : :: ::  .:   : : 
                                                                               
        {YELLOW}SubHunter – Subdomain Finder & HTTP Classifier{RESET}
"""
# =============================
# ===== EJECUTAR COMANDO ======
# =============================
def run_cmd(cmd):
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return proc.stdout.strip().splitlines()
    except Exception as e:
        print(f"{RED}[!] Fallo crítico: {e}{RESET}")
        return []
# =============================
# ===== CHECK TOOL ============
# =============================
def tool_exists(tool):
    return subprocess.call(
        f"command -v {tool}",
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ) == 0
# =============================
# ===== SUBDOMAIN ENUM ========
# =============================
def gather_subdomains(domain, outdir):
    all_subs = set()
    tools = {
        "subfinder": f"subfinder -d {domain} -silent",
        "assetfinder": f"assetfinder --subs-only {domain}",
        "findomain": f"findomain -t {domain} -q",
        "sublist3r": f"sublist3r -d {domain} -o {outdir}/.sublist3r.tmp"
    }
    print(f"{CYAN}========= {domain} ========={RESET}")
    for tool, cmd in tools.items():
        if not tool_exists(tool):
            print(f"{RED}[!] {tool} no está instalado{RESET}")
            continue
        print(f"{YELLOW}[+] Ejecutando {tool}...{RESET}")
        # Manejo especial sublist3r
        if tool == "sublist3r":
            tmp_file = f"{outdir}/.sublist3r.tmp"
            subs = []
            subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if os.path.exists(tmp_file):
                with open(tmp_file) as f:
                    subs = [x.strip() for x in f if x.strip()]
                os.remove(tmp_file)
            all_subs.update(subs)
            print(f"{GREEN}[+] sublist3r: {len(subs)} subdominios{RESET}")
            continue
        # Herramientas stdout
        subs = run_cmd(cmd)
        all_subs.update(subs)
        print(f"{GREEN}[+] {tool}: {len(subs)} subdominios{RESET}")
    # Guardar subdomains.txt
    final_file = f"{outdir}/subdomains.txt"
    with open(final_file, "w") as f:
        for s in sorted(all_subs):
            f.write(s + "\n")
    print(f"{GREEN}[✓] Total subdominios únicos: {len(all_subs)}{RESET}")
    print(f"{GREEN}[✓] Guardados en: {final_file}{RESET}")
    return final_file
# =============================
# ===== HTTPX CLASSIFIER ======
# =============================
def classify_with_httpx(sub_file, outdir):
    if not tool_exists("httpx"):
        print(f"{RED}[!] httpx no está instalado{RESET}")
        return
    print(f"{YELLOW}[+] Ejecutando httpx...{RESET}")
    cmd = (
        f"httpx -l {sub_file} "
        f"-json -status-code -follow-redirects -silent"
    )
    raw = run_cmd(cmd)
    results = {}
    timeouts = set()
    for line in raw:
        try:
            j = json.loads(line)
        except:
            continue
        host = j.get("host") or j.get("input")
        status = j.get("status_code")
        if not host:
            continue
        if status is not None:
            status = str(status)
            results.setdefault(status, set()).add(host)
        else:
            timeouts.add(host)
    for code, hosts in results.items():
        outfile = f"{outdir}/{code}.txt"
        with open(outfile, "w") as f:
            for h in sorted(hosts):
                f.write(h + "\n")
        print(f"{GREEN}[✓] {code}: {len(hosts)} hosts{RESET}")
    if timeouts:
        outfile = f"{outdir}/timeout.txt"
        with open(outfile, "w") as f:
            for h in sorted(timeouts):
                f.write(h + "\n")
        print(f"{RED}[!] Timeouts: {len(timeouts)} hosts{RESET}")
    print(f"{GREEN}[✓] Clasificación HTTP finalizada{RESET}")
# =============================
# ============ MAIN ===========
# =============================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("domain", help="Dominio objetivo (ej: example.com)")
    args = parser.parse_args()
    domain = args.domain.strip().lower()
    domain = domain.replace("https://", "").replace("http://", "").rstrip("/")
    outdir = domain
    os.makedirs(outdir, exist_ok=True)
    print(BANNER)
    sub_file = gather_subdomains(domain, outdir)
    classify_with_httpx(sub_file, outdir)
    # Print directory tree
    print(f"\n{CYAN}Output Directory Structure:{RESET}")
    print(f"{domain}/")
    files = [f for f in os.listdir(outdir) if not f.startswith('.')]
    sorted_files = sorted(files)
    for i, file in enumerate(sorted_files):
        if i == len(sorted_files) - 1:
            prefix = "└─ "
        else:
            prefix = "├─ "
        print(prefix + file)

if __name__ == "__main__":
    main()
