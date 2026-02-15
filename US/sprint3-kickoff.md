# 🚀 Sprint 3 — Polish + Launch Beta

**Dates** : 3 – 7 mars 2026
**Objectif** : Application propre, stable, zéro bug bloquant. Inviter 10 amis en beta.

**Prérequis** : Sprint 2 gate ✅ passée (parcours social complet, combat si Go).

---

## Rappel des décisions en vigueur

| # | Décision | Date | Statut |
|---|----------|------|--------|
| 1 | MVP Beta = core loop + social + combat si viable | 15 fév | ✅ Validé |
| 2 | LLM = OpenAI gpt-4o-mini | 15 fév | ✅ Validé |
| 3 | Shiro = frontend, Kuro = backend | 15 fév | ✅ Validé |
| 4 | Go/No-Go Combat PvP | 26 fév | ✅ ou ❌ (résolu) |

---

## Organisation de la semaine

| Jour | Événement |
|------|-----------|
| **Lundi 3** | Sprint kickoff. Shiro et Kuro lancent les tests E2E + fix bugs Sprint 2. |
| **Mercredi 5 matin** | Checkpoint mi-sprint (15 min). Tous les bugs bloquants doivent être résolus. |
| **Jeudi 6** | **Feature freeze.** Plus aucun changement fonctionnel. Uniquement du fix et du polish. |
| **Vendredi 7 matin** | Test final complet (Ilane + Shiro + Kuro). |
| **Vendredi 7 après-midi** | **Deploy prod + envoi invitations aux 10 beta-testeurs.** 🎉 |

**Standup async quotidien** — même format que les sprints précédents.

---

## Charge prévisionnelle

| Dev | US assignées | Heures estimées | Marge |
|-----|-------------|-----------------|-------|
| **Kuro** | 3.1 (co), 3.2 (co), 3.4, 3.5 | ~21h | ~14h marge (buffer bug fixes) |
| **Shiro** | 3.1 (co), 3.2 (co), 3.3, 3.6 | ~26h | ~9h marge |
| **Ilane** | 3.7, 3.8 (co) | ~5h | |

> La marge est **volontairement large** cette semaine. C'est le sprint de stabilisation — les imprévus sont le scénario normal, pas l'exception. Toute heure non utilisée en fix bugs va dans du polish supplémentaire.

---

## User Stories détaillées

---

### US-3.1 — Tests E2E complets

**Assigné** : Shiro + Kuro (travail conjoint)
**Estimation** : 8h (4h chacun)
**Priorité** : 🔴 Must
**Dépendances** : Sprint 2 terminé

#### Contexte

Des tests E2E Playwright existent déjà (auth, habits, dashboard, shop, character, api-health — tous passent au 10 février). Mais les features Social et Combat n'ont **pas de tests E2E**. Et les tests existants n'ont peut-être pas été mis à jour après les fix du Sprint 1.

L'objectif est d'avoir une suite de tests E2E qui couvre **tout le parcours beta** de bout en bout.

#### Répartition du travail

**Kuro** — Tests backend (pytest) :
1. Vérifier que tous les tests existants passent encore (régression)
2. Compléter les tests friends : add, accept, reject, list, delete
3. Compléter les tests leaderboard : classement avec 2+ users
4. Compléter les tests combat (si Go PvP) : challenge, history, validations
5. Compléter les tests badges : auto-attribution sur events
6. Résoudre les 12 tests skipped du Sprint 1 (si pas déjà fait)

**Shiro** — Tests E2E (Playwright) :
1. Mettre à jour les tests existants si des flows ont changé
2. Ajouter un test E2E pour le parcours complet :
   ```
   Register → Onboarding → Créer 1 habitude → Compléter → 
   Vérifier XP/Coins → Acheter un item → Équiper → 
   Ajouter un ami → Voir le leaderboard
   ```
3. Ajouter un test E2E pour le flow friends (ajouter un ami via code)
4. Ajouter un test E2E pour le combat (si Go PvP)
5. Vérifier le test responsive : exécuter tous les tests en viewport mobile (375×812)

#### Comment exécuter les tests

```bash
# Backend
docker compose exec backend pytest -v --tb=short

# Frontend E2E
cd frontend
npm run e2e              # Headless
npm run e2e:headed       # Avec navigateur visible
npm run e2e:report       # Rapport HTML
```

#### Critères d'acceptation

- [ ] **Tous** les tests backend passent (0 failed, 0 skipped non justifié)
- [ ] Les tests E2E couvrent : auth, habits, completions, shop, character, friends, leaderboard
- [ ] Le test E2E du parcours complet (register → leaderboard) passe en headless
- [ ] Si Go PvP : le test E2E du combat passe
- [ ] Les tests E2E passent en viewport mobile (375×812)
- [ ] Le rapport Playwright HTML est généré et consultable

---

### US-3.2 — Fix bugs Sprint 2

**Assigné** : Shiro + Kuro
**Estimation** : 15h (répartition dynamique)
**Priorité** : 🔴 Must
**Dépendances** : US-3.1 (les tests révèlent les bugs)

#### Contexte

C'est la US la plus imprévisible mais la plus importante. Après 2 sprints de développement intensif, il y aura des bugs. Cette US est un **budget temps dédié** au fix.

#### Processus de triage

1. **Lundi matin** : Shiro et Kuro font un run complet de l'app (2 comptes, tout le parcours)
2. Chaque bug trouvé est noté avec :
   - **Sévérité** : 🔴 Bloquant / 🟡 Gênant / 🟢 Cosmétique
   - **Description** : URL, action, résultat attendu vs obtenu
   - **Screenshot** si bug visuel
3. Les bugs sont triés par sévérité :
   - 🔴 **Bloquant** = empêche un beta-testeur d'utiliser l'app → fix immédiat
   - 🟡 **Gênant** = UX dégradée mais contournable → fix si temps disponible
   - 🟢 **Cosmétique** = visuel, pas fonctionnel → backlog post-beta

#### Répartition

- **Kuro** fixe les bugs backend (erreurs 500, données incohérentes, performance)
- **Shiro** fixe les bugs frontend (UI cassée, responsive, erreurs JS, UX)
- Si un bug est cross-stack → ils se coordonnent immédiatement (pas de ping-pong)

#### Bugs anticipés (à vérifier en priorité)

| Zone | Risque | Ce qui pourrait casser |
|------|--------|------------------------|
| Onboarding | Moyen | Si la création de personnage échoue, l'utilisateur est bloqué |
| Completions | Moyen | XP/Coins non attribués, streak non mis à jour |
| Shop | Faible | Achat qui débite mais n'ajoute pas l'item |
| Friends | Moyen | Demande qui ne s'affiche pas, accept qui ne fonctionne pas |
| Leaderboard | Moyen | Données incohérentes, utilisateur absent du classement |
| Combat (si Go) | Élevé | Crash de la simulation, récompenses non distribuées |
| Mobile | Moyen | Éléments qui débordent, boutons non cliquables |
| Celery/LLM | Moyen | Évaluation IA qui ne revient jamais, worker down |

#### Critères d'acceptation

- [ ] Tous les bugs 🔴 Bloquants sont résolus
- [ ] Au moins 80% des bugs 🟡 Gênants sont résolus
- [ ] Les bugs 🟢 Cosmétiques restants sont documentés dans un fichier `known-issues.md`
- [ ] Après fix, le parcours complet (register → combat) passe sans erreur
- [ ] Les tests E2E passent toujours après les fix (pas de régression)

---

### US-3.3 — Polish onboarding

**Assigné** : Shiro
**Estimation** : 8h
**Priorité** : 🔴 Must
**Dépendances** : Aucune

#### Contexte

L'onboarding est la **première impression** des beta-testeurs. Si c'est confus ou buggé, ils ne reviendront pas. L'onboarding actuel fonctionne (register → créer personnage → classe + genre) mais peut être amélioré.

#### Ce qui existe

- Page `/register` : email, username, password
- Page `/onboarding` : nom du personnage, choix de classe (5 classes), choix de genre (M/F)
- Preview d'évolution du personnage (niveaux 1, 5, 10, 15, 20)
- Après onboarding → redirect vers `/dashboard`

#### Ce qui doit être amélioré

**1. Flow register → onboarding plus fluide**
- Après register, redirection automatique vers onboarding (vérifier que ça ne se bloque pas)
- Si l'utilisateur refresh pendant l'onboarding, il ne perd pas sa progression
- Si l'utilisateur est déjà onboardé et revient sur `/onboarding` → redirect vers `/dashboard`

**2. Améliorer la page d'onboarding**
- Étape 1 : "Bienvenue ! Crée ton personnage" — Nom du personnage
- Étape 2 : Choix de la classe avec description de chaque classe et bonus de stats
  ```
  ⚔️ Guerrier  — +3 Force, +2 Endurance
  🧙 Mage      — +3 Intelligence, +2 Charisme
  🏹 Ranger    — +3 Agilité, +2 Force
  🛡️ Paladin   — +3 Endurance, +2 Charisme
  🗡️ Assassin  — +3 Agilité, +2 Intelligence
  ```
- Étape 3 : Choix du genre + preview du personnage
- Étape 4 : "Crée ta première habitude" — suggestion d'habitudes populaires + possibilité de créer la sienne
- Bouton "Passer" sur l'étape 4 (on ne force pas)

**3. Première habitude guidée (étape 4)**
- Proposer 3-5 habitudes populaires en cartes cliquables :
  - 🧘 Méditer 10 minutes
  - 💧 Boire 2L d'eau
  - 📚 Lire 30 minutes
  - 🏃 Faire du sport
  - 😴 Dormir 8 heures
- L'utilisateur en sélectionne une (ou crée la sienne)
- Après sélection → "Bravo ! Ta première habitude est créée. Direction le dashboard !"

**4. Message de bienvenue sur le dashboard**
- Au premier accès après onboarding, afficher un message/tooltip :
  "Complète ta première habitude pour gagner de l'XP ! 💪"
- Le message disparaît après la première complétion ou dismiss

#### Tâches concrètes

1. Vérifier le flow register → onboarding (pas de page blanche, pas de boucle)
2. Ajouter la protection contre le refresh (état en localStorage ou query param)
3. Ajouter les descriptions des classes avec bonus de stats
4. Créer l'étape 4 "Première habitude" avec les suggestions
5. Ajouter le message de bienvenue au dashboard (conditionnel : `user.total_completions === 0`)
6. Tester le flow complet sur mobile (chaque étape doit être scrollable et les boutons visibles)
7. Tester le cas "register puis fermer le navigateur puis revenir" → l'utilisateur doit pouvoir reprendre

#### Critères d'acceptation

- [ ] Register → onboarding → dashboard fonctionne sans accroc
- [ ] Un refresh pendant l'onboarding ne perd pas la progression
- [ ] Un utilisateur déjà onboardé qui visite `/onboarding` est redirigé vers `/dashboard`
- [ ] Les 5 classes affichent nom + description + bonus de stats
- [ ] L'étape "Première habitude" propose 3-5 suggestions + option custom
- [ ] Le dashboard affiche un message de bienvenue au premier accès
- [ ] Le flow complet est testable sur mobile sans problème de scroll ou de boutons coupés
- [ ] L'ensemble prend moins de 2 minutes pour un nouvel utilisateur

---

### US-3.4 — Backup base de données

**Assigné** : Kuro
**Estimation** : 2h
**Priorité** : 🔴 Must
**Dépendances** : Aucune

#### Contexte

Avant d'inviter 10 beta-testeurs, on doit avoir un **système de backup fonctionnel**. Si la base crash, on ne peut pas perdre les données des utilisateurs. Un script existe déjà dans la documentation (`backup.sh`) mais il n'a jamais été configuré en automatique.

#### Tâches concrètes

1. **Créer le script `scripts/backup.sh`** sur le VPS :
   ```bash
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   BACKUP_DIR="/home/debian/backups"
   BACKUP_FILE="$BACKUP_DIR/habit_tracker_${DATE}.sql.gz"
   
   mkdir -p $BACKUP_DIR
   
   docker compose exec -T habit-postgres pg_dump -U habit_user habit_tracker | gzip > $BACKUP_FILE
   
   # Garder les 7 derniers backups seulement
   ls -t $BACKUP_DIR/habit_tracker_*.sql.gz | tail -n +8 | xargs rm -f
   
   echo "$(date) - Backup créé: $BACKUP_FILE ($(du -h $BACKUP_FILE | cut -f1))" >> $BACKUP_DIR/backup.log
   ```

2. **Configurer un cron** pour backup quotidien à 3h du matin :
   ```bash
   crontab -e
   # Ajouter :
   0 3 * * * /home/debian/habit-tracker/scripts/backup.sh
   ```

3. **Tester la restauration** :
   - Faire un backup
   - Créer un utilisateur de test
   - Restaurer le backup
   - Vérifier que l'utilisateur de test n'existe plus (le backup est d'avant)
   - Re-créer l'utilisateur

4. **Documenter** la procédure de restauration :
   ```bash
   # Restauration
   gunzip < /home/debian/backups/habit_tracker_XXXXXXXX.sql.gz | \
     docker compose exec -T habit-postgres psql -U habit_user habit_tracker
   ```

#### Critères d'acceptation

- [ ] Le script `backup.sh` existe et fonctionne (testé manuellement)
- [ ] Un backup est créé et fait moins de 10 Mo (base quasi vide)
- [ ] Le cron est configuré pour 3h du matin quotidien
- [ ] Les anciens backups (>7 jours) sont automatiquement supprimés
- [ ] La restauration a été testée avec succès au moins une fois
- [ ] La procédure de backup/restore est documentée dans un fichier `BACKUP.md`

---

### US-3.5 — Monitoring fonctionnel

**Assigné** : Kuro
**Estimation** : 4h
**Priorité** : 🟡 Should
**Dépendances** : Aucune

#### Contexte

Pendant la beta, on doit pouvoir savoir **rapidement** si quelque chose est cassé. On n'a pas besoin d'un Grafana complet — on a besoin d'un minimum de visibilité.

#### Ce qui existe déjà

- Endpoint `GET /api/health` → health check basique
- Endpoint `GET /api/metrics` → métriques Prometheus
- Structlog JSON en backend → logs lisibles
- Dashboard monitoring à `monitoring.apps.ilanewep.cloud` (état inconnu)

#### Ce qu'on veut pour la beta

**1. Script de health check automatique**

Un script qui tourne toutes les 5 minutes et vérifie :
- Le backend répond (`/api/health` → 200)
- Le frontend répond (page d'accueil → 200)
- PostgreSQL est up (via le health check Docker)
- Redis est up (PING → PONG)
- Celery worker est actif (au moins 1 worker up)

Si un check échoue → écrire dans un fichier log + optionnellement envoyer un message (webhook Discord ou simple email si configuré).

**2. Dashboard de status simple**

Créer un endpoint `GET /api/health/detailed` qui retourne :
```json
{
  "status": "healthy",
  "checks": {
    "database": { "status": "up", "response_time_ms": 12 },
    "redis": { "status": "up", "response_time_ms": 3 },
    "celery": { "status": "up", "workers": 1 },
    "llm": { "status": "configured", "provider": "openai" }
  },
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "active_users_24h": 5
}
```

**3. Alerting basique**

Configurer un cron ou un script qui vérifie `/api/health/detailed` et envoie une alerte si un composant est down. Même un simple script bash + webhook Discord suffit.

#### Tâches concrètes

1. Créer l'endpoint `GET /api/health/detailed` avec les checks DB, Redis, Celery, LLM
2. Créer le script de monitoring `scripts/monitor.sh` :
   ```bash
   #!/bin/bash
   STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://habit.apps.ilanewep.cloud/api/health)
   if [ "$STATUS" != "200" ]; then
       echo "$(date) - ALERT: Backend down (HTTP $STATUS)" >> /home/debian/monitor.log
       # Optionnel : webhook Discord / email
   fi
   ```
3. Configurer le cron (toutes les 5 minutes)
4. Vérifier que les logs backend sont accessibles et lisibles (`docker logs habit-backend`)
5. Documenter les commandes de debug dans `MONITORING.md`

#### Critères d'acceptation

- [ ] `GET /api/health/detailed` retourne le status de tous les composants
- [ ] Le script de monitoring tourne toutes les 5 minutes
- [ ] Si le backend est down, une ligne est écrite dans le fichier de log
- [ ] Les logs backend sont consultables avec `docker logs habit-backend -f`
- [ ] Un fichier `MONITORING.md` documente : comment consulter les logs, comment vérifier l'état des services, comment redémarrer un service

---

### US-3.6 — Pages "Coming Soon" restantes

**Assigné** : Shiro
**Estimation** : 3h
**Priorité** : 🔴 Must
**Dépendances** : Décision Go/No-Go PvP connue

#### Contexte

Toutes les features non implémentées qui sont visibles dans la navigation doivent afficher un écran "Coming Soon" propre au lieu d'une page vide, cassée, ou en erreur. C'est essentiel pour la première impression des beta-testeurs.

#### Pages à traiter

**Systématiquement "Coming Soon"** (features exclues de la beta) :

| Page/Feature | Route | Ce qu'il faut |
|-------------|-------|---------------|
| Timer intégré | (pas de route) | Masquer le bouton/lien si visible |
| Notifications | `/settings` section notifs | Label "Coming Soon" à côté des toggles |
| Mode Vacances | `/settings` | Label "Coming Soon" |
| Insights IA | `/stats` section insights | Bloc "Coming Soon — L'IA analysera vos tendances bientôt" |
| Export PDF | `/stats` | Bouton export grisé + tooltip "Bientôt disponible" |

**Conditionnel (si No-Go PvP)** :

| Page/Feature | Route | Ce qu'il faut |
|-------------|-------|---------------|
| Combat PvP | `/combat` | Page "Coming Soon" avec illustration fun |
| Bouton Défier | `/friends`, `/profile/{id}` | Bouton grisé ou masqué |

#### Design "Coming Soon"

Chaque page Coming Soon doit avoir :
- Un icône ou illustration (emoji OK, pas besoin d'assets custom)
- Un titre : "🚧 Bientôt disponible"
- Un sous-titre spécifique à la feature : ex. "Le combat PvP entre amis arrive bientôt !"
- Un bouton "Retour au dashboard"
- Le tout centré, sobre, cohérent avec le design de l'app

#### Tâches concrètes

1. Lister toutes les routes/liens visibles dans la navigation qui mènent à des features non implémentées
2. Créer un composant réutilisable `ComingSoon` avec props : `title`, `description`, `icon`
3. Appliquer le composant sur chaque page concernée
4. Masquer ou griser les boutons qui déclenchent des features non disponibles
5. Vérifier que la sidebar/navigation ne contient pas de liens morts
6. Tester sur mobile

#### Critères d'acceptation

- [ ] Aucun lien dans la navigation ne mène à une page blanche ou en erreur
- [ ] Chaque feature non disponible affiche un écran "Coming Soon" propre
- [ ] Les boutons de features non disponibles sont grisés ou masqués
- [ ] La page "Coming Soon" est cohérente visuellement avec le reste de l'app
- [ ] Responsive mobile OK
- [ ] Si No-Go PvP : la page `/combat` affiche "Coming Soon" et le bouton "Défier" est masqué

---

### US-3.7 — Guide beta-testeur

**Assigné** : Ilane
**Estimation** : 2h
**Priorité** : 🔴 Must
**Dépendances** : App stable (dépend de US-3.1, 3.2, 3.3)

#### Contexte

Les 10 beta-testeurs sont des amis. Ils ne sont pas développeurs. Ils ont besoin d'un guide simple pour :
1. Savoir ce que c'est
2. Savoir comment y accéder
3. Savoir quoi faire
4. Savoir comment signaler un bug

#### Contenu du guide

**Format** : un message long (Discord, WhatsApp, ou email) + optionnellement une page web simple.

**Structure du guide** :

```markdown
# 🎮 HabitQuest — Guide Beta-testeur

## C'est quoi ?
HabitQuest est un habit tracker gamifié. Tu crées des habitudes, 
tu les complètes chaque jour, et tu fais progresser ton personnage RPG.
Plus tu es régulier, plus tu gagnes d'XP, tu montes de niveau, 
et tu débloques des équipements.

## Comment y accéder ?
1. Va sur : https://habit.apps.ilanewep.cloud
2. Crée ton compte (email + mot de passe)
3. Crée ton personnage (choisis ton nom, ta classe, ton apparence)
4. C'est parti !

## Quoi faire en premier ?
1. ✅ Crée 2-3 habitudes que tu fais vraiment (boire de l'eau, méditer, lire...)
2. ✅ Chaque jour, complète tes habitudes → tu gagnes XP et Coins
3. 🛍️ Avec tes Coins, achète des équipements dans la boutique
4. ⚔️ Équipe ton personnage et monte de niveau
5. 👥 Ajoute tes amis avec leur code ami → comparez-vous sur le leaderboard
6. 🏆 [Si PvP Go] Défie tes amis en combat !

## Mon code ami
Chacun a un code ami unique visible dans la page Amis.
Partage-le pour que tes potes t'ajoutent !

## Un bug ? Un problème ?
Envoie-moi un message avec :
- 📸 Screenshot
- 📝 Ce que tu faisais quand ça a buggé
- 📱 Sur quel appareil / navigateur

## Ce qui n'est pas encore dispo
- Notifications push
- Connexion Google/Apple
- Certaines features marquées "Coming Soon"

Merci de tester ! Vos retours m'aident énormément 🙏
```

#### Critères d'acceptation

- [ ] Le guide est rédigé en langage simple (pas de jargon technique)
- [ ] Il contient : lien d'accès, étapes d'inscription, quoi faire, comment signaler un bug
- [ ] Il est prêt à être copié-collé dans un message Discord/WhatsApp
- [ ] Le flow décrit dans le guide correspond à l'état réel de l'app (pas de feature qui n'existe pas)

---

### US-3.8 — Deploy prod + inviter 10 amis

**Assigné** : Ilane + Kuro
**Estimation** : 3h
**Priorité** : 🔴 Must
**Dépendances** : Toutes les autres US du Sprint 3

#### Contexte

C'est la dernière étape. L'app est stable, testée, documentée. On deploy la version finale et on invite les beta-testeurs.

#### Checklist de deploy

**Kuro — préparation serveur (1h) :**

1. [ ] `git pull` sur le VPS
2. [ ] `docker compose build` — rebuild frontend et backend
3. [ ] `docker compose up -d` — démarrage
4. [ ] `docker compose exec backend alembic upgrade head` — migrations (si nouvelles)
5. [ ] `docker compose exec backend python scripts/seed_badges.py` — vérifier que les badges sont seeded
6. [ ] `docker compose exec backend python scripts/seed_items.py` — vérifier que les items shop sont seeded
7. [ ] Vérifier `GET /api/health` → 200
8. [ ] Vérifier `GET /api/health/detailed` → tous les composants "up"
9. [ ] Vérifier que le backup cron est actif (`crontab -l`)
10. [ ] Vérifier que le monitoring tourne
11. [ ] Faire un backup manuel avant d'ouvrir aux beta-testeurs

**Ilane — vérification app (1h) :**

1. [ ] Créer un compte frais → parcours complet sans bug
2. [ ] Vérifier le responsive sur son propre téléphone
3. [ ] Vérifier que les seeds sont corrects (38 items en boutique, 75 badges)
4. [ ] Vérifier que l'évaluation IA fonctionne (créer une tâche avec `use_ai_evaluation: true`)
5. [ ] Vérifier que les env vars sensibles sont en place (`OPENAI_API_KEY`, `SECRET_KEY`, etc.)

**Ilane — invitations (1h) :**

1. [ ] Envoyer le guide beta-testeur aux 10 amis (Discord/WhatsApp/email)
2. [ ] Inclure le lien : https://habit.apps.ilanewep.cloud
3. [ ] Demander à chacun de créer un compte et d'ajouter les autres en amis (partager les friend codes)
4. [ ] Créer un canal/groupe dédié pour les retours beta
5. [ ] Poster un message de bienvenue dans le canal avec les instructions de base

#### Critères d'acceptation

- [ ] L'app est déployée et accessible sur https://habit.apps.ilanewep.cloud
- [ ] Health check OK, monitoring OK, backup OK
- [ ] Le guide beta-testeur est envoyé aux 10 amis
- [ ] Un canal de retours beta est créé
- [ ] Au moins 3 beta-testeurs ont créé un compte dans les 24h suivant l'invitation

---

## Sprint 3 — Gate de fin de sprint (vendredi 7 mars)

### Test final complet

**Qui** : Ilane + Shiro + Kuro
**Quand** : Vendredi 7 mars, 10h
**Durée** : 1h maximum

#### Scénario de test

Avec un **compte neuf** (jamais utilisé avant) :

1. Register (email + password)
2. Onboarding (personnage + classe + genre)
3. Créer 2 habitudes
4. Compléter les 2 habitudes → vérifier XP et Coins reçus
5. Aller en boutique → acheter un item
6. Aller dans l'inventaire → équiper l'item
7. Vérifier que le personnage LPC porte l'item
8. Créer une tâche → vérifier que l'évaluation IA se lance
9. Ajouter un ami via friend_code
10. L'ami accepte la demande
11. Voir l'ami dans la liste d'amis
12. Voir le leaderboard avec l'ami
13. Consulter le profil de l'ami
14. **Si Go PvP** : lancer un combat → voir le résultat
15. Vérifier qu'au moins 1 badge est débloqué
16. Vérifier tout ça sur mobile (iPhone ou Android)

#### Critères Gate Pass

- [ ] Les 16 étapes (ou 15 si No-Go PvP) passent sans erreur
- [ ] Pas d'erreur 500 dans les logs backend pendant tout le test
- [ ] Pas de console error côté frontend
- [ ] L'app est responsive et utilisable sur mobile
- [ ] Le temps total pour un nouveau utilisateur de faire tout le parcours : < 10 minutes

**Si la gate ne passe pas** → on ne lance PAS la beta. On fixe les bugs pendant le week-end et on relance lundi 10 mars.

---

## Post-beta : ce qui suit (backlog)

Pour info, voici ce qui a été explicitement exclu de la beta et qui pourra être priorisé après les retours des testeurs :

| Feature | Priorité post-beta |
|---------|-------------------|
| OAuth Google/Apple | Haute (facilite l'inscription) |
| Notifications push | Haute (rétention) |
| Rappels d'habitudes | Moyenne |
| Mode Vacances | Moyenne |
| Insights IA | Basse |
| Timer intégré | Basse |
| Widget iOS | Basse (nécessite app native) |
| Pets / Familiers | Basse |
| Weekly challenges | Basse |
| Export PDF | Basse |
| Light mode | Basse |

Les retours des 10 beta-testeurs pendant les 2 premières semaines guideront la priorisation.

---

## Résumé visuel

```
Lundi 3          Mardi 4         Mercredi 5       Jeudi 6          Vendredi 7
────────────────────────────────────────────────────────────────────────────────
KURO:
  US-3.1          US-3.2          US-3.4           US-3.5           US-3.8
  Tests BE        Fix bugs BE     Backup DB        Monitoring       Deploy
  + US-3.2 start                  + US-3.5 start                    + support

SHIRO:
  US-3.1          US-3.2          US-3.3           US-3.6           Fix last
  Tests E2E       Fix bugs FE     Polish           Coming Soon      bugs
  + US-3.2 start                  onboarding       pages            + support

ILANE:
                                                   US-3.7           US-3.8
                                                   Guide beta       Deploy
                                                                    + Invitations

                                  ⚡ Checkpoint                     
                                  (mercredi AM)    🧊 FEATURE
                                                   FREEZE           🏁 GATE
                                                   (jeudi)          + LAUNCH 🎉
                                                                    (vendredi)
```
