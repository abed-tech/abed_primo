"""
Paramètres Django pour le projet aabo.

Généré par 'django-admin startproject' avec Django 6.0.

Pour plus d'informations sur ce fichier :
https://docs.djangoproject.com/en/6.0/topics/settings/

Pour la liste complète des paramètres :
https://docs.djangoproject.com/en/6.0/ref/settings/
"""

import os
from pathlib import Path

# Construction des chemins du projet : BASE_DIR / 'sous_dossier'.
BASE_DIR = Path(__file__).resolve().parent.parent

DOSSIER_DONNEES = Path(os.environ.get('LOCALAPPDATA', str(BASE_DIR))) / 'aabo'
DOSSIER_DONNEES.mkdir(parents=True, exist_ok=True)


# Paramètres de développement (non adaptés à la production)
# Voir https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# AVERTISSEMENT : conserve la clé secrète de production hors du code source.
SECRET_KEY = 'django-insecure-(8@q64x8wo%65ghx#ct!k@2dqg(-2_%5z_h_=fvjdvw0(69a^z'

# AVERTISSEMENT : ne pas activer DEBUG en production.
DEBUG = True

ALLOWED_HOSTS = []


# Définition des applications

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'immobilier.apps.ConfigurationImmobilier',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

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

WSGI_APPLICATION = 'aabo.wsgi.application'

ASGI_APPLICATION = 'aabo.routage.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}


# Base de données
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DOSSIER_DONNEES / 'db.sqlite3',
    }
}


# Validation des mots de passe
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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


# Internationalisation
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_TZ = True

LOGIN_URL = '/connexion/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# Fichiers statiques (CSS, JavaScript, images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR/ 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Fichiers médias (vidéos, photos)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Modèle utilisateur personnalisé
AUTH_USER_MODEL = 'immobilier.Utilisateur'
