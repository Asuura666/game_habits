# HabitQuest — Documentation de reprise de projet

> **Dernière mise à jour** : 28 février 2026
> **Auteur** : Shiro 🦊
> **Statut** : En pause — prêt à reprendre

---

## 1. Présentation du projet

**HabitQuest** est un habit tracker gamifié qui transforme les habitudes quotidiennes en aventure RPG. Chaque habitude accomplie fait progresser un personnage avec XP, niveaux, équipements et combats PvP.

- **Repo** : https://github.com/Asuura666/game_habits
- **POC en ligne** : https://habit.apps.ilanewep.cloud
- **VPS** : `/home/debian/habit-tracker`
- **Branche active** : `main` (sprint-2 mergé)

---

## 2. Stack technique

### Backend
| Composant | Technologie |
|-----------|-------------|
| Framework | **FastAPI** (Python 3.12) |
| Base de données | **PostgreSQL** 16 |
| Cache / Queue | **Redis** 7 |
| Tâches async | **Celery** (worker + beat) |
| ORM | **SQLAlchemy** 2.0 (async) |
| Auth | JWT (access + refresh tokens) |
| IA | OpenAI GPT pour évaluation de tâches |
| Migrations | Alembic |

### Frontend
| Composant | Technologie |
|-----------|-------------|
| Framework | **Next.js 14** (App Router) |
| Langage | TypeScript |
| Styling | **Tailwind CSS** |
| UI Components | **shadcn/ui** |
| Sprites | **Universal LPC** (Liberated Pixel Cup) |
| Animations | Canvas API + sprites LPC |
| State | React hooks + Context |

### Infrastructure
| Composant | Détail |
|-----------|--------|
| Hosting | VPS OVH (Docker Compose) |
| Containers | 5 services : backend, postgres, redis, celery-worker, celery-beat |
| Frontend | Build statique servi par Next.js standalone |
| Proxy | Traefik (wildcard *.apps.ilanewep.cloud) |
| CI/CD | Non configuré (déploiement manuel) |

---

## 3. Architecture du code

### Backend (`backend/`)
```
backend/
├── app/
│   ├── main.py              # FastAPI app + middleware
│   ├── config.py            # Settings (env vars)
│   ├── database.py          # SQLAlchemy async engine
│   ├── auth.py              # JWT auth dependencies
│   ├── models/              # 17 modèles SQLAlchemy
│   │   ├── user.py
│   │   ├── character.py
│   │   ├── habit.py
│   │   ├── task.py
│   │   ├── item.py
│   │   ├── badge.py
│   │   ├── friendship.py
│   │   ├── combat.py
│   │   ├── stats.py
│   │   └── ...
│   ├── routers/             # 18 routeurs (90 endpoints)
│   │   ├── auth.py          # Register, login, refresh
│   │   ├── habits.py        # CRUD habitudes
│   │   ├── tasks.py         # CRUD tâches + évaluation IA
│   │   ├── characters.py    # Personnage + équipement
│   │   ├── shop.py          # Boutique (38 items)
│   │   ├── friends.py       # Amis + invitations
│   │   ├── combat.py        # Combat PvP
│   │   ├── leaderboard.py   # Classement
│   │   ├── stats.py         # Statistiques
│   │   ├── badges.py        # Badges / achievements
│   │   └── ...
│   ├── services/            # Logique métier
│   │   ├── character_service.py
│   │   ├── combat_service.py  # ⚠️ EN COURS
│   │   ├── streak_service.py
│   │   ├── notification_service.py
│   │   └── xp_service.py
│   └── tasks/               # Tâches Celery
│       └── llm_tasks.py     # Évaluation IA async
├── tests/                   # 102 tests (13 fichiers)
├── alembic/                 # Migrations DB
├── scripts/
│   └── seed_badges.py       # Script seed badges
├── requirements.txt
└── Dockerfile
```

### Frontend (`frontend/`)
```
frontend/src/
├── app/
│   ├── (app)/               # Routes protégées (auth)
│   │   ├── dashboard/       # Page principale
│   │   ├── habits/          # Gestion habitudes
│   │   ├── tasks/           # Gestion tâches
│   │   ├── character/       # Personnage + sprite
│   │   ├── shop/            # Boutique items
│   │   ├── inventory/       # Inventaire
│   │   ├── friends/         # Amis ✅
│   │   ├── leaderboard/     # Classement ✅
│   │   ├── combat/          # Combat PvP (UI basique)
│   │   ├── badges/          # Badges
│   │   ├── stats/           # Statistiques
│   │   └── settings/        # Paramètres
│   ├── (auth)/              # Login / Register
│   └── admin/               # Panel admin
├── components/
│   ├── character/           # Composants sprite LPC
│   ├── habits/              # Composants habitudes
│   ├── layout/              # Sidebar, header
│   ├── animations/          # LevelUpNotification
│   └── ui/                  # shadcn/ui
└── lib/
    ├── api.ts               # Client API fetch
    └── auth-context.tsx     # Auth provider
```

---

## 4. Base de données — Modèles

| Modèle | Table | Description |
|--------|-------|-------------|
| User | users | Comptes utilisateurs (email, password bcrypt) |
| Character | characters | Personnage RPG (level, xp, hp, coins, sprite layers) |
| Habit | habits | Habitudes récurrentes (daily/weekly) |
| Task | tasks | Tâches one-shot (avec subtasks) |
| Subtask | subtasks | Sous-tâches |
| Completion | completions | Log des complétions habitudes |
| Item | items | Items boutique (38 items) |
| UserInventory | user_inventory | Items possédés par user |
| Badge | badges | Badges / achievements |
| UserBadge | user_badges | Badges gagnés |
| Friendship | friendships | Relations amis (pending/accepted) |
| Combat | combats | Combats PvP |
| DailyStats | daily_stats | Stats quotidiennes |
| Notification | notifications | Notifications in-app |
| CoinTransaction | coin_transactions | Historique gold |
| XPTransaction | xp_transactions | Historique XP |

---

## 5. Ce qui fonctionne ✅

### Sprint 1 — Fondations (terminé)
- [x] Auth complète (register, login, refresh token, JWT)
- [x] CRUD Habitudes (create, read, update, delete, complete)
- [x] CRUD Tâches (avec subtasks)
- [x] Personnage RPG (création, XP, level up, coins)
- [x] Sprites LPC animés sur Canvas (idle, walk, multiple directions)
- [x] Personnalisation personnage (layers : body, hair, clothes, armor)
- [x] Boutique avec 38 items (armes, armures, potions)
- [x] Inventaire + équipement
- [x] Système de streaks (daily streaks avec best_streak)
- [x] Statistiques (completions, heatmap, daily stats)
- [x] Badges / Achievements
- [x] Évaluation IA des tâches (GPT via Celery async)
- [x] Rate limiting LLM (20/jour par user)
- [x] Mobile responsive
- [x] LevelUpNotification animée
- [x] 57 tests backend passants

### Sprint 2 — Social (partiellement terminé)
- [x] Page Amis (UI + API : invitations, accepter, refuser, supprimer)
- [x] Page Leaderboard (classement par XP, level, streaks avec onglets)
- [x] 7 tests leaderboard
- [ ] **Combat PvP** — `combat_service.py` écrit (225 lignes) mais **non intégré**
  - Logique : attaque, défense, compétences, calcul dégâts basé sur stats personnage
  - Manque : intégration avec les routes, UI combat, matchmaking
- [ ] Notifications temps réel (modèle existe, pas de WebSocket)

### Total : 102 tests collectés, 90 endpoints API

---

## 6. Ce qui reste à faire ❌

### Priorité haute
1. **Combat PvP** — Finir l'intégration de `combat_service.py` :
   - Connecter aux routes `/api/combat/`
   - UI de combat (animations, tour par tour)
   - Matchmaking (challenge un ami)
2. **Notifications** — WebSocket ou polling pour notifications temps réel
3. **Calendrier** — La page existe mais est basique

### Priorité moyenne
4. **Plus de customisation personnage** — Plus de sprites LPC (coiffures, visages)
5. **Widget iOS** — Idée initiale, jamais commencé
6. **CI/CD** — Pipeline GitHub Actions pour déploiement auto
7. **PWA** — Manifest + service worker pour mobile

### Priorité basse
8. **Admin panel** — Existe mais très basique
9. **Achievements avancés** — Plus de badges, quêtes quotidiennes
10. **Mode sombre** — Partiellement implémenté

---

## 7. Comment relancer le projet

### Démarrer en local
```bash
cd /home/debian/habit-tracker
docker compose up -d
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Docs API: http://localhost:8000/docs
```

### Vérifier que tout tourne
```bash
docker ps --format '{{.Names}} {{.Status}}' | grep habit
# habit-backend      Up (healthy)
# habit-celery-beat  Up (healthy)
# habit-celery-worker Up (healthy)
# habit-redis        Up (healthy)
# habit-postgres     Up (healthy)
```

### Lancer les tests
```bash
docker exec habit-backend python3 -m pytest -v
# 102 tests
```

### Seed la DB (si vide)
```bash
docker exec habit-backend python3 scripts/seed_badges.py
```

### Variables d'environnement importantes
- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection
- `SECRET_KEY` — JWT secret
- `OPENAI_API_KEY` — Pour évaluation IA des tâches

---

## 8. Points d'attention ⚠️

1. **combat_service.py** est écrit mais pas connecté aux routes — c'est le dernier WIP
2. **Les sprites LPC** sont sous licence CC-BY-SA 3.0 — créditer Universal LPC Generator
3. **L'évaluation IA** consomme des tokens OpenAI — rate limited à 20/jour/user
4. **Le frontend** est en Next.js 14 App Router — attention au mix Server/Client Components
5. **Le skill HabitQuest** existe dans l'agent Shiro : `skills/habitquest-lpc-skill/`
6. **Les docs existantes** : `docs/FUNCTIONAL.md` (675 lignes) et `docs/TECHNICAL.md` (1320 lignes) sont détaillées

---

## 9. Historique des sprints

| Sprint | Dates | Contenu |
|--------|-------|---------|
| Sprint 1 | 7-10 fév 2026 | Fondations : auth, habits, tasks, character, shop, inventory, sprites LPC, streaks, stats, badges, LLM eval, responsive, 57 tests |
| Sprint 2 | 10-15 fév 2026 | Social : friends page, leaderboard, combat_service (WIP), 102 tests total |
| Pause | 15 fév → ... | Projet mis en pause pour focus CallRounded |

---

*Documentation rédigée par Shiro 🦊 — 28 février 2026*
*Pour reprendre : lire ce doc + docs/FUNCTIONAL.md + docs/TECHNICAL.md*
