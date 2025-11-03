#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Envoi automatique d'e-mails suite à l'analyse du code.
Utilise les Repository Secrets GitHub ou les variables d'environnement locales.
"""
import os
import smtplib
import subprocess
import sys
from email.mime.text import MIMEText
from typing import Literal, Optional
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
GEMINI_APP_PASSWORD = os.getenv("GEMINI_APP_PASSWORD")

if not SENDER_EMAIL or not GEMINI_APP_PASSWORD:
    print("Les variables SENDER_EMAIL et GEMINI_APP_PASSWORD ne sont pas définies.")
    print("Configure-les dans tes Secrets GitHub ou ton fichier .env.")
    sys.exit(1)


def get_git_user_email() -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        email = result.stdout.strip()
        if not email:
            print("Aucune adresse e-mail configurée dans Git.")
            return None
        return email
    except Exception as e:
        print(f"Impossible de récupérer l'e-mail Git : {e}")
        return None


def send_email(subject: str, message: str, status: Literal["success", "failure"]) -> None:
    to_email = get_git_user_email()
    if not to_email:
        print("Aucun e-mail de destination. L'envoi du mail est annulé.")
        return
    try:
        msg = MIMEText(message, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        print(f"Envoi du mail à {to_email} ...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, GEMINI_APP_PASSWORD)
            server.send_message(msg)
        print("Mail envoyé avec succès." if status == "success" else "Mail d’échec envoyé.")
    except Exception as e:
        print(f"Erreur lors de l’envoi du mail : {e}")


if __name__ == "__main__":
    send_email(
        subject="[Smart CV Generator] Test d'envoi d'email automatique",
        message="Ceci est un test depuis le hook Git.",
        status="success",
    )