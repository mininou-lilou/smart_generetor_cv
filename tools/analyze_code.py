#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse complète : syntaxe, format, style, logique, typage, sécurité
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ===========================
# Configuration
# ===========================

LOG_DIR = Path("tools")
LOG_PATH = LOG_DIR / ".last_analysis.log"
APP_DIR = Path("app")
LOG_DIR.mkdir(exist_ok=True)

# ===========================
# Fonctions utilitaires
# ===========================

def run_tool(name: str, cmd: list) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=Path.cwd()
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except FileNotFoundError:
        return False, f"{name} non trouvé. Installe-le avec 'pip install {name.lower()}'"
    except Exception as e:
        return False, f"Erreur : {e}"

def log_result(lines: list, tool: str, success: bool, details: str = "") -> None:
    status = "Réussi" if success else "Échec"
    lines.append(f"{tool} — {status}")
    if details:
        lines.append("--- Détails ---")
        lines.append(details)
    lines.append("")

def check_requests_usage() -> tuple[bool, str]:
    issues = []
    for py_file in APP_DIR.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
            if "requests." in content and "try:" not in content and "except" not in content:
                issues.append(f"{py_file}: 'requests' utilisé sans try/except")
        except:
            pass
    return (len(issues) == 0, "\n".join(issues) if issues else "")

# ===========================
# Analyse principale
# ===========================

def main() -> int:
    print("Lancement de l'analyse complète...\n")

    # INITIALISE LE RAPPORT AVANT TOUT
    report_lines = []
    all_success = True

    # En-tête
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines.append("=" * 60)
    report_lines.append(f"Rapport d'analyse du {timestamp}")
    report_lines.append("=" * 60 + "\n")

    # === OUTILS ===
    tools = {
        "Syntaxe Python": [sys.executable, "-m", "py_compile"] + [str(p) for p in APP_DIR.rglob("*.py")],
        "Black (formatage)": [sys.executable, "-m", "black", "--check", "--diff", str(APP_DIR)],
        "Flake8 (lint)": [sys.executable, "-m", "flake8", str(APP_DIR)],
        "Pylint (logique)": [sys.executable, "-m", "pylint", "--recursive=y", str(APP_DIR)],
        "Mypy (typage)": [sys.executable, "-m", "mypy", str(APP_DIR)],
    }

    for name, cmd in tools.items():
        print(f"{name}...")
        success, output = run_tool(name, cmd)
        log_result(report_lines, name, success, output)
        print(f"{'Réussi' if success else 'Échec'}")
        if not success:
            all_success = False
        print()

    # === VÉRIFICATION REQUESTS ===
    print("Requests (sécurité)...")
    success_req, output_req = check_requests_usage()
    log_result(report_lines, "Requests (sécurité)", success_req, output_req)
    print(f"{'Réussi' if success_req else 'Échec'}")
    if not success_req:
        all_success = False
    print()

    # === RÉSUMÉ ===
    summary = "Tout est propre !\n" if all_success else "Des problèmes détectés.\n"
    print(summary)
    report_lines.append("=" * 60)
    report_lines.append(summary)
    report_lines.append("=" * 60 + "\n")

    # === SAUVEGARDE ===
    try:
        LOG_PATH.write_text("\n".join(report_lines), encoding="utf-8")
        print(f"Rapport sauvegardé : {LOG_PATH}")
    except Exception as e:
        print(f"Échec sauvegarde : {e}")

    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())