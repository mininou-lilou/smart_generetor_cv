#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyse automatique du code Python du projet Smart CV Generator.
Vérifie le formatage (Black), le style (Flake8) et le typage (Mypy).
Les résultats sont affichés clairement et sauvegardés dans tools/.last_analysis.log
pour envoi par e-mail via send_report.py.
"""

import subprocess
import sys
import io
import os
from datetime import datetime
from typing import Tuple
from dotenv import load_dotenv

# Forcer l'encodage UTF-8 sur Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Charger les variables locales (.env) si présentes
load_dotenv()

# Récupération des secrets (compatibles GitHub Actions et .env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
GEMINI_APP_PASSWORD = os.getenv("GEMINI_APP_PASSWORD")

if not GEMINI_API_KEY:
    print("⚠️  Avertissement : aucune clé IA détectée (GEMINI_API_KEY).")
else:
    print("🔑 Clé API IA détectée (masquée pour sécurité).")

if not SENDER_EMAIL or not GEMINI_APP_PASSWORD:
    print("⚠️  Les variables e-mail ne sont pas toutes définies (SENDER_EMAIL / GEMINI_APP_PASSWORD).")
    print("➡️  Configure-les dans tes secrets GitHub ou ton fichier .env.\n")


# ===========================
# ⚙️ Fonctions utilitaires
# ===========================

def run_command(command: str) -> Tuple[int, str]:
    """Exécute une commande shell et retourne (code_retour, sortie)."""
    process = subprocess.run(
        command, shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return process.returncode, (process.stdout + process.stderr).strip()


def print_status(tool: str, success: bool, details: str = "") -> None:
    """Affiche un message coloré selon le succès ou l’échec."""
    symbol = "✅" if success else "❌"
    print(f"{symbol} {tool} {'réussi' if success else 'a échoué.'}")
    if not success and details:
        print(details)
    print()


# ===========================
# 🚀 Analyse principale
# ===========================

def main() -> None:
    print("🚀 Lancement de l'analyse du projet Smart CV Generator...\n")

    tools = {
        "Black (formatage)": "black --check app/",
        "Flake8 (lint)": "flake8 app/",
        "Mypy (typage strict)": "mypy app/",
    }

    global_success = True
    report_lines = []

    # Ajout d’un en-tête dans le rapport
    report_lines.append("=" * 60)
    report_lines.append(f"🧪 Rapport d'analyse du {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 60 + "\n")

    for tool, command in tools.items():
        print(f"🔍 {tool}...")
        code, output = run_command(command)
        success = code == 0
        print_status(tool, success, output)

        # Sauvegarde dans le rapport
        status_text = "✅ Réussi" if success else "❌ Échec"
        report_lines.append(f"{tool} — {status_text}")
        if output:
            report_lines.append(f"--- Détails ---\n{output}\n")
        report_lines.append("")

        if not success:
            global_success = False

    if not global_success:
        summary = "🚫 Des problèmes ont été détectés. Corrigez-les avant de committer/pusher.\n"
        print(summary)
    else:
        summary = "🎉 Tout est propre ! Le code respecte les standards de qualité.\n"
        print(summary)

    # Ajouter un résumé clair à la fin du rapport
    report_lines.append("=" * 60)
    report_lines.append(summary)
    report_lines.append("=" * 60 + "\n")

    # ===========================
    # 💾 Sauvegarde du rapport
    # ===========================
    os.makedirs("tools", exist_ok=True)
    report_path = os.path.join("tools", ".last_analysis.log")

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
        print(f"📝 Rapport sauvegardé dans {report_path}")
    except Exception as e:
        print(f"⚠️ Impossible d’écrire le rapport d’analyse : {e}")

    # Code de sortie selon le résultat
    sys.exit(0 if global_success else 1)


if __name__ == "__main__":
    main()
