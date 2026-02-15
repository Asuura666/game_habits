# Audit Sprint-Aware — Claude (3 agents)

**Date :** 15 février 2026
**Auditeur :** Claude Opus 4.6 (3 agents parallèles)
**Agents :** backend-auditor, frontend-auditor, readiness-analyst
**Méthode :** Cross-référencement code source ↔ User Stories Sprints 2 & 3
**Référence :** US/sprint2-kickoff.md, US/sprint3-kickoff.md, docs/audit-sprint1-claude.md (144 findings)

---

## Résumé Exécutif

| Métrique | Valeur |
|----------|--------|
| **Score Readiness Sprint 2** | **4/10 — NO-GO conditionnel** |
| **Score Readiness Sprint 3 / Beta** | **3.5/10 — NO-GO sans fixes Sprint 2** |
| **Blockers pré-Sprint 2** | 4 (doivent être fixés AVANT le 24 fév) |
| **Bugs critiques backend** | 4 |
| **Bugs critiques frontend** | 1 bloquant + 12 importants |
| **Effort restant backend** | ~30-35h (vs 38h budgétés) |
| **Effort restant frontend** | ~35h / 23h si No-Go PvP (vs 34h budgétés) |

### Verdict

**Sprint 2 est réalisable SI et SEULEMENT SI les 4 blockers pré-sprint sont corrigés avant le 24 février.** Sans ces corrections, aucune US ne peut aboutir correctement.

**Sprint 3 / Beta est réalisable SI Sprint 2 est livré ET les fixes sécurité sont appliqués.** Le risque principal est le Go/No-Go PvP qui représente 24h de travail combiné (12h BE + 12h FE).

---

## 4 BLOCKERS PRÉ-SPRINT 2 (À fixer IMMÉDIATEMENT)

| # | Blocker | Impact | Effort | Responsable |
|---|---------|--------|--------|-------------|
| **B1** | `frontend/src/lib/utils.ts` n'existe pas — 22 fichiers cassés, **build impossible** | TOUTES les US frontend | 5 min | Shiro |
| **B2** | Deux classes `Base` (database.py vs models/base.py) — `init_db()` crée 0 tables | Migrations, nouvelles tables Sprint 2 | 30 min | Kuro |
| **B3** | Migration 001 diverge de ~50+ colonnes vs modèles actuels | Intégrité DB, deploy prod | 2-4h | Kuro |
| **B4** | Services sync (badge, xp, streak, combat) vs routers async — crash runtime | US-2.5, US-2.8, core loop | 4h | Kuro |

---

## AUDIT BACKEND PAR US

### US-2.1 — Friends Backend (Kuro, 6h, Must)

| Métrique | Valeur |
|----------|--------|
| **État** | 75% prêt |
| **Risque** | Faible |
| **Effort restant** | 2h |

**Ce qui existe :** Router complet (8 endpoints), modèle Friendship, schemas, 12 tests qui passent, friend_code fonctionnel avec auto-accept si demande inverse.

**Problèmes :**
- Pas de rate limit (spec : max 10 demandes en attente)
- N+1 queries dans `list_friends()` (SELECT User individuel par ami dans la boucle, lignes 137-154)
- URLs légèrement différentes de la spec (`/friends/code/{code}` vs `/friends/add`) — le frontend devra s'adapter

---

### US-2.3 — Leaderboard Backend (Kuro, 6h, Must)

| Métrique | Valeur |
|----------|--------|
| **État** | 80% prêt |
| **Risque** | Moyen |
| **Effort restant** | 3h |

**Ce qui existe :** Router avec 5 endpoints (weekly, monthly, streak, completion, pvp), filtrage amis via `get_friend_ids_with_self()`, LeaderboardService Redis complet.

**Problèmes :**
- **Double système non connecté** : le router fait des queries SQL directes, le LeaderboardService Redis n'est JAMAIS appelé
- LeaderboardService utilise Session sync (incompatible avec le router async)
- PvP leaderboard fait N queries en boucle par ami (lignes 383-407)
- Pas de caching — chaque appel recalcule tout en SQL

---

### US-2.5 — Combat PvP Backend (Kuro, 12h, Should — Go/No-Go 26 fév)

| Métrique | Valeur |
|----------|--------|
| **État** | 55% prêt |
| **Risque** | **ÉLEVÉ** |
| **Effort restant** | 10-14h |

**Ce qui existe :** Router (5 endpoints), CombatService (simulation complète), modèle Combat (JSONB log+stats). Router actuellement DÉSACTIVÉ dans main.py.

**Problèmes critiques :**

| ID | Description |
|----|-------------|
| BUG-C1 | **CRASH GARANTI** : Le router appelle `CombatService.create_combatant()` / `simulate_combat()` comme méthodes de classe, mais le service définit des fonctions standalone. Interface incompatible. |
| BUG-C2 | **Formules divergentes du CDC** : HP = `100 + endurance*5` (CDC: *10), Dodge = `agility*0.5%, cap 30%` (CDC: *2%, cap 40%), Crit = `intelligence*0.3%, cap 20%` (CDC: *1.5%, cap 30%) |
| BUG-C3 | Pas de check niveau minimum 5 |
| BUG-C4 | Pas de cooldown 1 combat/paire/jour |
| BUG-C5 | Mise max = 1000 dans le router (spec : 100) |
| BUG-C6 | Pas de `check_all_badges()` après combat |
| BUG-C7 | Endpoint `GET /combat/preview/{user_id}` manquant |
| BUG-C8 | Equipment bonuses = TODO dans le service |

**Verdict Go/No-Go :** En l'état, le combat est **No-Go**. 10-14h de travail restant, plus que les 12h budgétées. Si Kuro commence tôt et est efficace, c'est faisable mais serré.

---

### US-2.8 — Badges Auto-Attribution (Kuro, 4h, Must)

| Métrique | Valeur |
|----------|--------|
| **État** | 60% prêt |
| **Risque** | **ÉLEVÉ** |
| **Effort restant** | 5-6h |

**Ce qui existe :** BadgeService avec `check_all_badges()` (10 condition_types), `unlock_badge()` avec XP reward, router badges (5 endpoints), modèles Badge + UserBadge.

**Problèmes critiques :**

| ID | Description |
|----|-------------|
| BUG-B1 | **`check_all_badges()` n'est JAMAIS appelé** — le flux de complétion ne le déclenche pas. Les badges ne se débloquent JAMAIS automatiquement. |
| BUG-B2 | Service utilise Session sync (`db.query()`) — incompatible avec les routers async |
| BUG-B3 | `unlock_badge()` appelle `add_xp()` qui est aussi sync — chaîne sync cohérente mais incompatible async |
| BUG-B4 | Badge "comeback" retourne `True` si `current_streak == 1` (trop permissif) |
| BUG-B5 | `_check_coins_condition` "total_earned" = TODO non implémenté |
| BUG-B6 | Script `seed_badges.py` introuvable dans le repository |

---

### US-3.1 — Tests Backend (Kuro, 4h, Must)

| Métrique | Valeur |
|----------|--------|
| **État** | 50% prêt |
| **Risque** | Moyen |
| **Effort restant** | 6-8h |

**Ce qui existe :** 11 fichiers de tests, ~83 qui passent, 12 skipped. Tests friends bon coverage.

**Manques :** Pas de `test_combat.py`, pas de `test_leaderboard.py`, pas de `test_badges.py`. Les features Sprint 2 n'ont aucun test dédié.

---

### US-3.4 — Backup DB (Kuro, 2h, Must)

| Métrique | Valeur |
|----------|--------|
| **État** | 60% prêt |
| **Risque** | Faible |
| **Effort restant** | 1.5h |

**Ce qui existe :** Script `backup.sh` avec pg_dump + gzip + rotation 7 jours.

**Manques :** Pas de cron configuré, pas de script `restore.sh`, pas de test de restauration.

---

### US-3.5 — Monitoring (Kuro, 4h, Should)

| Métrique | Valeur |
|----------|--------|
| **État** | 50% prêt |
| **Risque** | Moyen |
| **Effort restant** | 3h |

**Ce qui existe :** `GET /api/health` (liveness), `GET /api/health/detailed` (DB+Redis), Prometheus instrumentator.

**Problèmes :**
- Router `health.py` séparé référence `settings.app_version` qui n'existe pas → crash si monté
- Duplication : health endpoints dans main.py ET dans health.py (non monté)
- Pas de check Celery ni LLM
- Pas de script `monitor.sh`

---

## AUDIT FRONTEND PAR US

### BLOCKER TRANSVERSAL : `@/lib/utils` manquant

**22 fichiers** importent `cn()` depuis `@/lib/utils` mais le répertoire `frontend/src/lib/` **n'existe pas**. Le build Next.js échoue. **Toutes les US frontend sont bloquées.**

Correction (5 min) : Créer `frontend/src/lib/utils.ts` avec `cn()` (clsx + tailwind-merge, dépendances déjà installées).

---

### US-2.2 — Friends Frontend (Shiro, 8h, Must)

| Métrique | Valeur |
|----------|--------|
| **État** | 75% prêt |
| **Risque** | Moyen |
| **Effort restant** | 3h |

**Ce qui existe :** Page `/friends` complète (449 lignes), 3 sections (amis, demandes, ajouter), FriendCard, friend_code copier, états vides, API réelle intégrée, responsive Tailwind.

**Problèmes :**
- Build cassé (blocker `cn()`)
- Pas de hooks dédiés (tout en useState/useEffect inline, React Query non utilisé)
- Demandes sortantes affichent l'UUID au lieu du username
- Pas de lien vers profil ami

---

### US-2.4 — Leaderboard Frontend (Shiro, 8h, Must)

| Métrique | Valeur |
|----------|--------|
| **État** | 80% prêt |
| **Risque** | Faible |
| **Effort restant** | 2h |

**Ce qui existe :** Page complète (300 lignes), 4 onglets (dépasse la spec de 3), podium top 3 avec médailles et animations framer-motion, surbrillance utilisateur courant, position sticky si hors top 10, états vides.

**Manques :** CTA vers /friends dans l'état vide, pull-to-refresh.

---

### US-2.6 — Combat PvP Frontend (Shiro, 12h, Should — conditionnel)

| Métrique | Valeur |
|----------|--------|
| **État** | **15% prêt** |
| **Risque** | **ÉLEVÉ** |
| **Effort restant** | 12h (rewrite complet) |

**Ce qui existe :** Page `/combat` (348 lignes) mais c'est du **PvE client-side contre 3 ennemis en dur** (Slime, Gobelin, Dragon). 100% mock data, 0 appel API. Ce n'est PAS du PvP.

**Manques (tout le PvP) :** Écran pré-combat, intégration API PvP, résultat PvP, historique, bouton "Défier", gestion erreurs.

---

### US-2.7 — Page Profil Ami (Shiro, 6h, Must)

| Métrique | Valeur |
|----------|--------|
| **État** | **0% prêt** |
| **Risque** | Moyen |
| **Effort restant** | 6h |

Le répertoire `frontend/src/app/(app)/profile/` **n'existe pas**. Page entièrement à créer.

---

### US-3.1 — Tests E2E Playwright (Shiro, 4h, Must)

| Métrique | Valeur |
|----------|--------|
| **État** | 30% prêt |
| **Risque** | Moyen |
| **Effort restant** | 4h |

**Ce qui existe :** 6 specs E2E (auth, habits, dashboard, shop, character, api-health).

**Problèmes :** Sélecteurs fragiles qui ne matchent pas le HTML réel, bouton "Passer" référencé mais inexistant dans l'onboarding. Pas de test parcours complet, friends, combat, ni responsive mobile.

---

### US-3.3 — Polish Onboarding (Shiro, 8h, Must)

| Métrique | Valeur |
|----------|--------|
| **État** | 60% prêt |
| **Risque** | Moyen |
| **Effort restant** | 5h |

**Ce qui existe :** 4 étapes (nom, classe avec descriptions/bonus, apparence avec preview LPC multi-niveaux, confirmation), progress bar, animations.

**Manques :** Pas de protection refresh (données perdues si F5), pas d'étape "première habitude guidée" (spec), pas de message bienvenue dashboard.

---

### US-3.6 — Pages Coming Soon (Shiro, 3h, Must)

| Métrique | Valeur |
|----------|--------|
| **État** | 0% prêt |
| **Risque** | Faible |
| **Effort restant** | 3h |

Aucun composant `ComingSoon` n'existe. Tâche simple et bien définie.

---

## PROBLÈMES CROSS-CUTTING DÉTECTÉS

### Frontend — Bugs hors US

| ID | Description | Impact |
|----|-------------|--------|
| FE-007 | Dashboard = 100% mock data (mockHabits, mockTasks, stats en dur) | Crédibilité beta |
| FE-008 | Page Stats = 100% mock data (dates janvier 2024) | Crédibilité beta |
| FE-009 | React Query installé mais jamais utilisé (tout en fetch+useState) | Dette technique |
| FE-010 | Login/Register dupliquent access_token comme refresh_token | Auth cassée |
| FE-011 | Debug info (API URL) exposée en production sur la page login | Sécurité |
| FE-012 | Bouton Google OAuth présent mais non fonctionnel | UX confuse |

### Sécurité — Findings toujours présents

| Finding | Statut | Bloque Beta ? |
|---------|--------|---------------|
| SEC-01 : Routes admin sans auth | **TOUJOURS PRÉSENT** | **OUI** — beta users peuvent wiper les items |
| SEC-02 : Apple verify=False | Toujours présent | Non (OAuth désactivé) |
| SEC-03 : JWT secret = "change-me-in-production" | **TOUJOURS PRÉSENT** | **OUI** — si .env prod pas configuré |
| SEC-04 : Reset token en logs | **TOUJOURS PRÉSENT** | **OUI** — PII leak |
| SEC-05 : Token 30 jours | Toujours présent | Non (acceptable beta) |
| SEC-08 : Aucun rate limiting | Toujours présent | Oui (LLM abuse → coûts OpenAI) |

### Architecture — Findings toujours présents

| Finding | Statut | Impact |
|---------|--------|--------|
| BIZ-02 : 2 systèmes streak freeze | Toujours présent | Confusion, ghost fields en DB |
| BIZ-03 : Class bonuses non implémentés | Toujours présent | Combat déséquilibré (toutes classes identiques) |
| Deux systèmes DI (deps.py vs utils/dependencies.py) | Toujours présent | 2 libs JWT différentes |
| Sync services vs async routers | Toujours présent | Crash runtime si badges/combat activés |

---

## MATRICE READINESS PAR US

### Sprint 2 — Social + Combat PvP

| US | Assigné | Priorité | État | Risque | Effort restant | Verdict |
|----|---------|----------|------|--------|---------------|---------|
| US-2.1 Friends BE | Kuro | Must | 75% | Faible | 2h | ✅ Faisable |
| US-2.2 Friends FE | Shiro | Must | 75% | Moyen | 3h | ✅ Faisable (après fix cn()) |
| US-2.3 Leaderboard BE | Kuro | Must | 80% | Moyen | 3h | ✅ Faisable |
| US-2.4 Leaderboard FE | Shiro | Must | 80% | Faible | 2h | ✅ Faisable |
| US-2.5 Combat PvP BE | Kuro | Should | 55% | **ÉLEVÉ** | 10-14h | ⚠️ Risqué (>budget 12h) |
| US-2.6 Combat PvP FE | Shiro | Should | 15% | **ÉLEVÉ** | 12h | ⚠️ Risqué (rewrite complet) |
| US-2.7 Profil ami | Shiro | Must | 0% | Moyen | 6h | ✅ Faisable |
| US-2.8 Badges | Kuro | Must | 60% | **ÉLEVÉ** | 5-6h | ⚠️ Critique (jamais appelé) |

**Charge Sprint 2 :**
- Kuro : 2 + 3 + 10-14 + 5-6 = **20-25h** (budget : 28h + 7h marge) → OK si pas de surprise
- Shiro : 3 + 2 + 12 + 6 = **23h** (budget : 34h + 1h marge) → OK mais SERRÉ avec PvP
- Sans PvP : Kuro = 10-11h, Shiro = 11h → confortable

### Sprint 3 — Polish + Launch Beta

| US | Assigné | Priorité | État | Risque | Effort restant |
|----|---------|----------|------|--------|---------------|
| US-3.1 Tests BE | Kuro | Must | 50% | Moyen | 6-8h |
| US-3.1 Tests E2E | Shiro | Must | 30% | Moyen | 4h |
| US-3.2 Fix bugs | Both | Must | N/A | Élevé | 15h budget |
| US-3.3 Onboarding | Shiro | Must | 60% | Moyen | 5h |
| US-3.4 Backup | Kuro | Must | 60% | Faible | 1.5h |
| US-3.5 Monitoring | Kuro | Should | 50% | Moyen | 3h |
| US-3.6 Coming Soon | Shiro | Must | 0% | Faible | 3h |
| US-3.7 Guide | Ilane | Must | 0% | Faible | 2h |
| US-3.8 Deploy | Ilane+Kuro | Must | N/A | Moyen | 3h |

---

## PLAN D'ACTION PRIORISÉ

### 🔴 AVANT Sprint 2 (immédiat — ce week-end)

| # | Action | Responsable | Effort |
|---|--------|-------------|--------|
| 1 | Créer `frontend/src/lib/utils.ts` (cn + clsx + tailwind-merge) | Shiro | 5 min |
| 2 | Unifier les 2 classes Base (supprimer celle de database.py) | Kuro | 30 min |
| 3 | Générer migration Alembic pour les ~50 colonnes divergentes | Kuro | 2-4h |
| 4 | Convertir badge_service, xp_service, streak_service en async | Kuro | 4h |

### 🟡 PENDANT Sprint 2 (24-28 février)

| # | Action | Responsable | Contexte |
|---|--------|-------------|----------|
| 5 | Implémenter class bonuses dans Character model | Kuro | US-2.5 Go/No-Go |
| 6 | Fixer l'interface combat router/service (BUG-C1) | Kuro | US-2.5 |
| 7 | Corriger formules combat (HP, dodge, crit) pour matcher CDC | Kuro | US-2.5 |
| 8 | Intégrer `check_all_badges()` dans completions router | Kuro | US-2.8 |
| 9 | Ajouter gestion 401 (auto-logout ou refresh) dans auth store | Shiro | Transversal |
| 10 | Masquer bouton Google OAuth | Shiro | US-3.6 anticipé |
| 11 | Unifier les 2 systèmes de DI | Kuro | Qualité |
| 12 | Décider SQL-only vs Redis pour leaderboard | Kuro | US-2.3 |

### 🟢 Sprint 3 (3-7 mars)

| # | Action | Responsable |
|---|--------|-------------|
| 13 | Ajouter `Depends(require_admin)` sur toutes les routes admin | Kuro |
| 14 | Vérifier JWT secret en prod (.env) | Kuro |
| 15 | Supprimer le log du reset token | Kuro |
| 16 | Ajouter rate limiting sur /auth et /tasks (LLM) | Kuro |
| 17 | Remplacer mock data dashboard/stats par appels API | Shiro |
| 18 | Fixer login/register qui duplique access_token comme refresh_token | Shiro |

### ⚪ Post-beta (backlog)

- SEC-02 : Apple OAuth (feature désactivée)
- SEC-05/06 : Token durée / même secret (acceptable 10 users)
- BIZ-01 : Race condition shop (10 users = low risk)
- FE-02 : Tokens localStorage (XSS risk low pour beta)
- Migration vers React Query hooks
- Performance (N+1 queries, Redis caching)
- RBAC propre

---

## RECOMMANDATION STRATÉGIQUE : Go/No-Go PvP

Le combat PvP (US-2.5 + US-2.6) représente **22-26h de travail combiné** (10-14h BE + 12h FE) pour un budget de 24h.

**Arguments No-Go :**
- Le router backend CRASH si activé (interface incompatible)
- Le frontend est du PvE mock, pas du PvP — rewrite complet
- Les formules ne matchent pas le CDC
- 8 manques fonctionnels identifiés côté backend
- Shiro a déjà 1h de marge seulement
- Risque élevé de décaler le Sprint 3

**Arguments Go :**
- Le CombatService existe et la simulation fonctionne (modulo formules)
- Le modèle DB est complet
- Si Kuro fixe les 4 blockers pré-sprint ce week-end, il gagne du temps

**Ma recommandation : Préparer le No-Go, viser le Go.**
- Kuro fixe les blockers pré-sprint + commence le combat dès lundi
- Mercredi 26 : évaluation réaliste — si les 4 critères Go/No-Go ne sont pas remplis, No-Go immédiat
- Si No-Go : Shiro réinvestit 12h dans polish (onboarding, responsive, mock→API), Kuro renforce tests et badges

---

*Audit réalisé par Claude Opus 4.6 — 3 agents parallèles — 15 février 2026*
*Agents : backend-auditor, frontend-auditor, readiness-analyst*
*Cross-référencé avec : US/sprint2-kickoff.md, US/sprint3-kickoff.md, docs/audit-sprint1-claude.md*
