#!/usr/bin/env python
"""Utilitaire en ligne de commande Django pour les tâches d'administration."""
import os
import sys


def main():
    """Exécute les tâches d'administration."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aabo.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. Vérifie qu'il est installé et "
            "disponible via la variable d'environnement PYTHONPATH. As-tu "
            "oublié d'activer un environnement virtuel ?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
