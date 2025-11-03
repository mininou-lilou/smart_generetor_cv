# app/utils.py
import requests
from datetime import datetime

def send_notification(message):
    url = "https://api.example.com/notify"
    data = {"msg": message}
    requests.post(url, json=data)  # ERREUR : pas de try/except

def unused_function():
    x = 42
    return x + 1  # ERREUR : fonction jamais utilisée

class BadClass:
    def __init__(self):
        self.name = "test"
    
    def get_name(self) -> int:  # ERREUR MYPY : retourne str, pas int
        return self.name
