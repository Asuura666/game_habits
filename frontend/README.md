# HabitQuest Frontend

Frontend Next.js pour l'application de gamification d'habitudes HabitQuest.

## 🚀 Technologies

- **Next.js 14** - Framework React avec App Router
- **TypeScript** - Typage statique
- **Tailwind CSS** - Styling utility-first
- **Framer Motion** - Animations fluides
- **Zustand** - State management
- **React Query** - Data fetching & caching
- **Lucide React** - Icônes

## 📁 Structure du projet

```
src/
├── app/                    # App Router (Next.js 14)
│   ├── layout.tsx          # Root layout avec providers
│   ├── page.tsx            # Landing page
│   ├── globals.css         # Styles globaux + Tailwind
│   ├── (auth)/             # Routes authentification
│   │   ├── login/          # Page de connexion
│   │   └── register/       # Page d'inscription
│   └── (app)/              # Routes protégées (avec sidebar)
│       ├── layout.tsx      # Layout avec Sidebar + Header
│       ├── dashboard/      # Dashboard principal
│       ├── habits/         # Gestion des habitudes
│       ├── tasks/          # Gestion des tâches
│       ├── character/      # Profil du personnage
│       ├── shop/           # Boutique
│       ├── combat/         # Arène de combat
│       ├── friends/        # Amis
│       ├── leaderboard/    # Classement
│       └── stats/          # Statistiques
├── components/
│   ├── ui/                 # Composants UI réutilisables
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── ProgressBar.tsx
│   │   └── Badge.tsx
│   ├── layout/             # Composants de mise en page
│   │   ├── Sidebar.tsx
│   │   └── Header.tsx
│   └── habits/             # Composants métier habitudes
│       ├── HabitCard.tsx
│       └── HabitList.tsx
├── lib/
│   ├── api.ts              # Client API
│   └── utils.ts            # Fonctions utilitaires
├── stores/
│   └── authStore.ts        # Store Zustand pour l'auth
└── types/
    └── index.ts            # Types TypeScript
```

## 🛠️ Installation

```bash
# Installer les dépendances
npm install

# Copier les variables d'environnement
cp .env.example .env.local

# Lancer en développement
npm run dev
```

## 🐳 Docker

```bash
# Build l'image
docker build -t habitquest-frontend .

# Lancer le conteneur
docker run -p 3000:3000 habitquest-frontend
```

## 📝 Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `NEXT_PUBLIC_API_URL` | URL de l'API backend | `http://localhost:8000/api` |

## ✨ Fonctionnalités

### Pages

- **Landing** - Page d'accueil avec présentation
- **Login/Register** - Authentification avec validation
- **Dashboard** - Vue d'ensemble avec stats et habitudes du jour
- **Habits** - Liste, création et complétion d'habitudes
- **Tasks** - Todo-list gamifiée avec priorités
- **Character** - Profil RPG avec stats et équipement
- **Shop** - Boutique pour dépenser l'or
- **Combat** - Système de combat tour par tour
- **Friends** - Gestion des amis et demandes
- **Leaderboard** - Classement par XP et streak
- **Stats** - Graphiques et analyse de progression

### Composants UI

- Boutons avec variants et états loading
- Cards avec animations hover
- Inputs avec validation et icônes
- Barres de progression animées (XP, HP, Mana)
- Badges colorés par type

### Thème

- Mode sombre par défaut
- Palette de couleurs :
  - Primary (bleu) - Actions principales
  - Accent (violet) - Éléments spéciaux
  - Game colors - Gold, XP (vert), HP (rouge), Mana (bleu)

## 🎮 Gamification

- **XP** - Gagné en complétant habitudes/tâches
- **Or** - Monnaie pour acheter en boutique
- **Niveaux** - Progression basée sur l'XP
- **Streaks** - Séries de jours consécutifs
- **Combat** - Utilise la productivité pour combattre des monstres
- **Équipement** - Items avec stats et raretés

## 📄 License

MIT
