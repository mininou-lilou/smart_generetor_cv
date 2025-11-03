#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Envoi d'un rapport complet (lint + typage + diff Git + analyse IA)
via e-mail après un push, commit ou GitHub Actions.
Compatible avec :
  • Repository Secrets (GitHub)
  • Fichier .env local
  • Hooks Git (pre-commit / pre-push)
"""

import os
import io
import smtplib
import subprocess
import sys
from email.mime.text import MIMEText
from typing import Literal, Optional, List

# --- Forcer UTF-8 sur Windows ---
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# --- Chargement optionnel de .env ---
try:
    from dotenv import load_dotenv
    load_dotenv()  # Charge .env si présent
except ImportError:
    print("Warning: 'python-dotenv' non installé → .env ignoré.")

# --- Variables d'environnement ---
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
GEMINI_APP_PASSWORD = os.getenv("GEMINI_APP_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Vérification e-mail ---
SEND_EMAIL_ENABLED = bool(SENDER_EMAIL and GEMINI_APP_PASSWORD)
if not SEND_EMAIL_ENABLED:
    print("Warning: E-mail désactivé (SENDER_EMAIL ou GEMINI_APP_PASSWORD manquants).")


# ====================================================
# Fonctions utilitaires
# ====================================================

def get_git_user_email() -> Optional[str]:
    """Récupère l'email Git de l'utilisateur (git config user.email)."""
    try:
        result = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True, text=True, check=False, encoding="utf-8"
        )
        email = result.stdout.strip()
        return email if email else None
    except Exception as e:
        print(f"Warning: Impossible de lire git config user.email : {e}")
        return None


def read_analysis_report() -> str:
    """Lit le rapport d'analyse généré par analyze_code.py."""
    path = "tools/.last_analysis.log"
    if not os.path.exists(path):
        return "Warning: Aucun rapport d’analyse trouvé (tools/.last_analysis.log)."
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Warning: Erreur lecture rapport : {e}"


def get_git_diff() -> str:
    """Récupère le diff des changements (staged ou dernier commit)."""
    try:
        # Priorité : changements staged
        result = subprocess.run(
            ["git", "diff", "--cached"], capture_output=True, text=True,
            check=False, encoding="utf-8"
        )
        if result.stdout.strip():
            return result.stdout

        # Sinon : diff du dernier commit
        result = subprocess.run(
            ["git", "diff", "HEAD~1"], capture_output=True, text=True,
            check=False, encoding="utf-8"
        )
        return result.stdout.strip() or "Aucun changement détecté."
    except Exception as e:
        return f"Warning: Erreur git diff : {e}"


def get_changed_files() -> List[str]:
    """Liste des fichiers modifiés dans le dernier commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            capture_output=True, text=True, check=False, encoding="utf-8"
        )
        return [f for f in result.stdout.splitlines() if f.strip()]
    except Exception:
        return []


def ask_gemini_for_analysis(report: str, diff: str, changed_files: List[str]) -> str:
    """Analyse via Gemini API → retourne du HTML stylé."""
    if not GEMINI_API_KEY:
        return "<p style='color: orange;'>Warning: GEMINI_API_KEY manquante → IA désactivée.</p>"

    try:
        import requests  # Import local → évite erreur si non utilisé

        prompt = f"""
Tu es un expert en revue de code Python. Génère un **rapport HTML complet** :

**Fichiers modifiés** : {', '.join(changed_files) or 'Aucun'}
**Diff Git** :
{diff[:3000]}
**Rapport d’analyse** :
{report}

**Style** :
- Titre principal en <h1> (vert si succès, rouge si échec)
- Fond #f9f9fb
- Boîte blanche centrée avec ombre
- Code en <pre><code>
- Suggestions en bleu
- Ton professionnel, clair, actionnable
"""

        url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"
        headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        text = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        html = text.replace("```html", "").replace("```", "").strip()
        return html or "<p>Warning: Réponse vide de l’IA.</p>"

    except ImportError:
        return "<p style='color: red;'>Error: 'requests' non installé. pip install requests</p>"
    except Exception as e:
        return f"<p style='color: red;'>Warning: Erreur Gemini API : {e}</p>"


def send_email(subject: str, html_body: str, status: Literal["success", "failure"]) -> None:
    """Envoie un e-mail HTML via Gmail."""
    if not SEND_EMAIL_ENABLED:
        print("Warning: E-mail désactivé.")
        return

    recipient = get_git_user_email() or SENDER_EMAIL
    if not recipient:
        print("Warning: Aucun destinataire → e-mail ignoré.")
        return

    msg = MIMEText(html_body, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, GEMINI_APP_PASSWORD)
            server.send_message(msg)
        print(f"Success: E-mail envoyé à {recipient}")
    except Exception as e:
        print(f"Warning: Échec envoi e-mail : {e}")


# ====================================================
# Exécution principale
# ====================================================

def main() -> None:
    # Récupère les arguments
    status = sys.argv[1] if len(sys.argv) > 1 else "success"
    origin = sys.argv[2] if len(sys.argv) > 2 else "manual"

    print(f"Préparation du rapport ({origin})...")

    report = read_analysis_report()
    diff = get_git_diff()
    files = get_changed_files()

    html_analysis = ask_gemini_for_analysis(report, diff, files)

    subject = (
        "Success: Smart CV Generator — Code validé"
        if status == "success"
        else "Failure: Smart CV Generator — Erreurs détectées"
    )

    send_email(subject, html_analysis, status)


if __name__ == "__main__":
    main()