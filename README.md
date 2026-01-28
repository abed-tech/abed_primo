# Aabo

Application Django (mobile-first) pour la publication de biens immobiliers sous forme de vidéos verticales et la messagerie.

## Prérequis

- Python 3 (recommandé)

## Installation (Windows)

### 1) Créer l’environnement virtuel

Depuis la racine du projet (là où se trouve `manage.py`) :

```bat
python -m venv .venv
```

### 2) Activer l’environnement virtuel

- CMD :

```bat
.\.venv\Scripts\activate.bat
```

- PowerShell :

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloque l’exécution, exécuter une seule fois :

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 3) Installer les dépendances

```bat
pip install -r requirements.txt
```

## Lancer l’application

### 1) Migrations

```bat
python manage.py migrate
```

### 2) Démarrer le serveur

```bat
python manage.py runserver
```

Puis ouvrir :

- `http://127.0.0.1:8000/`

## Administration

Créer un superutilisateur :

```bat
python manage.py createsuperuser
```

Puis accéder à :

- `http://127.0.0.1:8000/admin/`
