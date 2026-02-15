# 🐺 Audit Backend — HabitQuest Sprint 1

**Date:** 2026-02-15  
**Auditeur:** Kuro  
**Scope:** Core loop API — Register → Onboarding → Habits → XP/Coins → Shop → Équipement

---

## ✅ Endpoints qui fonctionnent

| Endpoint | Status | Notes |
|----------|--------|-------|
| `POST /api/auth/register` | ✅ OK | User créé avec level=1, xp=0, coins=0 |
| `POST /api/auth/login` | ✅ OK | Token JWT retourné |
| `GET /api/auth/me` | ✅ OK | Données user correctes |
| `POST /api/characters/` | ✅ OK | Character créé, stats initialisées |
| `GET /api/characters/me` | ✅ OK | Retourne 404 correct si pas de perso |
| `POST /api/habits/` | ✅ OK | Habit créé avec base_xp/base_coins |
| `GET /api/habits/today` | ✅ OK | Liste habits du jour |
| `POST /api/completions/` | ✅ OK | XP/Coins calculés avec streak bonus |
| `GET /api/shop/items` | ✅ OK | 38 items, pagination OK |
| `POST /api/shop/buy/{id}` | ✅ OK | Achat + débit coins OK |
| `GET /api/inventory/` | ✅ OK | Items possédés listés |
| `POST /api/inventory/equip/{id}` | ✅ OK | Item équipé, slot assigné |
| `GET /api/inventory/equipped` | ✅ OK | Map des slots équipés |
| `GET /api/badges/collection` | ✅ OK | 68 badges total |

---

## 🚨 BUGS CRITIQUES (P0)

### BUG-001: Celery workers crash — asyncio event loop mismatch

**Severity:** P0 — BLOQUANT  
**Fichier:** `/app/app/tasks/stats_tasks.py:190`  
**Symptôme:** Les workers Celery sont en état `unhealthy`  

```
RuntimeError: Task <Task pending name='Task-3' coro=<_aggregate_daily_stats_async()...> 
got Future <Future pending> attached to a different loop
```

**Cause:** Le code utilise `asyncio.new_event_loop()` dans le worker Celery, mais `async_session_maker()` crée une connexion asyncpg liée au loop d'origine (quand le module a été importé). Le pool de connexions est bound au mauvais event loop.

**Impact:**
- Tâches async ne s'exécutent pas
- Stats agrégées ne se calculent pas
- Notifications push ne partent pas
- Pas de génération LLM

**Fix proposé:**
```python
# Option 1: Sync DB dans Celery (recommandé)
# Utiliser une session sync SQLAlchemy dans les tasks

# Option 2: Créer le pool dans la task
async def _aggregate_daily_stats_async():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        ...
```

---

## ⚠️ BUGS MEDIUM (P1)

### BUG-002: best_streak ne se met pas à jour

**Severity:** P1  
**Endpoint:** `POST /api/completions/`  
**Symptôme:** Après completion, `current_streak=1` mais `best_streak=0`

```json
{
  "current_streak": 1,
  "best_streak": 0  // ← Devrait être 1
}
```

**Cause:** La logique de mise à jour du `best_streak` ne s'exécute pas ou compare incorrectement.

**Fix:** Vérifier dans le code de completion que `best_streak = max(best_streak, current_streak)`

---

### BUG-003: Tests character skipped — fixture async/sync mismatch

**Severity:** P1 — Tests broken  
**Fichier:** `tests/test_character.py`  
**Symptôme:** 12 tests skipped

**Cause:** Le fichier utilise `AsyncClient` mais `conftest.py` fournit un `httpx.Client` sync.

```python
# conftest.py
@pytest.fixture(scope="session")
def client():
    with httpx.Client(...) as client:  # ← SYNC
        yield client

# test_character.py
async def test_create_character(self, client: AsyncClient):  # ← ASYNC
```

**Fix:** Créer une fixture `async_client` dans conftest.py ou convertir les tests en sync.

---

### BUG-004: Tests E2E failures — connexion errors

**Severity:** P1 — Tests broken  
**Symptôme:** 42 tests en ERROR avec `httpx.ConnectError`

**Cause:** L'environnement de test (`docker-compose.test.yml`) ne connecte pas correctement au backend ou le backend de test n'est pas démarré.

**Fix:** Vérifier que le container de test peut joindre le backend, ou utiliser TestClient avec app montée en mémoire.

---

## 📊 Résumé des tests

| Status | Count |
|--------|-------|
| Passed | 6 |
| Failed | 35 |
| Skipped | 12 |
| Errors | 42 |
| **Total** | **95** |

La majorité des failures viennent de l'infra de test, pas du code.

---

## 🔧 Services Status

| Service | Status | Health |
|---------|--------|--------|
| habit-backend | UP | ✅ healthy |
| habit-frontend | UP | ✅ healthy |
| habit-postgres | UP | ✅ healthy |
| habit-redis | UP | ✅ healthy |
| habit-celery-worker | UP | ⚠️ **unhealthy** |
| habit-celery-beat | UP | ⚠️ **unhealthy** |

---

## 📝 Recommandations

### Priorité 1 (Sprint 1)
1. **FIX BUG-001** — Celery event loop (US-1.4)
2. **FIX BUG-002** — best_streak logic
3. **FIX tests infra** — conftest.py async/sync

### Priorité 2 (Sprint 2+)
4. Ajouter tests de non-régression pour le core loop
5. Monitoring Celery avec health endpoint dédié
6. Rate limiting sur endpoints sensibles

---

## ✅ Core Loop Validation

```
Register ✅ → Character ✅ → Habit ✅ → Complete ✅ → XP/Coins ✅ → Shop ✅ → Buy ✅ → Equip ✅
```

**Le core loop backend fonctionne.** Les bugs critiques sont sur Celery (async tasks) et les tests.

---

*Rapport généré par Kuro 🐺*
