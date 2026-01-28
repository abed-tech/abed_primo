#!/usr/bin/env bash
# Script de build pour Render.com
# Place ce fichier à la racine du projet

set -o errexit  # Arrêter en cas d'erreur

echo "========================================"
echo "🚀 DÉPLOIEMENT AABO SUR RENDER"
echo "========================================"

# 1. Aller dans le dossier backend
cd backend

echo "📦 1. Installation des dépendances Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🗄️  2. Migration de la base de données..."
python manage.py migrate --noinput

echo "📁 3. Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear

echo "👤 4. Création du superuser admin (si nécessaire)..."
# Crée un superuser par défaut (email: admin@aabo.com, password: admin123)
echo "from django.contrib.auth import get_user_model; User = get_user_model(); \
User.objects.create_superuser('admin', 'admin@aabo.com', 'admin123') \
if not User.objects.filter(username='admin').exists() else print('Superuser existe déjà')" \
| python manage.py shell

echo "✅ BUILD TERMINÉ AVEC SUCCÈS !"
echo "👉 L'application sera disponible à : https://abed_primo-4.onrender.com"
echo "👉 Admin : http://abed_primo-4.onrender.com/admin"
echo "   Identifiants : admin / admin123"