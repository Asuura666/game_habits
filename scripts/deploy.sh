#!/bin/bash
# Habit Tracker - Deployment Script
set -e

echo "🚀 Déploiement Habit Tracker..."

# Configuration
PROJECT_DIR="/home/debian/habit-tracker"
cd $PROJECT_DIR

# Pull latest code
echo "📥 Pull du code..."
git pull origin main

# Build images
echo "📦 Build des images Docker..."
docker compose build --no-cache

# Run migrations
echo "🔄 Migrations base de données..."
docker compose run --rm backend alembic upgrade head

# Restart services
echo "🔄 Redémarrage des services..."
docker compose down
docker compose up -d

# Wait for services
echo "⏳ Attente du démarrage..."
sleep 10

# Health check
echo "🏥 Health check..."
if curl -sf https://habit.apps.ilanewep.cloud/api/health > /dev/null; then
    echo "✅ Déploiement terminé avec succès !"
else
    echo "❌ Health check échoué !"
    docker compose logs backend --tail=50
    exit 1
fi

# Show status
docker compose ps
