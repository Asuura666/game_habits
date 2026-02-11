# Habit Tracker — Changelog & Documentation

**Projet :** Habit Tracker Gamifié  
**POC :** https://habit.apps.ilanewep.cloud  
**GitHub :** https://github.com/Asuura666/game_habits  
**VPS :** ssh debian@hello.apps.ilanewep.cloud  

---

## 📅 Historique des Modifications

### 10 février 2026

#### Backend (57 tests passent ✅)
- ✅ Fix dependencies (`email-validator`, `PyJWT`, `bcrypt` pin)
- ✅ Fix schemas pydantic (`stats.py`, `habit.py`)
- ✅ Fix imports (`friends.py`, `stats.py`)
- ✅ Désactivé combat router (CombatService manquant)
- ✅ Celery graceful degradation
- ✅ Alembic `env.py` Base import fix
- ✅ Seed 38 items shop
- ✅ Fix nginx port 8001 → 8000
- ✅ Logging structlog JSON + middleware request logging
- ✅ Métriques Prometheus sur `/api/metrics`

#### Frontend
- ✅ Responsive mobile (hamburger menu, sidebar slide)
- ✅ Login : meilleur error handling + logs
- ✅ `noValidate` forms (évite validation browser)
- ✅ **LPCCharacter** component avec layers dynamiques (body + hair + armor)
- ✅ Sprites LPC téléchargés (`/public/sprites/`)
- ✅ Page `/character` mise à jour avec LPCCharacter
- ✅ Onboarding avec sélection genre (Masculin/Féminin)
- ✅ Preview évolution personnage (niveaux 1, 5, 10, 15, 20)
- ✅ ErrorBoundary React pour capturer les erreurs
- ✅ Endpoint `/api/log/error` pour logging client

#### Tests E2E (Playwright)
- ✅ `e2e/auth.spec.ts` — register, login, logout, validation
- ✅ `e2e/habits.spec.ts` — CRUD habits, completion
- ✅ `e2e/dashboard.spec.ts` — navigation, stats display
- ✅ `e2e/shop.spec.ts` — items listing, purchase flow
- ✅ `e2e/character.spec.ts` — onboarding, customization
- ✅ `e2e/api-health.spec.ts` — 7/7 tests passent

#### Git
- Commit `c6abf51` — Fix dependencies + schemas
- Commit `4d41012` — LPCCharacter sprites (character + onboarding)
- Commit `5243eb0` — Tests E2E + Logging + Corrections API

---

## 🏗️ Architecture

### Stack Technique

| Composant | Technologie | Port |
|-----------|-------------|------|
| Frontend | Next.js 14 + Tailwind + shadcn/ui | 3001 |
| Backend | FastAPI + SQLAlchemy 2.0 | 8000 |
| Database | PostgreSQL 16 | 5432 (interne) |
| Cache | Redis 7 | 6379 (interne) |
| Task Queue | Celery + Redis | - |
| Reverse Proxy | Traefik | 80/443 |

### Docker Compose Services

```
habit-frontend        → Next.js (port 3001)
habit-backend         → FastAPI (port 8000)
habit-postgres        → PostgreSQL
habit-redis           → Redis
habit-celery-worker   → Celery Worker
habit-celery-beat     → Celery Beat (scheduler)
```

---

## 🔌 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Inscription |
| POST | `/api/auth/login` | Connexion (retourne JWT) |
| POST | `/api/auth/logout` | Déconnexion |
| GET | `/api/users/me` | Profil utilisateur |

### Habits
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/habits/` | Liste des habitudes |
| POST | `/api/habits/` | Créer une habitude |
| GET | `/api/habits/{id}` | Détail habitude |
| PUT | `/api/habits/{id}` | Modifier habitude |
| DELETE | `/api/habits/{id}` | Supprimer habitude |

### Completions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/completions/` | Compléter une habitude |
| GET | `/api/completions/` | Historique completions |

### Character
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/characters/me` | Mon personnage (⚠️ après onboarding) |
| POST | `/api/characters/` | Créer personnage (onboarding) |

### Shop
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/shop/items` | Liste items boutique |
| POST | `/api/shop/purchase` | Acheter un item |

### Stats
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats/overview` | Statistiques globales |

### Inventory
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/inventory/` | Mon inventaire |
| GET | `/api/inventory/equipped` | Items équipés |
| POST | `/api/inventory/{id}/equip` | Équiper un item |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/metrics` | Métriques Prometheus |

---

## 🎮 Sprites LPC

### Structure
```
/public/sprites/
├── body/
│   ├── male.png
│   └── female.png
├── hair/
│   ├── bangslong_male.png
│   ├── bangslong_female.png
│   └── ponytail_female.png
├── armor/
│   ├── robe_male.png / robe_female.png
│   ├── leather_male.png / leather_female.png
│   └── plate_male.png / plate_female.png
└── weapons/
```

### Évolution selon niveau
| Niveau | Armure |
|--------|--------|
| 1-2 | Aucune |
| 3-7 | Robe |
| 8-14 | Cuir |
| 15+ | Plate |

### Ring de rareté
| Niveau | Couleur | Tier |
|--------|---------|------|
| 1-4 | Gris | Commun |
| 5-9 | Vert | Peu commun |
| 10-14 | Bleu | Rare |
| 15-19 | Violet | Épique |
| 20+ | Or | Légendaire |

---

## 🧪 Tests

### Lancer les tests backend
```bash
cd /home/debian/habit-tracker/backend
pytest -v
```

### Lancer les tests E2E
```bash
cd /home/debian/habit-tracker/frontend
npm run e2e              # Headless
npm run e2e:headed       # Avec navigateur
npm run e2e:report       # Générer rapport HTML
```

---

## 📊 Monitoring

### Logs Docker
```bash
docker logs habit-backend -f --tail 100
docker logs habit-frontend -f --tail 100
```

### Métriques Prometheus
```
https://habit.apps.ilanewep.cloud/api/metrics
```

### Dashboard Monitoring
```
https://monitoring.apps.ilanewep.cloud
```

---

## 🚫 Features Désactivées

| Feature | Raison | Status |
|---------|--------|--------|
| Combat PvP | `CombatService` non implémenté | ❌ Désactivé |
| OAuth Google/Apple | Credentials non configurées | ❌ Non configuré |
| Notifications Push | Non implémenté | 💡 Future |
| Widget iOS | Nécessite app native Swift | 💡 Future |

---

## 📝 Notes pour les Testeurs

### Créer un compte
1. Aller sur https://habit.apps.ilanewep.cloud/register
2. Email valide, password 8+ chars avec majuscule et chiffre
3. Compléter l'onboarding (nom + classe + genre)

### Tester les features
- ✅ Créer des habitudes (quotidien, hebdo, etc.)
- ✅ Compléter des habitudes → gagne XP et coins
- ✅ Visiter la boutique → acheter des items
- ✅ Voir les stats et le dashboard
- ✅ Personnaliser le personnage
- ❌ Combat (désactivé)

### Signaler un bug
Contacter Ilane avec :
- URL de la page
- Action effectuée
- Message d'erreur (screenshot)
- Navigateur utilisé

---

## 🔄 Commandes Utiles

### Rebuild Frontend
```bash
cd /home/debian/habit-tracker/frontend
docker build -t habit-tracker-frontend .
docker stop habit-frontend && docker rm habit-frontend
docker run -d --name habit-frontend --network habit-tracker_habit-network -p 3001:3000 --restart unless-stopped habit-tracker-frontend
```

### Rebuild Backend
```bash
cd /home/debian/habit-tracker
docker compose build backend
docker compose up -d backend
```

### Voir l'état des services
```bash
docker ps | grep habit
```

### Accès base de données
```bash
docker exec -it habit-postgres psql -U habit_user -d habit_tracker
```

---

*Documentation générée par Shiro 🦊 — Dernière mise à jour : 11 février 2026*
