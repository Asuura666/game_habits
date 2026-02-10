# 🎮 HabitQuest

<div align="center">

![HabitQuest Banner](https://img.shields.io/badge/HabitQuest-Gamify%20Your%20Life-blueviolet?style=for-the-badge&logo=gamepad&logoColor=white)

[![Live Demo](https://img.shields.io/badge/🌐%20Live%20Demo-habit.apps.ilanewep.cloud-success?style=for-the-badge)](https://habit.apps.ilanewep.cloud)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)

**Transformez vos habitudes quotidiennes en quêtes épiques 🗡️**

[Demo](https://habit.apps.ilanewep.cloud) • [Documentation](#-documentation) • [Installation](#-installation)

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎯 Habit Tracking
- Créez des habitudes quotidiennes, hebdomadaires ou personnalisées
- Suivez vos streaks et progressions
- Recevez des rappels intelligents

### ⚔️ Système RPG
- Gagnez de l'XP en complétant vos habitudes
- Montez de niveau et débloquez des récompenses
- Personnalisez votre avatar avec des équipements

</td>
<td width="50%">

### 📊 Statistiques
- Tableaux de bord détaillés
- Graphiques de progression
- Historique complet des activités

### 🏆 Gamification
- Système de badges et achievements
- Classements entre amis
- Combats PvP basés sur la productivité

</td>
</tr>
</table>

---

## 🖼️ Screenshots

<div align="center">
<table>
<tr>
<td align="center"><b>🏠 Landing Page</b></td>
<td align="center"><b>📱 Dashboard</b></td>
</tr>
<tr>
<td><img src="docs/screenshots/landing.png" alt="Landing" width="400"/></td>
<td><img src="docs/screenshots/dashboard.png" alt="Dashboard" width="400"/></td>
</tr>
<tr>
<td align="center"><b>👤 Character</b></td>
<td align="center"><b>📈 Stats</b></td>
</tr>
<tr>
<td><img src="docs/screenshots/character.png" alt="Character" width="400"/></td>
<td><img src="docs/screenshots/stats.png" alt="Stats" width="400"/></td>
</tr>
</table>
</div>

---

## 🛠️ Tech Stack

<table>
<tr>
<td align="center" width="25%">

**Frontend**

![Next.js](https://img.shields.io/badge/-Next.js%2014-black?style=flat-square&logo=next.js)
![React](https://img.shields.io/badge/-React%2018-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/-TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Tailwind](https://img.shields.io/badge/-Tailwind%20CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)

</td>
<td align="center" width="25%">

**Backend**

![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/-Python%203.11-3776AB?style=flat-square&logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/-SQLAlchemy-red?style=flat-square)
![Pydantic](https://img.shields.io/badge/-Pydantic%20V2-E92063?style=flat-square)

</td>
<td align="center" width="25%">

**Database**

![PostgreSQL](https://img.shields.io/badge/-PostgreSQL%2016-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/-Redis-DC382D?style=flat-square&logo=redis&logoColor=white)

</td>
<td align="center" width="25%">

**DevOps**

![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/-Nginx-009639?style=flat-square&logo=nginx&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/-GitHub%20Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)

</td>
</tr>
</table>

---

## 🚀 Installation

### Prérequis

- Docker & Docker Compose
- Node.js 20+ (pour le développement)
- Python 3.11+ (pour le développement)

### Quick Start avec Docker

```bash
# Cloner le repo
git clone https://github.com/Asuura666/game_habits.git
cd game_habits

# Copier les variables d'environnement
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Lancer avec Docker
docker compose up -d

# L'app est disponible sur http://localhost:3000
```

### Développement Local

<details>
<summary><b>Backend (FastAPI)</b></summary>

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer les migrations
alembic upgrade head

# Démarrer le serveur
uvicorn app.main:app --reload --port 8000
```

</details>

<details>
<summary><b>Frontend (Next.js)</b></summary>

```bash
cd frontend

# Installer les dépendances
npm install --legacy-peer-deps

# Démarrer en mode développement
npm run dev
```

</details>

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [📋 Cahier des Charges](docs/cdc-habit-tracker.md) | Spécifications complètes du projet |
| [🔧 Documentation Technique](docs/TECHNICAL.md) | Architecture, API, déploiement |
| [📚 Documentation Fonctionnelle](docs/FUNCTIONAL.md) | Guide utilisateur, fonctionnalités |

### API Endpoints

```
🔐 Auth
POST   /api/auth/register     # Inscription
POST   /api/auth/login        # Connexion
GET    /api/auth/me           # Profil utilisateur

📋 Habits
GET    /api/habits            # Liste des habitudes
POST   /api/habits            # Créer une habitude
PATCH  /api/habits/:id        # Modifier
DELETE /api/habits/:id        # Supprimer

✅ Completions
POST   /api/completions       # Marquer comme complété
GET    /api/completions       # Historique

👤 Character
GET    /api/characters/me     # Mon personnage
PATCH  /api/characters/me     # Modifier

📊 Stats
GET    /api/stats/overview    # Vue d'ensemble
GET    /api/stats/streaks     # Streaks actifs
```

---

## 🧪 Tests

```bash
# Backend tests (20 tests)
cd backend && pytest -v

# Frontend tests (50 tests)
cd frontend && npm test
```

**Coverage**: 70 tests ✅

---

## 🗺️ Roadmap

- [x] 🔐 Authentification JWT
- [x] 📋 CRUD Habitudes & Tâches
- [x] ⭐ Système XP & Niveaux
- [x] 👤 Personnages personnalisables
- [x] 📊 Statistiques & Dashboard
- [ ] ⚔️ Combats PvP
- [ ] 🏪 Boutique d'équipements
- [ ] 📱 App mobile (React Native)
- [ ] 🤖 Évaluation IA des tâches

---

## 👥 Contributeurs

<a href="https://github.com/Asuura666">
  <img src="https://avatars.githubusercontent.com/u/66923556?v=4" width="60" style="border-radius: 50%"/>
</a>

---

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

<div align="center">

**Fait avec ❤️ et beaucoup de ☕**

[![Star](https://img.shields.io/github/stars/Asuura666/game_habits?style=social)](https://github.com/Asuura666/game_habits)

</div>
