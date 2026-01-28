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

## Déploiement en production

### Prérequis

L'application est prête pour le déploiement sur les plateformes suivantes :
- **Heroku**
- **Railway**
- **Render**
- **Vercel** (avec adaptations)
- Tout service supportant Python/Django

### Configuration des variables d'environnement

Copier `.env.example` en `.env` et configurer :

```bash
SECRET_KEY=votre-cle-secrete-unique-et-aleatoire
DEBUG=False
ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
DATABASE_URL=postgres://user:password@host:port/dbname  # Optionnel
```

**Générer une SECRET_KEY sécurisée :**

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Déploiement sur Heroku

1. Installer Heroku CLI et se connecter :

```bash
heroku login
```

2. Créer une application :

```bash
heroku create nom-de-votre-app
```

3. Ajouter PostgreSQL :

```bash
heroku addons:create heroku-postgresql:mini
```

4. Configurer les variables d'environnement :

```bash
heroku config:set SECRET_KEY="votre-cle-secrete"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="nom-de-votre-app.herokuapp.com"
```

5. Déployer :

```bash
git push heroku main
```

6. Exécuter les migrations :

```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Déploiement sur Railway

1. Connecter votre dépôt GitHub à Railway
2. Ajouter une base de données PostgreSQL depuis le dashboard
3. Configurer les variables d'environnement dans Settings :
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=votre-domaine.railway.app`
4. Railway détectera automatiquement le `Procfile` et `runtime.txt`
5. Exécuter les migrations via le terminal Railway :

```bash
python manage.py migrate
python manage.py createsuperuser
```

### Déploiement sur Render

1. Créer un nouveau Web Service sur Render
2. Connecter votre dépôt GitHub
3. Configurer :
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn aabo.wsgi:application`
4. Ajouter une base de données PostgreSQL
5. Configurer les variables d'environnement :
   - `SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=votre-app.onrender.com`
   - `DATABASE_URL` (automatique si PostgreSQL ajouté)
6. Déployer et exécuter les migrations

### Collecte des fichiers statiques

Avant le premier déploiement, collecter les fichiers statiques :

```bash
python manage.py collectstatic --noinput
```

### Notes importantes

- **WhiteNoise** est configuré pour servir les fichiers statiques en production
- **Gunicorn** est utilisé comme serveur WSGI
- **Daphne** peut être utilisé pour les WebSockets (Channels)
- La base de données SQLite est utilisée en développement, PostgreSQL recommandé en production
- Les fichiers médias (uploads) nécessitent un stockage externe (S3, Cloudinary) en production

### Sécurité

En production, assurez-vous de :
- Utiliser une `SECRET_KEY` unique et sécurisée
- Définir `DEBUG=False`
- Configurer correctement `ALLOWED_HOSTS`
- Utiliser HTTPS (automatique sur Heroku/Railway/Render)
- Configurer un stockage externe pour les fichiers médias
