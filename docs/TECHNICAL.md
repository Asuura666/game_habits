# Documentation Technique - Habit Tracker

> **Version**: 1.0.0  
> **Dernière mise à jour**: 2026-02-09  
> **Stack**: Python 3.12 / FastAPI / PostgreSQL / Redis / Celery

---

## Table des Matières

1. [Architecture](#1-architecture)
2. [Base de données](#2-base-de-données)
3. [API REST](#3-api-rest)
4. [Authentification](#4-authentification)
5. [Services métier](#5-services-métier)
6. [Celery Tasks](#6-celery-tasks)
7. [Monitoring](#7-monitoring)
8. [Déploiement](#8-déploiement)

---

## 1. Architecture

### 1.1 Diagramme de l'Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND                                        │
│                        (Mobile / Web App)                                    │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TRAEFIK                                           │
│                     (Reverse Proxy + SSL)                                    │
│              habit.apps.ilanewep.cloud/api/*                                 │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HABIT-BACKEND                                        │
│                    (FastAPI + Uvicorn)                                       │
│                         Port: 8000                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         ROUTERS                                       │   │
│  │  /auth  /users  /habits  /tasks  /completions  /characters           │   │
│  │  /shop  /inventory  /combat  /friends  /leaderboard  /badges         │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        SERVICES                                       │   │
│  │  XPService  LevelService  StreakService  CombatService  LLMService   │   │
│  │  BadgeService  LeaderboardService                                     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└───────────┬──────────────────────┬──────────────────────┬───────────────────┘
            │                      │                      │
            ▼                      ▼                      ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────────────────┐
│    POSTGRESQL     │  │      REDIS        │  │     CELERY WORKERS            │
│   (PostgreSQL 16) │  │   (Redis 7)       │  │  ┌─────────────────────────┐  │
│                   │  │                   │  │  │    celery-worker        │  │
│  • users          │  │  • Session cache  │  │  │    (concurrency=2)      │  │
│  • habits         │  │  • Rate limiting  │  │  │                         │  │
│  • tasks          │  │  • Celery broker  │  │  │  • LLM Tasks            │  │
│  • completions    │  │  • Celery backend │  │  │  • Notification Tasks   │  │
│  • characters     │  │                   │  │  │  • Stats Tasks          │  │
│  • items          │  │                   │  │  │  • Cleanup Tasks        │  │
│  • combats        │  │                   │  │  └─────────────────────────┘  │
│  • badges         │  │                   │  │  ┌─────────────────────────┐  │
│  • notifications  │  │                   │  │  │    celery-beat          │  │
│  • daily_stats    │  │                   │  │  │    (scheduler)          │  │
│                   │  │                   │  │  └─────────────────────────┘  │
└───────────────────┘  └───────────────────┘  └───────────────────────────────┘
                                                            │
                                                            ▼
                                              ┌─────────────────────────────┐
                                              │   EXTERNAL SERVICES         │
                                              │                             │
                                              │  • Anthropic Claude API     │
                                              │  • OpenAI API               │
                                              │  • Google OAuth             │
                                              │  • Apple Sign In            │
                                              └─────────────────────────────┘
```

### 1.2 Stack Technique Détaillée

| Composant | Technologie | Version | Description |
|-----------|-------------|---------|-------------|
| **Runtime** | Python | 3.12 | Langage principal |
| **Framework** | FastAPI | latest | API REST async |
| **ORM** | SQLAlchemy | 2.0 | Async avec mapped columns |
| **Database** | PostgreSQL | 16-alpine | Base de données principale |
| **Cache/Queue** | Redis | 7-alpine | Cache + Broker Celery |
| **Task Queue** | Celery | latest | Tâches asynchrones |
| **Web Server** | Uvicorn | latest | ASGI server |
| **Auth** | python-jose | latest | JWT tokens |
| **Password** | passlib[bcrypt] | latest | Hashing bcrypt |
| **Validation** | Pydantic | 2.x | Schemas + Settings |
| **LLM** | Anthropic + OpenAI | latest | IA pour évaluation tâches |
| **Metrics** | Prometheus | latest | prometheus-fastapi-instrumentator |
| **Logging** | structlog | latest | Logging structuré JSON |
| **Container** | Docker | latest | Containerisation |
| **Reverse Proxy** | Traefik | latest | SSL + Routing |

### 1.3 Flux de Données

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUX PRINCIPAL                               │
└─────────────────────────────────────────────────────────────────┘

1. CRÉATION TÂCHE AVEC IA
   Client → POST /api/tasks {use_ai_evaluation: true}
         → Backend crée Task (status: pending)
         → Celery Task lancé: evaluate_task_difficulty
         → LLM Service appelle Claude/GPT
         → Task mis à jour avec ai_difficulty, ai_xp_reward
         → Notification envoyée à l'utilisateur

2. COMPLÉTION HABITUDE
   Client → POST /api/completions {habit_id, value}
         → Backend vérifie ownership
         → StreakService.update_streak()
         → XPService.calculate_habit_xp()
         → XPService.add_xp() → check level up
         → BadgeService.check_badges()
         → Response avec XP, coins, streak info

3. COMBAT PVP
   Client → POST /api/combat/challenge {defender_id, bet_coins}
         → CombatService.simulate_combat()
         → Génération combat_log turn-by-turn
         → distribute_rewards() au gagnant
         → Combat record en DB
         → Notifications aux deux joueurs
```

---

## 2. Base de Données

### 2.1 Schéma ER (Relations entre Tables)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ENTITY RELATIONSHIP DIAGRAM                        │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────┐
                              │    users     │
                              │──────────────│
                              │ id (PK/UUID) │
                              │ email        │
                              │ username     │
                              │ level        │
                              │ total_xp     │
                              │ coins        │
                              │ current_streak│
                              │ friend_code  │
                              │ google_id    │
                              │ apple_id     │
                              └──────┬───────┘
                                     │
          ┌──────────────┬───────────┼───────────┬──────────────┬─────────────┐
          │              │           │           │              │             │
          ▼              ▼           ▼           ▼              ▼             ▼
   ┌────────────┐ ┌───────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐
   │ characters │ │  habits   │ │  tasks  │ │ inventory│ │ badges   │ │friendships │
   │────────────│ │───────────│ │─────────│ │──────────│ │──────────│ │────────────│
   │ id (PK)    │ │ id (PK)   │ │ id (PK) │ │ id (PK)  │ │user_id PK│ │ id (PK)    │
   │ user_id FK │ │ user_id FK│ │user_id FK│ │user_id FK│ │badge_id PK│ │requester FK│
   │ name       │ │ name      │ │ title   │ │ item_id FK│ │          │ │addressee FK│
   │ class      │ │ frequency │ │ priority│ │is_equipped│ │          │ │ status     │
   │ STR/END/AGI│ │ streak    │ │ai_diff  │ └─────┬────┘ └────┬─────┘ └────────────┘
   │ INT/CHA    │ └─────┬─────┘ │ai_xp    │       │           │
   └────────────┘       │       └────┬────┘       ▼           ▼
                        │            │      ┌──────────┐ ┌──────────┐
                        ▼            │      │  items   │ │  badges  │
                 ┌────────────┐      │      │──────────│ │  (def)   │
                 │completions │      │      │ id (PK)  │ │──────────│
                 │────────────│      │      │ name     │ │ id (PK)  │
                 │ id (PK)    │      │      │ category │ │ code     │
                 │ habit_id FK│      │      │ rarity   │ │ condition│
                 │ user_id FK │      │      │ price    │ └──────────┘
                 │ date       │      │      │ bonuses  │
                 │ xp_earned  │      │      └──────────┘
                 └────────────┘      │
                                     ▼
                              ┌────────────┐
                              │  subtasks  │
                              │────────────│
                              │ id (PK)    │
                              │ task_id FK │
                              │ title      │
                              │is_completed│
                              └────────────┘

   ┌────────────────────────────────────────────────────────────────────────┐
   │                          AUTRES TABLES                                 │
   ├────────────────────────────────────────────────────────────────────────┤
   │  combats         : PvP battles (challenger, defender, winner, log)     │
   │  notifications   : User alerts (type, title, message, data)            │
   │  xp_transactions : Audit log of XP changes                             │
   │  coin_transactions: Audit log of coin changes                          │
   │  daily_stats     : Aggregated daily stats per user                     │
   │  rate_limits     : LLM rate limiting tracking                          │
   └────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Description des Tables

#### `users` - Utilisateurs
| Colonne | Type | Contrainte | Description |
|---------|------|------------|-------------|
| id | UUID | PK | Identifiant unique |
| email | VARCHAR(255) | UNIQUE, NOT NULL | Email de connexion |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Nom d'affichage |
| password_hash | VARCHAR(255) | NULLABLE | Hash bcrypt (null si OAuth) |
| display_name | VARCHAR(100) | NULLABLE | Nom affiché (optionnel) |
| bio | VARCHAR(280) | NULLABLE | Bio utilisateur |
| avatar_url | VARCHAR(500) | NULLABLE | URL avatar |
| timezone | VARCHAR(50) | DEFAULT 'UTC' | Timezone utilisateur |
| level | INTEGER | DEFAULT 1 | Niveau actuel |
| total_xp | INTEGER | DEFAULT 0 | XP cumulé |
| coins | INTEGER | DEFAULT 0 | Monnaie virtuelle |
| current_streak | INTEGER | DEFAULT 0 | Streak actif |
| best_streak | INTEGER | DEFAULT 0 | Meilleur streak |
| last_activity_date | DATE | NULLABLE | Dernière activité |
| streak_freeze_available | INTEGER | DEFAULT 1 | Freezes disponibles |
| friend_code | VARCHAR(20) | UNIQUE | Code ami (hex 8 chars) |
| is_public | BOOLEAN | DEFAULT FALSE | Profil public |
| google_id | VARCHAR(255) | UNIQUE, NULLABLE | ID OAuth Google |
| apple_id | VARCHAR(255) | UNIQUE, NULLABLE | ID OAuth Apple |
| notifications_enabled | BOOLEAN | DEFAULT TRUE | Notifications actives |
| theme | VARCHAR(20) | DEFAULT 'dark' | Thème UI |
| last_login_at | TIMESTAMP | NULLABLE | Dernier login |
| deleted_at | TIMESTAMP | NULLABLE | Soft delete |
| created_at | TIMESTAMP | auto | Création |
| updated_at | TIMESTAMP | auto | Mise à jour |

**Index**: `idx_users_email`, `idx_users_username`, `idx_users_friend_code`, `idx_users_google_id`

#### `habits` - Habitudes récurrentes
| Colonne | Type | Contrainte | Description |
|---------|------|------------|-------------|
| id | UUID | PK | Identifiant unique |
| user_id | UUID | FK → users | Propriétaire |
| name | VARCHAR(100) | NOT NULL | Nom habitude |
| description | TEXT | NULLABLE | Description |
| icon | VARCHAR(50) | DEFAULT '✅' | Emoji icône |
| color | VARCHAR(20) | DEFAULT '#6366F1' | Couleur hex |
| category | VARCHAR(50) | DEFAULT 'general' | Catégorie |
| frequency_type | VARCHAR(20) | DEFAULT 'daily' | daily/weekly/specific_days/x_per_week |
| frequency_days | INTEGER[] | DEFAULT [] | Jours (0=Lun, 6=Dim) |
| frequency_count | INTEGER | NULLABLE | X fois par semaine |
| target_value | INTEGER | NULLABLE | Objectif quantifiable |
| unit | VARCHAR(30) | NULLABLE | Unité (pages, min, ml) |
| reminder_time | TIME | NULLABLE | Heure rappel |
| reminder_enabled | BOOLEAN | DEFAULT FALSE | Rappel actif |
| current_streak | INTEGER | DEFAULT 0 | Streak habitude |
| best_streak | INTEGER | DEFAULT 0 | Meilleur streak |
| total_completions | INTEGER | DEFAULT 0 | Total complétions |
| total_xp_earned | INTEGER | DEFAULT 0 | XP total gagné |
| position | INTEGER | DEFAULT 0 | Ordre affichage |
| is_archived | BOOLEAN | DEFAULT FALSE | Archivé |
| archived_at | TIMESTAMP | NULLABLE | Date archivage |

**Index**: `idx_habits_user_id`, `idx_habits_category`, `idx_habits_archived`

#### `tasks` - Tâches ponctuelles avec évaluation IA
| Colonne | Type | Contrainte | Description |
|---------|------|------------|-------------|
| id | UUID | PK | Identifiant unique |
| user_id | UUID | FK → users | Propriétaire |
| title | VARCHAR(200) | NOT NULL | Titre tâche |
| description | TEXT | NULLABLE | Description |
| category | VARCHAR(50) | DEFAULT 'general' | Catégorie |
| priority | VARCHAR(20) | DEFAULT 'medium' | low/medium/high/urgent |
| due_date | DATE | NULLABLE | Date limite |
| due_time | TIME | NULLABLE | Heure limite |
| ai_difficulty | VARCHAR(20) | NULLABLE | trivial/easy/medium/hard/epic/legendary |
| ai_xp_reward | INTEGER | NULLABLE | XP évalué par IA |
| ai_coins_reward | INTEGER | NULLABLE | Coins évalués par IA |
| ai_reasoning | TEXT | NULLABLE | Explication IA |
| ai_suggested_subtasks | JSONB | DEFAULT [] | Sous-tâches suggérées |
| user_xp_adjustment | INTEGER | DEFAULT 0 | Ajustement manuel XP |
| user_coins_adjustment | INTEGER | DEFAULT 0 | Ajustement manuel coins |
| final_xp_reward | INTEGER | NULLABLE | XP final (IA + ajustement) |
| final_coins_reward | INTEGER | NULLABLE | Coins final |
| status | VARCHAR(20) | DEFAULT 'pending' | pending/in_progress/completed/cancelled |
| completed_at | TIMESTAMP | NULLABLE | Date complétion |

**Index**: `idx_tasks_user_id`, `idx_tasks_status`, `idx_tasks_due_date`

#### `characters` - Personnages RPG (LPC-based)
| Colonne | Type | Contrainte | Description |
|---------|------|------------|-------------|
| id | UUID | PK | Identifiant unique |
| user_id | UUID | FK → users, UNIQUE | Un personnage par user |
| name | VARCHAR(50) | NOT NULL | Nom personnage |
| class | VARCHAR(20) | NOT NULL | warrior/mage/ranger/paladin/assassin |
| gender | VARCHAR(20) | NOT NULL | Genre apparence |
| skin_color | VARCHAR(20) | NOT NULL | Couleur peau |
| hair_style | VARCHAR(50) | NOT NULL | Style cheveux |
| hair_color | VARCHAR(20) | NOT NULL | Couleur cheveux |
| eye_color | VARCHAR(20) | NOT NULL | Couleur yeux |
| strength | INTEGER | DEFAULT 0 | STR - dégâts |
| endurance | INTEGER | DEFAULT 0 | END - HP |
| agility | INTEGER | DEFAULT 0 | AGI - esquive |
| intelligence | INTEGER | DEFAULT 0 | INT - critique/XP bonus |
| charisma | INTEGER | DEFAULT 0 | CHA - social |
| unallocated_points | INTEGER | DEFAULT 0 | Points à distribuer |
| equipped_weapon_id | UUID | NULLABLE | FK implicite |
| equipped_armor_id | UUID | NULLABLE | FK implicite |
| equipped_helmet_id | UUID | NULLABLE | FK implicite |
| equipped_accessory_id | UUID | NULLABLE | FK implicite |
| equipped_pet_id | UUID | NULLABLE | FK implicite |

#### `items` - Objets du shop
| Colonne | Type | Contrainte | Description |
|---------|------|------------|-------------|
| id | UUID | PK | Identifiant unique |
| name | VARCHAR(100) | NOT NULL | Nom objet |
| description | TEXT | NULLABLE | Description |
| category | VARCHAR(30) | NOT NULL | weapon/armor/helmet/accessory/pet |
| rarity | VARCHAR(20) | NOT NULL | common/uncommon/rare/epic/legendary |
| price | INTEGER | NOT NULL | Prix en coins |
| strength_bonus | INTEGER | DEFAULT 0 | Bonus STR |
| endurance_bonus | INTEGER | DEFAULT 0 | Bonus END |
| agility_bonus | INTEGER | DEFAULT 0 | Bonus AGI |
| intelligence_bonus | INTEGER | DEFAULT 0 | Bonus INT |
| charisma_bonus | INTEGER | DEFAULT 0 | Bonus CHA |
| sprite_url | VARCHAR(500) | NULLABLE | URL sprite LPC |
| sprite_layer | INTEGER | DEFAULT 0 | Layer rendu |
| is_available | BOOLEAN | DEFAULT TRUE | Disponible à l'achat |
| is_limited | BOOLEAN | DEFAULT FALSE | Édition limitée |
| available_from | TIMESTAMP | NULLABLE | Début disponibilité |
| available_until | TIMESTAMP | NULLABLE | Fin disponibilité |
| required_level | INTEGER | DEFAULT 1 | Niveau requis |

**Index**: `idx_items_category`, `idx_items_rarity`, `idx_items_available`

#### `combats` - Historique PvP
| Colonne | Type | Contrainte | Description |
|---------|------|------------|-------------|
| id | UUID | PK | Identifiant unique |
| challenger_id | UUID | FK → users | Initiateur |
| defender_id | UUID | FK → users | Défenseur |
| winner_id | UUID | FK → users, NULLABLE | Gagnant (null si nul) |
| bet_coins | INTEGER | DEFAULT 0 | Mise |
| combat_log | JSONB | NOT NULL | Log tour par tour |
| challenger_stats | JSONB | NOT NULL | Stats snapshot challenger |
| defender_stats | JSONB | NOT NULL | Stats snapshot defender |
| challenger_final_hp | INTEGER | NULLABLE | HP final challenger |
| defender_final_hp | INTEGER | NULLABLE | HP final defender |
| total_turns | INTEGER | NULLABLE | Nombre de tours |
| winner_xp_reward | INTEGER | DEFAULT 0 | XP gagnant |
| winner_coins_reward | INTEGER | DEFAULT 0 | Coins gagnant |
| status | VARCHAR(20) | DEFAULT 'completed' | pending/completed/cancelled |
| created_at | TIMESTAMP | auto | Date combat |

**Index**: `idx_combats_challenger`, `idx_combats_defender`, `idx_combats_created`

#### `badges` - Définitions des badges
| Colonne | Type | Contrainte | Description |
|---------|------|------------|-------------|
| id | UUID | PK | Identifiant unique |
| code | VARCHAR(50) | UNIQUE | Code technique |
| name | VARCHAR(100) | NOT NULL | Nom affiché |
| description | TEXT | NOT NULL | Description |
| icon | VARCHAR(50) | NOT NULL | Emoji/icône |
| rarity | VARCHAR(20) | NOT NULL | common/uncommon/rare/epic/legendary/secret/seasonal |
| xp_reward | INTEGER | DEFAULT 0 | XP bonus déblocage |
| condition_type | VARCHAR(50) | NOT NULL | streak/completions/level/time/secret/date/combat_wins |
| condition_value | JSONB | NOT NULL | Paramètres condition |
| is_secret | BOOLEAN | DEFAULT FALSE | Badge secret |
| is_seasonal | BOOLEAN | DEFAULT FALSE | Badge saisonnier |

### 2.3 Index et Contraintes

```sql
-- Contraintes d'unicité
UNIQUE (users.email)
UNIQUE (users.username)
UNIQUE (users.friend_code)
UNIQUE (users.google_id)
UNIQUE (users.apple_id)
UNIQUE (characters.user_id)
UNIQUE (user_inventory.user_id, user_inventory.item_id) -- uq_user_inventory
UNIQUE (completions.habit_id, completions.completed_date) -- uq_completion_habit_date
UNIQUE (friendships.requester_id, friendships.addressee_id) -- uq_friendship_pair
UNIQUE (daily_stats.user_id, daily_stats.date) -- uq_daily_stats_user_date

-- Contraintes de vérification
CHECK (friendships.requester_id != friendships.addressee_id) -- ck_not_self_friend

-- Index partiels PostgreSQL
CREATE INDEX idx_users_google_id ON users(google_id) WHERE google_id IS NOT NULL;
CREATE INDEX idx_tasks_due_date ON tasks(due_date) WHERE status = 'pending';
```

---

## 3. API REST

### 3.1 Vue d'ensemble des Endpoints

| Préfixe | Module | Description |
|---------|--------|-------------|
| `/api/auth` | Authentication | Login, Register, OAuth, Refresh |
| `/api/users` | Users | Profile CRUD, Settings |
| `/api/habits` | Habits | CRUD habitudes récurrentes |
| `/api/tasks` | Tasks | CRUD tâches + évaluation IA |
| `/api/completions` | Completions | Enregistrement complétions |
| `/api/characters` | Characters | Personnage RPG + stats |
| `/api/shop` | Shop | Catalogue items |
| `/api/inventory` | Inventory | Inventaire utilisateur |
| `/api/combat` | Combat | PvP battles |
| `/api/friends` | Friends | Système d'amis |
| `/api/leaderboard` | Leaderboard | Classements |
| `/api/stats` | Stats | Statistiques utilisateur |
| `/api/badges` | Badges | Achievements |

### 3.2 Endpoints Détaillés

#### Authentication (`/api/auth`)

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/register` | Inscription email/password | ❌ |
| POST | `/login` | Connexion email/password | ❌ |
| POST | `/logout` | Déconnexion | ✅ |
| POST | `/refresh` | Refresh access token | ❌ |
| POST | `/google` | OAuth Google | ❌ |
| POST | `/apple` | OAuth Apple | ❌ |
| GET | `/me` | Profil utilisateur connecté | ✅ |
| POST | `/forgot-password` | Demande reset password | ❌ |
| POST | `/reset-password` | Reset password avec token | ❌ |

**Exemple: Register**
```json
// POST /api/auth/register
// Request
{
  "email": "player@example.com",
  "username": "Player123",
  "password": "SecurePass123!"
}

// Response 201 Created
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 2592000,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "player@example.com",
    "username": "Player123",
    "level": 1,
    "total_xp": 0,
    "coins": 0,
    "current_streak": 0
  }
}
```

#### Habits (`/api/habits`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Liste toutes les habitudes |
| POST | `/` | Créer une habitude |
| GET | `/today` | Habitudes du jour avec progression |
| GET | `/{habit_id}` | Détails d'une habitude |
| PUT | `/{habit_id}` | Modifier une habitude |
| DELETE | `/{habit_id}` | Supprimer une habitude |
| POST | `/{habit_id}/archive` | Archiver une habitude |
| GET | `/{habit_id}/history` | Historique complétions |

**Exemple: Create Habit**
```json
// POST /api/habits
// Request
{
  "title": "Méditation",
  "description": "10 minutes de méditation guidée",
  "icon": "🧘",
  "color": "#10B981",
  "frequency": "daily",
  "reminder_time": "07:00:00"
}

// Response 201 Created
{
  "id": "...",
  "title": "Méditation",
  "frequency": "daily",
  "current_streak": 0,
  "best_streak": 0,
  "base_xp": 10,
  "base_coins": 5
}
```

#### Tasks (`/api/tasks`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Liste des tâches |
| POST | `/` | Créer une tâche (+ AI eval optionnel) |
| GET | `/today` | Tâches dues aujourd'hui |
| GET | `/overdue` | Tâches en retard |
| GET | `/{task_id}` | Détails + évaluation IA |
| PUT | `/{task_id}` | Modifier une tâche |
| DELETE | `/{task_id}` | Supprimer une tâche |
| POST | `/{task_id}/complete` | Compléter → recevoir récompenses |
| POST | `/{task_id}/reevaluate` | Relancer évaluation IA |

**Exemple: Create Task with AI**
```json
// POST /api/tasks
// Request
{
  "title": "Préparer présentation Q1",
  "description": "Slides pour la réunion de lundi, 20 slides max",
  "priority": "high",
  "due_date": "2026-02-15T17:00:00Z",
  "use_ai_evaluation": true
}

// Response 201 Created (évaluation async)
{
  "id": "...",
  "title": "Préparer présentation Q1",
  "status": "pending",
  "difficulty": null,  // Sera rempli par Celery
  "xp_reward": null,
  "ai_reasoning": null
}

// Après évaluation IA (notification)
{
  "difficulty": "hard",
  "xp_reward": 70,
  "coins_reward": 35,
  "ai_reasoning": "Task requires creative effort, multiple slides, and deadline pressure.",
  "suggested_subtasks": [
    "Gather Q1 data",
    "Create outline",
    "Design slides",
    "Review and polish"
  ]
}
```

#### Combat (`/api/combat`)

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/history` | Historique combats |
| POST | `/challenge` | Lancer un défi |
| GET | `/preview/{user_id}` | Aperçu avant combat |
| GET | `/{combat_id}` | Détails d'un combat |

### 3.3 Codes d'Erreur

| Code | Signification | Exemple |
|------|---------------|---------|
| 200 | OK | GET réussi |
| 201 | Created | POST réussi |
| 204 | No Content | DELETE réussi |
| 400 | Bad Request | Validation échouée |
| 401 | Unauthorized | Token invalide/expiré |
| 403 | Forbidden | Accès refusé |
| 404 | Not Found | Ressource inexistante |
| 409 | Conflict | Email déjà utilisé |
| 422 | Unprocessable Entity | Données invalides |
| 429 | Too Many Requests | Rate limit atteint |
| 500 | Internal Server Error | Erreur serveur |

**Format d'erreur standardisé:**
```json
{
  "detail": "Message d'erreur explicite"
}
```

---

## 4. Authentification

### 4.1 Flow OAuth (Google & Apple)

```
┌─────────────────────────────────────────────────────────────────┐
│                    GOOGLE OAUTH FLOW                            │
└─────────────────────────────────────────────────────────────────┘

  ┌────────┐      ┌────────────┐      ┌────────────┐      ┌─────────┐
  │ Client │      │   Google   │      │  Backend   │      │   DB    │
  └───┬────┘      └─────┬──────┘      └─────┬──────┘      └────┬────┘
      │                 │                   │                  │
      │ 1. Login button │                   │                  │
      │ ────────────────►                   │                  │
      │                 │                   │                  │
      │ 2. Redirect to Google               │                  │
      │ ◄────────────────                   │                  │
      │                 │                   │                  │
      │ 3. User consents│                   │                  │
      │ ────────────────►                   │                  │
      │                 │                   │                  │
      │ 4. id_token     │                   │                  │
      │ ◄────────────────                   │                  │
      │                 │                   │                  │
      │ 5. POST /api/auth/google            │                  │
      │ ─────────────────────────────────────►                  │
      │                 │                   │                  │
      │                 │  6. Verify token  │                  │
      │                 │ ◄──────────────────                  │
      │                 │                   │                  │
      │                 │  7. Token valid   │                  │
      │                 │ ──────────────────►                  │
      │                 │                   │                  │
      │                 │                   │ 8. Find/Create  │
      │                 │                   │ ─────────────────►
      │                 │                   │                  │
      │                 │                   │ 9. User data    │
      │                 │                   │ ◄─────────────────
      │                 │                   │                  │
      │ 10. JWT + user  │                   │                  │
      │ ◄─────────────────────────────────────                  │
      │                 │                   │                  │
```

**Implémentation Backend:**
```python
@router.post("/google")
async def google_auth(request: OAuthRequest, db: DatabaseSession):
    # 1. Vérifier le token Google
    idinfo = google_id_token.verify_oauth2_token(
        request.id_token,
        google_requests.Request(),
        settings.google_client_id
    )
    
    google_id = idinfo["sub"]
    email = idinfo.get("email")
    
    # 2. Chercher ou créer l'utilisateur
    user = await find_by_google_id(google_id)
    
    if not user:
        # Lier à un compte existant ou créer nouveau
        user = await find_or_create_user(email, google_id)
    
    # 3. Générer JWT
    return TokenResponse(
        access_token=create_access_token({"sub": str(user.id)}),
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )
```

### 4.2 JWT Structure

**Access Token (30 jours):**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // user_id
  "exp": 1739145600,                               // expiration timestamp
  "iat": 1736553600                                // issued at
}
```

**Refresh Token (60 jours):**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "exp": 1741824000,
  "iat": 1736553600,
  "type": "refresh"
}
```

**Configuration:**
```python
# app/config.py
class Settings(BaseSettings):
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 43200  # 30 jours
```

### 4.3 Refresh Token Strategy

```
┌────────────────────────────────────────────────────────────────┐
│                   TOKEN REFRESH FLOW                           │
└────────────────────────────────────────────────────────────────┘

1. Access token expire (après 30 jours)
2. Client détecte 401 Unauthorized
3. Client POST /api/auth/refresh avec refresh_token
4. Backend vérifie:
   - Token valide et non expiré
   - Type = "refresh"
   - User existe et actif
5. Backend génère nouveau access_token
6. Client stocke nouveau token
7. Client retry la requête originale

Notes:
- Refresh token valide 60 jours
- Un seul refresh token actif par session
- En production: implémenter token rotation + blacklist Redis
```

---

## 5. Services Métier

### 5.1 XP & Level System

#### Formule de progression
```python
# XP requis pour atteindre un niveau
XP_BASE = 100
XP_EXPONENT = 1.8

def xp_for_level(level: int) -> int:
    if level <= 1:
        return 0
    total_xp = 0
    for lvl in range(2, level + 1):
        total_xp += int(XP_BASE * (lvl ** XP_EXPONENT))
    return total_xp

# Exemples:
# Niveau 1:  0 XP (départ)
# Niveau 2:  100 XP
# Niveau 5:  871 XP
# Niveau 10: 6,310 XP
# Niveau 20: 44,090 XP
# Niveau 50: 538,632 XP
# Niveau 100: 3,981,072 XP
```

#### XP par activité

| Source | XP Base | Modificateurs |
|--------|---------|---------------|
| **Habitude (easy)** | 10 | +streak mult, +INT bonus |
| **Habitude (medium)** | 15 | +streak mult, +INT bonus |
| **Habitude (hard)** | 20 | +streak mult, +INT bonus |
| **Tâche trivial** | 5 | +20% si early |
| **Tâche easy** | 15 | +20% si early |
| **Tâche medium** | 35 | +20% si early |
| **Tâche hard** | 70 | +20% si early |
| **Tâche epic** | 150 | +20% si early |
| **Tâche legendary** | 300 | +20% si early |
| **Combat (victoire)** | 50 | +10 par niveau adversaire |
| **Combat (défaite)** | 10 | Consolation |

#### Récompenses par palier

| Niveau | Stat Points | Coins | Titre | Déblocage |
|--------|-------------|-------|-------|-----------|
| 5 | 5 | 100 | Apprenti Aventurier | basic_sword |
| 10 | 5 | 250 | Aventurier | leather_armor, PvP combat |
| 15 | 5 | 400 | Aventurier Confirmé | silver_ring |
| 20 | 5 | 600 | Héros Local | steel_sword |
| 25 | 10 | 1000 | Champion | champion_cape, Guilds |
| 30 | 5 | 800 | Vétéran | veteran_helmet |
| 40 | 5 | 1200 | Élite | elite_armor |
| 50 | 15 | 2000 | Légende Vivante | legendary_sword, custom_titles |
| 75 | 10 | 3000 | Mythique | mythic_wings |
| 100 | 20 | 5000 | Immortel | immortal_aura, prestige_system |

### 5.2 Streak Calculation

```python
# Multiplicateur de streak
STREAK_MIN = 1.0
STREAK_MAX = 2.0
STREAK_INCREMENT = 0.02  # +2% par jour

def get_streak_multiplier(streak: int) -> float:
    """
    Streak 0:  x1.00
    Streak 5:  x1.10
    Streak 10: x1.20
    Streak 25: x1.50
    Streak 50: x2.00 (cap)
    """
    multiplier = STREAK_MIN + (streak * STREAK_INCREMENT)
    return min(STREAK_MAX, multiplier)

# Logique de mise à jour
def update_streak(user, completion_date):
    last_activity = user.last_activity_date
    
    if last_activity is None:
        # Premier jour
        user.current_streak = 1
    elif (completion_date - last_activity).days == 1:
        # Jour consécutif
        user.current_streak += 1
    elif (completion_date - last_activity).days == 2:
        # Un jour manqué - vérifier freeze
        if user.streak_freeze_available > 0:
            user.streak_freeze_available -= 1
            user.current_streak += 1  # Maintenu
        else:
            user.current_streak = 1  # Reset
    elif (completion_date - last_activity).days > 2:
        # Plus de 2 jours - reset
        user.current_streak = 1
    
    user.last_activity_date = completion_date
```

### 5.3 Combat Simulation

```python
# Configuration
BASE_HP = 100
HP_PER_ENDURANCE = 5
MAX_TURNS = 50
MAX_DODGE_CHANCE = 0.30  # 30%
MAX_CRIT_CHANCE = 0.20   # 20%
CRIT_DAMAGE_MULT = 1.5
DAMAGE_VARIANCE = 0.20   # ±20%

# Calcul HP
max_hp = BASE_HP + (endurance * HP_PER_ENDURANCE)
# Exemple: END 20 → 100 + 100 = 200 HP

# Calcul esquive (AGI)
dodge_chance = min(agility * 0.005, MAX_DODGE_CHANCE)
# Exemple: AGI 30 → 15% esquive

# Calcul critique (INT)
crit_chance = min(intelligence * 0.003, MAX_CRIT_CHANCE)
# Exemple: INT 30 → 9% critique

# Dégâts de base
damage = (strength + weapon_bonus) * random(0.8, 1.2)
if is_crit:
    damage *= CRIT_DAMAGE_MULT

# Réduction armure
armor_reduction = min(0.5, armor_bonus * 0.02)  # Cap 50%
final_damage = damage * (1 - armor_reduction)
```

**Flow combat:**
```
1. Déterminer premier attaquant (plus haute AGI)
2. Boucle jusqu'à KO ou 50 tours:
   a. Attaquant calcule dégâts
   b. Défenseur tente esquive
   c. Si touché, appliquer dégâts
   d. Vérifier KO
   e. Inverser rôles
3. Déterminer gagnant:
   - KO direct → adversaire gagne
   - Temps écoulé → plus haut % HP gagne
   - Égalité HP → match nul
4. Distribuer récompenses
```

### 5.4 LLM Integration

**Architecture:**
```python
class LLMService:
    """Service d'évaluation IA avec function calling."""
    
    # Providers supportés
    provider: "anthropic" | "openai"
    model: str  # claude-3-5-haiku / gpt-4o-mini
    
    # Tools disponibles
    TOOLS = [
        "get_user_stats",      # Stats utilisateur pour calibration
        "get_similar_tasks",   # Tâches similaires historiques
        "get_reward_scale",    # Échelle XP/coins par difficulté
        "get_category_average" # Moyennes par catégorie
    ]
```

**Échelle de récompenses:**
```python
REWARD_SCALE = {
    "trivial":   {"xp_min": 5,   "xp_max": 15,  "coins_min": 2,   "coins_max": 5},
    "easy":      {"xp_min": 15,  "xp_max": 35,  "coins_min": 5,   "coins_max": 15},
    "medium":    {"xp_min": 35,  "xp_max": 75,  "coins_min": 15,  "coins_max": 35},
    "hard":      {"xp_min": 75,  "xp_max": 150, "coins_min": 35,  "coins_max": 75},
    "epic":      {"xp_min": 150, "xp_max": 300, "coins_min": 75,  "coins_max": 150},
    "legendary": {"xp_min": 300, "xp_max": 500, "coins_min": 150, "coins_max": 300},
}
```

**System prompt IA:**
```
Tu es un évaluateur expert pour une app de suivi d'habitudes gamifiée.
Analyse les tâches et détermine:
1. Difficulté: trivial, easy, medium, hard, epic, legendary
2. XP Reward: basé sur échelle et complexité
3. Coins Reward: basé sur difficulté
4. Temps estimé: en minutes
5. Sous-tâches: découpage en étapes

Utilise les outils pour:
- Vérifier le niveau utilisateur pour calibrer
- Trouver des tâches similaires passées
- Référencer l'échelle de récompenses

Réponds en JSON:
{
  "difficulty": "medium",
  "xp_reward": 50,
  "coins_reward": 25,
  "reasoning": "...",
  "suggested_subtasks": ["Step 1", "Step 2"],
  "estimated_time_minutes": 60
}
```

---

## 6. Celery Tasks

### 6.1 Configuration

```python
# app/celery_app.py
celery_app = Celery(
    "habit_tracker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.llm_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.stats_tasks",
        "app.tasks.cleanup_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,      # 5 minutes max
    worker_prefetch_multiplier=1,
    result_expires=3600,      # 1 heure
)
```

### 6.2 Tâches Planifiées (Beat Schedule)

| Tâche | Fréquence | Description |
|-------|-----------|-------------|
| `aggregate_daily_stats` | Tous les jours (00:00 UTC) | Agrège les stats du jour précédent |
| `reset_weekly_freeze` | Tous les lundis (00:00 UTC) | Reset des streak freezes hebdomadaires |
| `cleanup_old_notifications` | Tous les jours | Supprime notifications > 30 jours |

```python
celery_app.conf.beat_schedule = {
    "aggregate-daily-stats": {
        "task": "app.tasks.stats_tasks.aggregate_daily_stats",
        "schedule": 86400.0,  # 24h
    },
    "reset-weekly-freeze": {
        "task": "app.tasks.cleanup_tasks.reset_weekly_freeze",
        "schedule": 604800.0,  # 7 jours
    },
    "cleanup-notifications": {
        "task": "app.tasks.cleanup_tasks.cleanup_old_notifications",
        "schedule": 86400.0,  # 24h
    },
}
```

### 6.3 Tâches Async

#### LLM Tasks
| Tâche | Retry | Description |
|-------|-------|-------------|
| `evaluate_task_difficulty` | 3x, backoff | Évalue une tâche via LLM |
| `reevaluate_task` | 2x | Relance évaluation |
| `batch_evaluate_tasks` | 2x | Évalue plusieurs tâches |

```python
@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,        # Exponential backoff
    retry_backoff_max=300,     # Max 5 minutes
)
def evaluate_task_difficulty(self, task_id: str):
    """Évalue une tâche via LLM avec retry automatique."""
    ...
```

#### Notification Tasks
| Tâche | Description |
|-------|-------------|
| `send_notification` | Crée une notification utilisateur |
| `broadcast_notification` | Envoie à plusieurs utilisateurs |
| `send_streak_warnings` | Alerte streaks à risque |
| `mark_notifications_read` | Marque notifications lues |

#### Stats Tasks
| Tâche | Description |
|-------|-------------|
| `aggregate_daily_stats` | Agrège stats quotidiennes |
| `calculate_leaderboard` | Calcule classements |
| `recalculate_user_totals` | Recalcule XP/coins depuis transactions |

### 6.4 Retry Strategy

```python
# Configuration retry par défaut
RETRY_CONFIG = {
    "max_retries": 3,
    "default_retry_delay": 60,        # 1 minute
    "retry_backoff": True,            # Exponential
    "retry_backoff_max": 300,         # 5 minutes max
}

# Séquence retry avec backoff:
# Tentative 1: immédiate
# Tentative 2: après 60s
# Tentative 3: après 120s
# Tentative 4: après 240s (cap à 300s si dépassé)
```

---

## 7. Monitoring

### 7.1 Métriques Prometheus

**Endpoint**: `GET /api/metrics`

Métriques auto-collectées par `prometheus-fastapi-instrumentator`:

| Métrique | Type | Description |
|----------|------|-------------|
| `http_requests_total` | Counter | Total requêtes HTTP |
| `http_request_duration_seconds` | Histogram | Latence requêtes |
| `http_request_size_bytes` | Summary | Taille requêtes |
| `http_response_size_bytes` | Summary | Taille réponses |
| `http_requests_in_progress` | Gauge | Requêtes en cours |

**Labels**: `method`, `handler`, `status`

### 7.2 Health Check Endpoints

#### Simple Health Check
```
GET /api/health

Response 200:
{
  "status": "healthy",
  "app": "Habit Tracker API",
  "version": "1.0.0",
  "environment": "production"
}
```

#### Detailed Health Check
```
GET /api/health/detailed

Response 200:
{
  "status": "healthy",
  "database": "healthy",
  "redis": "healthy",
  "app": "Habit Tracker API",
  "version": "1.0.0"
}

Response 503 (si service down):
{
  "status": "unhealthy",
  "database": "unhealthy: Connection refused",
  "redis": "healthy",
  ...
}
```

### 7.3 Logging Structure

**Format**: JSON structuré via `structlog`

```json
{
  "timestamp": "2026-02-09T12:34:56.789Z",
  "level": "info",
  "event": "task_completed",
  "task_id": "550e8400-...",
  "user_id": "123e4567-...",
  "xp_earned": 50,
  "coins_earned": 25
}
```

**Niveaux de log**:
- `DEBUG`: Détails développement
- `INFO`: Événements normaux
- `WARNING`: Situations anormales non-critiques
- `ERROR`: Erreurs avec stack trace

**Configuration**:
```python
# app/config.py
log_level: str = "INFO"  # Configurable via env
```

---

## 8. Déploiement

### 8.1 Docker Compose Configuration

```yaml
# docker-compose.yml (simplifié)
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${DB_USER:-habit_user}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME:-habit_tracker}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready"]
      
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb
    volumes:
      - redis_data:/data
      
  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://...
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres: { condition: service_healthy }
      redis: { condition: service_healthy }
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.habit-api.rule=Host(`habit.apps.ilanewep.cloud`) && PathPrefix(`/api`)"
      
  celery-worker:
    build: ./backend
    command: celery -A app.celery_app worker --loglevel=info --concurrency=2
    
  celery-beat:
    build: ./backend
    command: celery -A app.celery_app beat --loglevel=info

volumes:
  postgres_data:
  redis_data:

networks:
  habit-network:
  traefik-public:
    external: true
```

### 8.2 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_USER` | ❌ | habit_user | PostgreSQL username |
| `DB_PASSWORD` | ✅ | - | PostgreSQL password |
| `DB_NAME` | ❌ | habit_tracker | Database name |
| `SECRET_KEY` | ✅ | - | JWT signing key |
| `REDIS_URL` | ❌ | redis://localhost:6379/0 | Redis connection |
| `DATABASE_URL` | ❌ | (construit) | Full PostgreSQL URL |
| `ANTHROPIC_API_KEY` | ❌ | - | Clé API Claude |
| `OPENAI_API_KEY` | ❌ | - | Clé API OpenAI |
| `GOOGLE_CLIENT_ID` | ❌ | - | OAuth Google |
| `GOOGLE_CLIENT_SECRET` | ❌ | - | OAuth Google |
| `APPLE_CLIENT_ID` | ❌ | - | Sign In with Apple |
| `ENVIRONMENT` | ❌ | production | development/production |
| `LOG_LEVEL` | ❌ | INFO | DEBUG/INFO/WARNING/ERROR |
| `CORS_ORIGINS` | ❌ | https://habit.apps.ilanewep.cloud | Origines autorisées |

### 8.3 Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code
COPY . .

# User non-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### 8.4 Scripts de Déploiement

#### Démarrage complet
```bash
#!/bin/bash
# deploy.sh

# Vérifier les variables requises
if [ -z "$DB_PASSWORD" ] || [ -z "$SECRET_KEY" ]; then
    echo "ERROR: DB_PASSWORD and SECRET_KEY must be set"
    exit 1
fi

# Pull latest images
docker compose pull

# Start services
docker compose up -d --build

# Wait for health
echo "Waiting for services..."
sleep 10

# Run migrations
docker compose exec backend alembic upgrade head

# Check health
curl -f http://localhost:8000/api/health || exit 1

echo "Deployment complete!"
```

#### Mise à jour sans downtime
```bash
#!/bin/bash
# update.sh

# Build new image
docker compose build backend

# Rolling update
docker compose up -d --no-deps backend

# Wait and verify
sleep 5
curl -f http://localhost:8000/api/health/detailed

# Update workers
docker compose up -d --no-deps celery-worker celery-beat
```

#### Backup base de données
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="habit_tracker_${DATE}.sql.gz"

docker compose exec -T postgres pg_dump -U habit_user habit_tracker | gzip > $BACKUP_FILE

echo "Backup created: $BACKUP_FILE"
```

---

## Annexes

### A. Schéma JSON Complet des Modèles

Voir les fichiers `app/schemas/*.py` pour les schémas Pydantic complets.

### B. Collection Postman/Insomnia

Disponible sur demande avec tous les endpoints documentés.

### C. Changelog

| Version | Date | Changements |
|---------|------|-------------|
| 1.0.0 | 2026-02-09 | Version initiale |

---

*Documentation générée automatiquement depuis le code source.*
