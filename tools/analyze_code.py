#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse automatique du code Python du projet Smart CV Generator.
Vérifie le formatage (Black), le style (Flake8) et le typage (Mypy).
Les résultats sont sauvegardés dans tools/.last_analysis.log
pour envoi par e-mail via send_report.py.
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# ===========================
# Configuration
# ===========================

LOG_DIR = Path("tools")
LOG_PATH = LOG_DIR / ".last_analysis.log"
APP_DIR = Path("app")

# Créer le dossier tools si absent
LOG_DIR.mkdir(exist_ok=True)

# ===========================
# Fonctions utilitaires
# ===========================

def run_tool(name: str, cmd: list) -> tuple[bool, str]:
    """Exécute un outil via python -m et retourne (succès, sortie)."""
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
        success = result.returncode == 0
        return success, output
    except FileNotFoundError:
        return False, f"{name} non trouvé. Installe-le avec 'pip install {name.lower()}'"
    except Exception as e:
        return False, f"Erreur inattendue : {e}"


def log_result(lines: list, tool: str, success: bool, details: str = "") -> None:
    """Ajoute un résultat au rapport."""
    status = "Réussi" if success else "Échec"
    lines.append(f"{tool} — {status}")
    if details:
        lines.append("--- Détails ---")
        lines.append(details)
    lines.append("")


# ===========================
# Analyse principale
# ===========================

def main() -> int:
    print("Lancement de l'analyse du projet Smart CV Generator...\n")

    # Outils avec python -m (garanti de marcher après pip install)
    tools = {
        "Black (formatage)": [sys.executable, "-m", "black", "--check", "--diff", str(APP_DIR)],
        "Flake8 (lint)": [sys.executable, "-m", "flake8", str(APP_DIR)],
        "Mypy (typage strict)": [sys.executable, "-m", "mypy", str(APP_DIR)],
    }

    report_lines = []
    all_success = True

    # En-tête
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines.append("=" * 60)
    report_lines.append(f"Rapport d'analyse du {timestamp}")
    report_lines.append("=" * 60 + "\n")

    # Exécution
    for name, cmd in tools.items():
        print(f"{name}...")
        success, output = run_tool(name, cmd)
        log_result(report_lines, name, success, output)

        print(f"{'Réussi' if success else 'Échec'}")
        if not success:
            all_success = False
        print()

    # Résumé
    if all_success:
        summary = "Tout est propre ! Le code respecte les standards de qualité.\n"
    else:
        summary = "Des problèmes ont été détectés. Corrigez-les avant de committer/pusher.\n"
        print(summary)

    report_lines.append("=" * 60)
    report_lines.append(summary)
    report_lines.append("=" * 60 + "\n")

    # Sauvegarde
    try:
        LOG_PATH.write_text("\n".join(report_lines), encoding="utf-8")
        print(f"Rapport sauvegardé : {LOG_PATH}")
    except Exception as e:
        print(f"Impossible d’écrire le rapport : {e}")

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())