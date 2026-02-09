# 🎯 Habit Tracker Gamifié

Application de suivi d'habitudes gamifiée avec personnage RPG évolutif, système de tâches évaluées par IA, combat PvP entre amis, et statistiques avancées.

## 🚀 Stack Technique

- **Backend**: FastAPI + Python 3.12 + SQLAlchemy 2.0
- **Frontend**: Next.js 14 + React 18 + Tailwind CSS
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Queue**: Celery
- **LLM**: Claude 3.5 Haiku (évaluation des tâches)
- **Infra**: Docker Compose + Traefik

## 📦 Installation

### Prérequis

- Docker & Docker Compose
- Git

### Setup

```bash
# Clone
git clone https://github.com/Asuura666/habit-tracker.git
cd habit-tracker

# Configuration
cp .env.example .env
# Éditer .env avec vos valeurs

# Lancer
docker compose up -d

# Migrations
docker compose exec backend alembic upgrade head
```

## 🏗️ Structure

```
habit-tracker/
├── backend/           # API FastAPI
│   ├── app/
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── routers/   # API endpoints
│   │   ├── services/  # Business logic
│   │   └── tasks/     # Celery tasks
│   └── alembic/       # Migrations
├── frontend/          # Next.js app
├── scripts/           # Deploy & backup
└── docker-compose.yml
```

## 🔗 URLs

- **App**: https://habit.apps.ilanewep.cloud
- **API Docs**: https://habit.apps.ilanewep.cloud/api/docs
- **Monitoring**: https://monitoring.apps.ilanewep.cloud

## 📊 Features

- ✅ Habitudes récurrentes avec fréquences flexibles
- ✅ Tâches personnalisées évaluées par IA
- ✅ Système XP, niveaux (1-50), badges
- ✅ Personnage RPG (LPC sprites)
- ✅ Boutique d'équipements
- ✅ Combat PvP entre amis
- ✅ Leaderboard & statistiques

## 🔧 Commandes utiles

```bash
# Logs
docker compose logs -f backend

# Shell Python
docker compose exec backend python

# Migrations
docker compose exec backend alembic revision --autogenerate -m "description"
docker compose exec backend alembic upgrade head

# Backup
./scripts/backup.sh

# Deploy
./scripts/deploy.sh
```

## 📝 License

MIT

---

*Développé par Ilane avec 🦊 Shiro*
