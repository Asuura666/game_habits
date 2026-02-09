#!/bin/bash
# Habit Tracker - Database Backup Script
set -e

# Configuration
BACKUP_DIR="/home/debian/backups/habit-tracker"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql.gz"
CONTAINER_NAME="habit-postgres"

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

echo "💾 Backup de la base de données..."

# Dump database
docker exec $CONTAINER_NAME pg_dump -U ${DB_USER:-habit_user} ${DB_NAME:-habit_tracker} | gzip > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Backup créé: $BACKUP_FILE"
    ls -lh $BACKUP_FILE
else
    echo "❌ Erreur lors du backup"
    exit 1
fi

# Rotation: keep last 7 backups
echo "🧹 Rotation des backups (conservation des 7 derniers)..."
ls -t $BACKUP_DIR/backup_*.sql.gz | tail -n +8 | xargs -r rm -v

echo "📊 Backups disponibles:"
ls -lh $BACKUP_DIR/backup_*.sql.gz | tail -5
