"""
Configuration ASGI pour le projet aabo.

Expose l'appelable ASGI sous forme de variable de module nommée ``application``.

Documentation :
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aabo.settings')

from .routage import application