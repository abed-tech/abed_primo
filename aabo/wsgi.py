"""
Configuration WSGI pour le projet aabo.

Expose l'appelable WSGI sous forme de variable de module nommée ``application``.

Documentation :
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement pour la production
load_dotenv()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aabo.settings')

application = get_wsgi_application()
