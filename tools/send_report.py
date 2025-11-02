#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📬 Envoi d'un rapport complet (lint + typage + diff Git + analyse IA)
via e-mail après un push ou un commit.
Compatible avec les Repository Secrets GitHub et un .env local.
"""

import os
import io
import smtplib
import subprocess
from email.mime.text import MIMEText
from typing import Literal, Optional, List
from dotenv import load_dotenv
import requests
import json
import sys

# ✅ Forcer l'encodage UTF-8 sous Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# 🔐 Charger les secrets depuis .env ou GitHub
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
GEMINI_APP_PASSWORD = os.getenv("GEMINI_APP_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not SENDER_EMAIL or not GEMINI_APP_PASSWORD:
    print("⚠️ Variables manquantes : SENDER_EMAIL ou GEMINI_APP_PASSWORD non définies.")
    sys.exit(0)  # On ne bloque pas le commit, on envoie juste un avertissement


# ====================================================
# 🔧 Fonctions utilitaires
# ====================================================

def get_git_user_email() -> Optional[str]:
    """Récupère l'adresse e-mail configurée dans Git localement."""
    try:
        result = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True, text=True, encoding="utf-8"
        )
        email = result.stdout.strip()
        return email or None
    except Exception as e:
        print(f"⚠️ Erreur récupération e-mail Git : {e}")
        return None


def read_analysis_report() -> str:
    """Lit le dernier rapport généré par analyze_code.py s’il existe."""
    report_path = "tools/.last_analysis.log"
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            return f.read()
    return "⚠️ Aucun rapport d’analyse disponible."


def get_git_diff() -> str:
    """Retourne le diff Git des fichiers modifiés."""
    try:
        diff = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, encoding="utf-8")
        if not diff.stdout.strip():
            diff = subprocess.run(["git", "diff", "HEAD~1"], capture_output=True, text=True, encoding="utf-8")
        return diff.stdout if diff.stdout.strip() else "Aucun diff disponible."
    except Exception:
        return "⚠️ Impossible de générer le diff Git."


def get_changed_files() -> List[str]:
    """Liste les fichiers modifiés depuis le dernier commit."""
    try:
        res = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            capture_output=True, text=True, encoding="utf-8"
        )
        return [f for f in res.stdout.splitlines() if f.strip()]
    except Exception:
        return []


def ask_gemini_for_analysis(report: str, diff: str, changed_files: list[str]) -> str:
    """Appelle Gemini pour générer une version HTML du rapport."""
    if not GEMINI_API_KEY:
        return "<p>⚠️ Clé GEMINI_API_KEY non configurée. Analyse IA désactivée.</p>"

    try:
        prompt = f"""
Tu es un assistant expert en revue de code Python.
Analyse les résultats suivants et écris un e-mail HTML structuré, clair et professionnel :

--- Résultats analyse ---
{report}

--- Fichiers modifiés ---
{', '.join(changed_files)}

--- Diff Git ---
{diff[:2000]}

Style HTML :
- fond gris clair (#f4f4f9)
- boîte blanche centrale avec ombre
- titres colorés (vert si succès, rouge si erreurs)
- suggestions IA bleues
- texte lisible, clair, professionnel
        """

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": GEMINI_API_KEY,
        }

        body = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        # ✅ Nouveau endpoint + modèle correct (Gemini 1.5 Flash)
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent",
            headers=headers,
            data=json.dumps(body),
            timeout=60
        )

        if response.status_code != 200:
            return f"<p>⚠️ Erreur API Gemini : {response.text}</p>"

        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return "<p>⚠️ Aucune réponse reçue de l'IA.</p>"

        html_content = candidates[0]["content"]["parts"][0].get("text", "")
        return html_content.replace("```html", "").replace("```", "").strip()

    except Exception as e:
        return f"<p>⚠️ Erreur Gemini : {e}</p>"


def send_email(subject: str, html_body: str, status: Literal["success", "failure"]) -> None:
    """Envoie un e-mail HTML avec les résultats de l’analyse."""
    recipient = get_git_user_email() or SENDER_EMAIL
    if not recipient:
        print("❌ Aucun destinataire valide trouvé pour l’envoi du mail.")
        return

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, GEMINI_APP_PASSWORD)
            server.send_message(msg)
        print(f"📧 Rapport envoyé à {recipient}")
    except Exception as e:
        print(f"⚠️ Erreur lors de l’envoi du mail : {e}")


# ====================================================
# 🚀 Exécution principale
# ====================================================

def main() -> None:
    """Envoi automatique après commit/push"""
    status = sys.argv[1] if len(sys.argv) > 1 else "success"
    origin = sys.argv[2] if len(sys.argv) > 2 else "manual"

    print(f"📨 Préparation de l’envoi du rapport ({origin})...")

    report = read_analysis_report()
    diff = get_git_diff()
    files = get_changed_files()

    success = status == "success"

    print("🤖 Génération du résumé IA...")
    html_content = ask_gemini_for_analysis(report, diff, files)

    subject = (
        "✅ Smart CV Generator — Code validé"
        if success
        else "❌ Smart CV Generator — Erreurs détectées"
    )

    send_email(subject, html_content, status)


if __name__ == "__main__":
    main()
