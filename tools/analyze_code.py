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
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
os.environ["PYTHONIOENCODING"] = "utf-8"


# --- Chargement optionnel de .env ---
try:
    from dotenv import load_dotenv
    load_dotenv()
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
            capture_output=True, text=True, check=False, encoding="utf-8", errors="replace"
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
        result = subprocess.run(
            ["git", "diff", "--cached"], capture_output=True, text=True,
            check=False, encoding="utf-8", errors="replace"
        )
        if result.stdout.strip():
            return result.stdout
        result = subprocess.run(
            ["git", "diff", "HEAD~1"], capture_output=True, text=True,
            check=False, encoding="utf-8", errors="replace"
        )
        return result.stdout.strip() or "Aucun changement détecté."
    except Exception as e:
        return f"Warning: Erreur git diff : {e}"


def get_changed_files() -> List[str]:
    """Liste des fichiers modifiés dans le dernier commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            capture_output=True, text=True, check=False, encoding="utf-8", errors="replace"
        )
        return [f for f in result.stdout.splitlines() if f.strip()]
    except Exception:
        return []


def ask_gemini_for_analysis(report: str, diff: str, changed_files: List[str]) -> str:
    """Analyse via Gemini API → retourne du HTML stylé (modèle 2.5 Flash prioritaire)."""
    if not GEMINI_API_KEY:
        return "<p style='color: orange;'>Warning: GEMINI_API_KEY manquante → IA désactivée.</p>"

    MODELS = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash"
    ]

    for model in MODELS:
        try:
            import requests  # Import local
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

            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            headers = {"Content-Type": "application/json"}
            params = {"key": GEMINI_API_KEY}
            payload = {"contents": [{"parts": [{"text": prompt}]}]}

            response = requests.post(url, headers=headers, params=params, json=payload, timeout=60)
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

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Warning: Modèle '{model}' non trouvé → essai suivant...")
                continue
            else:
                raise
        except Exception as e:
            print(f"Warning: Erreur avec '{model}' : {e}")
            continue

    return "<p style='color: red;'>Erreur: Modèles Gemini KO. Vérifie ta clé sur <a href='https://aistudio.google.com/app/apikey'>AI Studio</a>.</p>"


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