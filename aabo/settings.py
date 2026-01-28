"""
Paramètres Django pour le projet aabo.
Version optimisée pour Render.com (gratuit)
"""

import os
from pathlib import Path

# Construction des chemins
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================
# 🔐 SÉCURITÉ - Variables d'environnement
# ============================================

# SECRET_KEY depuis Render (OBLIGATOIRE)
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 
    'django-dev-key-only-change-in-production'  # Dev seulement
)

# DEBUG depuis Render
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ============================================
# 🌍 HÔTES AUTORISÉS - Configuration Render
# ============================================

ALLOWED_HOSTS = []

# 1. URL fournie par Render (automatique)
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# 2. Variable manuelle pour toutes les URLs Render
if not DEBUG:
    ALLOWED_HOSTS.extend([
        '.onrender.com',           # Toutes les apps Render
        'localhost',
        '127.0.0.1',
    ])

# ============================================
# 📁 DOSSIER DONNÉES (adapté Render)
# ============================================

# Sur Render, utiliser BASE_DIR directement
DOSSIER_DONNEES = BASE_DIR / 'data'
DOSSIER_DONNEES.mkdir(parents=True, exist_ok=True)

# ============================================
# APPLICATIONS
# ============================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',  # Gardé mais sera WSGI sur Render gratuit
    'immobilier.apps.ConfigurationImmobilier',
]

# ============================================
# MIDDLEWARE
# ============================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ESSENTIEL pour static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================================
# TEMPLATES & URLs
# ============================================

ROOT_URLCONF = 'aabo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ============================================
# 🚨 IMPORTANT : WSGI vs ASGI sur Render gratuit
# ============================================

# Render gratuit supporte SEULEMENT WSGI
WSGI_APPLICATION = 'aabo.wsgi.application'

# Channels/ASGI désactivé pour compatibilité Render gratuit
# ASGI_APPLICATION = 'aabo.routage.application'  # À COMMENTER

# CHANNEL_LAYERS = {  # À COMMENTER
#     'default': {
#         'BACKEND': 'channels.layers.InMemoryChannelLayer',
#     }
# }

# ============================================
# BASE DE DONNÉES (SQLite pour gratuit)
# ============================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DOSSIER_DONNEES / 'db.sqlite3',
    }
}

# ============================================
# VALIDATION MOTS DE PASSE
# ============================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================
# INTERNATIONALISATION
# ============================================

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# ============================================
# AUTHENTIFICATION
# ============================================

LOGIN_URL = '/connexion/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ============================================
# ⚡ FICHIERS STATIQUES (CONFIGURATION RENDER)
# ============================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # ESSENTIEL pour collectstatic

# WhiteNoise configuration (pour servir les fichiers)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================
# 🖼️ FICHIERS MÉDIA (ATTENTION RENDER gratuit)
# ============================================

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ⚠️ ATTENTION : Les fichiers uploadés dans /media seront PERDUS
# à chaque redéploiement sur Render (gratuit)

# ============================================
# MODÈLE UTILISATEUR
# ============================================

AUTH_USER_MODEL = 'immobilier.Utilisateur'

# ============================================
# 🛡️ SÉCURITÉ PRODUCTION
# ============================================

if not DEBUG:
    # HTTPS obligatoire sur Render
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # Cookies sécurisés
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # Headers sécurité
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Protection XSS
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    
    # Referrer Policy
    SECURE_REFERRER_POLICY = 'same-origin'