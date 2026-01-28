# Configuration pour Render.com
# WSGI seulement (compatible avec le plan gratuit)

web: cd backend && gunicorn aabo.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --access-logfile -