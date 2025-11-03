Excellent réflexe 👏 — un bon **README** est essentiel pour ton futur repo GitHub et pour la CI/CD qu’on va ajouter ensuite.

Voici une version **claire, professionnelle et prête à copier dans ton `README.md`**, adaptée à ton projet **Smart CV Generator (Python + FastAPI + PDF + IA)**.

---

# 🧠 Smart CV Generator

> Générateur de CV intelligent en Python, capable de produire des CV professionnels en PDF à partir d’un formulaire web.
> Le projet inclut une architecture extensible avec intégration d’analyse IA, de hooks Git, de notifications e-mail et d’automatisation CI/CD.

---

## 🚀 Lancer le projet localement

### 🧱 1. Cloner le dépôt

```bash
git clone https://github.com/<ton-username>/smart-cv-generator.git
cd smart-cv-generator
```

---

### 🧰 2. Créer et activer un environnement virtuel

#### Windows :

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux :

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 📦 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Si le fichier `requirements.txt` n’existe pas encore, tu peux le créer avec ce contenu minimal :

```txt
fastapi
uvicorn
jinja2
weasyprint
python-multipart
```

> 💡 Pour Windows, WeasyPrint requiert l’installation du runtime GTK.
> Télécharge-le ici :
> 🔗 [https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)
> Installe-le puis coche **“Add GTK to PATH”** avant de relancer le serveur.

---

### ⚙️ 4. Lancer le serveur local

```bash
uvicorn app.main:app --reload
```

Le serveur se lancera sur :
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

### 🧾 5. Générer un CV

1️⃣ Accède à [http://127.0.0.1:8000](http://127.0.0.1:8000)
2️⃣ Remplis le formulaire
3️⃣ Clique sur **“Générer mon CV PDF”**
4️⃣ Le fichier `.pdf` sera automatiquement téléchargé.

---

## 🧩 Arborescence du projet

```
smart-cv-generator/
│
├─ app/
│  ├─ main.py                # Backend FastAPI
│  ├─ templates/
│  │   ├─ form.html          # Formulaire utilisateur
│  │   └─ cv_template.html   # Template du CV (HTML/CSS dynamique)
│  └─ static/
│      ├─ style.css          # Style du formulaire
│      └─ cv_style.css       # Style du CV PDF
│
├─ requirements.txt
├─ .gitignore
└─ README.md
```

---

## 🧠 Fonctionnalités actuelles

✅ Génération de CV en PDF à partir d’un formulaire web
✅ Champs dynamiques (les sections vides ne s’affichent pas)
✅ Interface moderne et responsive (HTML + CSS)
✅ Backend Python/FastAPI performant
✅ Support multi-plateforme (Windows/Linux/macOS)

---

## 🚧 Prochaines étapes (plan de développement)

| Étape | Objectif                                                      |
| ----- | ------------------------------------------------------------- |
| 🔜 1  | Intégration d’analyse IA automatique des fichiers modifiés    |
| 🔜 2  | Hooks Git (pré-commit / pré-push) pour vérifier code et tests |
| 🔜 3  | Envoi automatique d’e-mails de notification                   |
| 🔜 4  | CI/CD GitHub Actions (exécution automatisée en ligne)         |
| 🔜 5  | Amélioration du design PDF et ajout du profil photo           |

---

## 🔐 Variables d’environnement (à venir)

Pour les fonctionnalités IA et email :

```
TYPY_API_KEY=ta_cle_api_ia
MAIL_SENDER=adresse@example.com
MAIL_APP_PASSWORD=motdepasse_app
```

> 📁 Ces valeurs doivent être placées dans un fichier `.env` (non versionné).

---

## 👨‍💻 Auteur

**Tamsès la pépite (ONDOA ONDOA IV Gabriella Tamar)**
🎓 Étudiante en Réseaux et Sécurité Informatique
💡 Passionnée par la cybersécurité et l’automatisation
📍 Cameroun
# Test CI - déclencher GitHub Actions
---


