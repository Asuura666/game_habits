# 🏃 Sprint 2 — Social + Combat PvP

**Dates** : 24 – 28 février 2026
**Objectif** : Les 10 beta-testeurs peuvent interagir entre eux : ajouter des amis, se comparer sur le leaderboard, et (si viable) se défier en combat PvP.

**Prérequis** : Sprint 1 gate ✅ passée (parcours core loop sans bug, test du 21 février).

---

## Rappel des décisions en vigueur

| # | Décision | Date |
|---|----------|------|
| 1 | MVP Beta = core loop + social + combat si viable | 15 fév |
| 2 | LLM = OpenAI gpt-4o-mini | 15 fév |
| 3 | Shiro = frontend, Kuro = backend | 15 fév |
| 4 | **Go/No-Go Combat PvP : mercredi 26 fév** | 15 fév |

---

## Organisation de la semaine

| Jour | Événement |
|------|-----------|
| **Lundi 24** | Sprint kickoff. Shiro et Kuro démarrent US-2.1 à 2.4 (Social). |
| **Mercredi 26 matin** | Checkpoint mi-sprint (15 min). Friends + Leaderboard doivent être testables. |
| **Mercredi 26 après-midi** | **Go/No-Go PvP.** Si le backend combat passe les tests → Go. Sinon → "Coming Soon" et on réinvestit dans le polish. |
| **Vendredi 28** | Sprint review. Test collectif : 2 comptes, parcours social complet + combat si Go. |

**Standup async quotidien** — Shiro et Kuro postent chaque matin :
```
✅ Fait hier :
🎯 Prévu aujourd'hui :
🚧 Bloqué par :
```

---

## Charge prévisionnelle

| Dev | US assignées | Heures estimées | Marge |
|-----|-------------|-----------------|-------|
| **Kuro** | 2.1, 2.3, 2.5, 2.8 | ~28h | ~7h marge |
| **Shiro** | 2.2, 2.4, 2.6, 2.7 | ~34h | ~1h marge |

> ⚠️ Shiro est chargé. Si le Go PvP est confirmé mercredi, Kuro doit avoir fini ses US backend pour pouvoir aider Shiro sur le frontend combat si besoin.

---

## User Stories détaillées

---

### US-2.1 — Friends : flow backend complet

**Assigné** : Kuro
**Estimation** : 6h
**Priorité** : 🔴 Must
**Dépendances** : Aucune (friends router + model existent déjà)

#### Contexte technique

Le backend social existe déjà partiellement :
- **Modèle `Friendship`** en DB : `requester_id`, `addressee_id`, `status` (pending/accepted/rejected/blocked)
- **Router `friends.py`** avec les endpoints de base
- **Contrainte DB** : `uq_friendship_pair` + `ck_not_self_friend`
- Chaque user a un `friend_code` unique (généré à l'inscription)

Le travail ici est de **vérifier que tout fonctionne de bout en bout** et de **corriger les bugs/manques**.

#### Endpoints concernés

| Endpoint | Méthode | Ce qu'il doit faire |
|----------|---------|---------------------|
| `GET /api/friends` | GET | Retourner la liste d'amis acceptés avec niveau, streak, avatar |
| `GET /api/friends/requests` | GET | Retourner les demandes en attente (reçues + envoyées) |
| `POST /api/friends/add` | POST | Envoyer une demande via `friend_code`. Valider : code existe, pas soi-même, pas déjà ami, pas déjà demande en cours, max 10 demandes en attente |
| `POST /api/friends/{id}/accept` | POST | Accepter une demande. Vérifier que `id` est bien une demande reçue par le current_user et en status `pending` |
| `POST /api/friends/{id}/reject` | POST | Refuser une demande. Mêmes vérifs |
| `DELETE /api/friends/{id}` | DELETE | Supprimer un ami (les deux côtés). Supprimer la relation, pas soft delete |

#### Tâches concrètes

1. Lancer les tests existants sur le module friends → lister ce qui passe/casse
2. Vérifier que `POST /api/friends/add` valide correctement le `friend_code` (pas d'erreur 500 si code invalide)
3. Vérifier que la liste d'amis (`GET /api/friends`) retourne les infos utiles : `username`, `level`, `current_streak`, `avatar_url`, `last_activity_date`
4. Vérifier les cas limites : demande à soi-même, double demande, demande à un utilisateur déjà ami
5. Vérifier que le rate limit de 10 demandes en attente max est appliqué
6. Écrire/compléter les tests unitaires pour chaque endpoint (minimum 1 test positif + 1 test négatif par endpoint)

#### Critères d'acceptation

- [ ] `POST /api/friends/add` avec un `friend_code` valide crée une relation `pending`
- [ ] `POST /api/friends/add` avec un code invalide retourne 404
- [ ] `POST /api/friends/add` avec son propre code retourne 400
- [ ] `POST /api/friends/add` quand déjà ami retourne 409
- [ ] `POST /api/friends/{id}/accept` passe le status à `accepted`
- [ ] `GET /api/friends` retourne uniquement les amis `accepted` avec username, level, streak, avatar
- [ ] `GET /api/friends/requests` retourne les demandes `pending` (reçues et envoyées séparées)
- [ ] `DELETE /api/friends/{id}` supprime la relation des deux côtés
- [ ] Tous les tests passent (`pytest tests/test_friends.py -v`)

---

### US-2.2 — Friends : flow frontend complet

**Assigné** : Shiro
**Estimation** : 8h
**Priorité** : 🔴 Must
**Dépendances** : US-2.1 (backend friends doit être stable)

#### Contexte technique

La page `/friends` existe déjà dans le frontend mais l'UI est minimale. Il faut la rendre fonctionnelle et agréable pour la beta.

#### Pages et composants

**Page `/friends`** — 3 onglets ou sections :

1. **Mes amis** — Liste des amis acceptés
   - Chaque ami affiche : avatar (LPC ou initiales), username, niveau, streak actuel
   - Bouton "Défier" (grisé si combat désactivé, actif si Go PvP)
   - Bouton "Voir profil"
   - Bouton "Supprimer" (avec confirmation)

2. **Demandes** — Demandes reçues et envoyées
   - Demandes reçues : boutons "Accepter" / "Refuser"
   - Demandes envoyées : label "En attente" + bouton "Annuler"

3. **Ajouter un ami** — Formulaire
   - Champ texte pour saisir un `friend_code`
   - Afficher son propre `friend_code` avec un bouton "Copier"
   - Feedback : succès ("Demande envoyée !"), erreur ("Code invalide", "Déjà ami", etc.)
   - Afficher le nombre de demandes en attente si > 0

#### Appels API

```typescript
// Hooks à créer ou compléter
useFriends()        → GET /api/friends
useFriendRequests() → GET /api/friends/requests
addFriend(code)     → POST /api/friends/add
acceptFriend(id)    → POST /api/friends/{id}/accept
rejectFriend(id)    → POST /api/friends/{id}/reject
removeFriend(id)    → DELETE /api/friends/{id}
```

#### Tâches concrètes

1. Restructurer la page `/friends` avec les 3 sections (onglets ou accordion)
2. Créer le composant `FriendCard` (avatar, username, level, streak, actions)
3. Créer le composant `FriendRequestCard` (reçue vs envoyée, actions)
4. Implémenter le formulaire "Ajouter un ami" avec validation et feedback
5. Afficher le `friend_code` de l'utilisateur avec bouton copier (navigator.clipboard)
6. Ajouter les états de chargement (skeleton) et les états vides ("Aucun ami encore")
7. Gérer les erreurs API avec des toasts/messages explicites
8. Vérifier le responsive mobile (la page doit être utilisable sur iPhone)

#### Critères d'acceptation

- [ ] La page `/friends` affiche la liste d'amis avec avatar, username, niveau, streak
- [ ] On peut ajouter un ami via son `friend_code` — feedback succès ou erreur affiché
- [ ] Le `friend_code` de l'utilisateur est visible et copiable en un clic
- [ ] Les demandes reçues sont visibles avec boutons Accepter / Refuser fonctionnels
- [ ] Les demandes envoyées sont visibles avec label "En attente"
- [ ] On peut supprimer un ami (avec popup de confirmation)
- [ ] L'état vide affiche un message encourageant ("Invite tes amis !")
- [ ] La page est responsive et utilisable sur mobile
- [ ] Pas de console error en usage normal

---

### US-2.3 — Leaderboard : backend fiable

**Assigné** : Kuro
**Estimation** : 6h
**Priorité** : 🔴 Must
**Dépendances** : US-2.1 (le leaderboard filtre par amis, donc la relation doit être en place)

#### Contexte technique

Le leaderboard utilise Redis Sorted Sets pour les classements. Le `LeaderboardService` existe déjà. Les endpoints sont :

| Endpoint | Description |
|----------|-------------|
| `GET /api/leaderboard/xp/weekly` | Top XP cette semaine (amis uniquement) |
| `GET /api/leaderboard/xp/monthly` | Top XP ce mois (amis uniquement) |
| `GET /api/leaderboard/streak` | Top streak actuel (amis uniquement) |

Le travail est de **vérifier la fiabilité des données** et de **s'assurer que le leaderboard ne montre que les amis + soi-même**.

#### Tâches concrètes

1. Vérifier que le `LeaderboardService` met bien à jour les sorted sets à chaque gain d'XP et à chaque mise à jour de streak
2. Vérifier le filtrage : le leaderboard ne doit retourner que les amis `accepted` + l'utilisateur courant. Pas de leaderboard global pour la beta (privacy first)
3. Vérifier le format de réponse : chaque entrée doit contenir `username`, `level`, `score` (XP ou streak), `rank`, `avatar_url`
4. Vérifier le reset hebdomadaire : le classement XP weekly doit se réinitialiser le lundi (via Celery Beat ou TTL Redis)
5. Vérifier le cas "aucun ami" : retourner une liste avec juste l'utilisateur courant
6. Écrire les tests : au moins 2 users amis, vérifier que le classement est correct
7. Vérifier que la position de l'utilisateur courant est indiquée même s'il n'est pas dans le top

#### Critères d'acceptation

- [ ] `GET /api/leaderboard/xp/weekly` retourne le classement XP de la semaine pour les amis + soi
- [ ] `GET /api/leaderboard/xp/monthly` retourne le classement XP du mois pour les amis + soi
- [ ] `GET /api/leaderboard/streak` retourne le classement streak pour les amis + soi
- [ ] Chaque entrée contient : `username`, `level`, `score`, `rank`, `avatar_url`
- [ ] Un utilisateur sans ami ne voit que lui-même dans le leaderboard
- [ ] Les données sont cohérentes (l'XP affiché dans le leaderboard correspond à l'XP réel du user)
- [ ] Le classement weekly est bien réinitialisé chaque lundi
- [ ] Tous les tests passent

---

### US-2.4 — Leaderboard : frontend

**Assigné** : Shiro
**Estimation** : 8h
**Priorité** : 🔴 Must
**Dépendances** : US-2.3 (backend leaderboard fiable)

#### Contexte technique

La page `/leaderboard` existe dans le frontend mais est basique. Pour la beta, c'est un élément clé de motivation sociale.

#### Design attendu

**Page `/leaderboard`** :

1. **Sélecteur de classement** — 3 onglets :
   - 🏆 XP Hebdo
   - 📅 XP Mensuel
   - 🔥 Streak

2. **Liste classement** — Pour chaque entrée :
   - Position (#1, #2, #3 avec médailles 🥇🥈🥉, puis numéros)
   - Avatar (LPC mini ou initiales)
   - Username
   - Niveau (badge "Lv.12")
   - Score (XP ou jours de streak)
   - Mise en surbrillance de la ligne de l'utilisateur courant

3. **Position de l'utilisateur** — Toujours visible en bas de page si pas dans le top affiché

4. **État vide** — Si pas d'amis : message + lien vers la page `/friends` pour en ajouter

#### Appels API

```typescript
useLeaderboard(type: 'xp_weekly' | 'xp_monthly' | 'streak')
  → GET /api/leaderboard/xp/weekly
  → GET /api/leaderboard/xp/monthly
  → GET /api/leaderboard/streak
```

#### Tâches concrètes

1. Restructurer la page `/leaderboard` avec les 3 onglets
2. Créer le composant `LeaderboardEntry` (position, avatar, username, level, score)
3. Styliser le podium (top 3 avec médailles et visuellement distinct)
4. Mettre en surbrillance la ligne de l'utilisateur courant (fond coloré ou bordure)
5. Afficher la position de l'utilisateur en sticky en bas si hors du top visible
6. Ajouter l'état vide avec CTA vers `/friends`
7. Ajouter un pull-to-refresh ou bouton "Actualiser"
8. Vérifier le responsive mobile

#### Critères d'acceptation

- [ ] La page affiche 3 onglets : XP Hebdo, XP Mensuel, Streak
- [ ] Le classement affiche position, avatar, username, niveau, score pour chaque ami
- [ ] Le top 3 est visuellement distinct (médailles 🥇🥈🥉)
- [ ] La ligne de l'utilisateur courant est mise en surbrillance
- [ ] Si l'utilisateur n'a pas d'ami, un message avec lien vers `/friends` est affiché
- [ ] Responsive mobile OK
- [ ] Pas de console error

---

### US-2.5 — Combat PvP : réactivation backend

**Assigné** : Kuro
**Estimation** : 12h
**Priorité** : 🟡 Should (soumis au Go/No-Go du 26 fév)
**Dépendances** : US-2.1 (les joueurs doivent être amis pour combattre)

#### Contexte technique

**Ce qui existe déjà :**
- **Modèle `Combat`** en DB : `challenger_id`, `defender_id`, `winner_id`, `bet_coins`, `combat_log` (JSONB), stats snapshots, HP finaux, nombre de tours, récompenses
- **`CombatService`** dans `services/combat_service.py` : simulation tour par tour complète (dégâts, esquive, critiques, log)
- **Router `combat.py`** : existe mais **désactivé** depuis le 10 février (CombatService manquant à l'époque)

**Ce qui doit être fait :**
Réactiver le router, brancher les endpoints, tester la simulation de bout en bout.

#### Endpoints à réactiver/compléter

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `POST /api/combat/challenge` | POST | Lancer un défi. Body : `{ "defender_id": UUID, "bet_coins": int }` |
| `GET /api/combat/preview/{user_id}` | GET | Aperçu avant combat : stats des 2 joueurs, probabilités estimées |
| `GET /api/combat/history` | GET | Historique des combats de l'utilisateur (paginé) |
| `GET /api/combat/{combat_id}` | GET | Détail d'un combat (log tour par tour) |

#### Règles métier à valider

- Les deux joueurs doivent être **amis** (status `accepted`)
- Niveau minimum : **5** pour les deux joueurs
- Cooldown : **1 combat par paire d'amis par jour** (pas 1 combat par jour global, mais 1 par paire)
- Mise optionnelle : 0 à 100 coins maximum. Vérifier que les deux joueurs ont les fonds
- Le combat est **instantané** (simulation côté serveur, pas de websocket)
- Récompenses : victoire = 50-100 XP + 20-50 coins + mise. Défaite = 10 XP + perte de la mise

#### Formules de combat (déjà dans CombatService, à vérifier)

```python
# HP
max_hp = 100 + (endurance * 10)

# Dégâts
damage = (strength + weapon_bonus) * random(0.8, 1.2)
if is_crit: damage *= 1.5

# Esquive
dodge_chance = min(agility * 0.02, 0.40)  # Max 40%

# Critique
crit_chance = min(intelligence * 0.015, 0.30)  # Max 30%

# Réduction armure
armor_reduction = min(0.5, armor_bonus * 0.02)  # Max 50%
```

#### Tâches concrètes

1. Réactiver le router combat dans `main.py` (actuellement commenté/désactivé)
2. Vérifier que `CombatService.simulate_combat()` fonctionne avec les stats actuelles des personnages (y compris bonus d'équipement)
3. Implémenter la validation : vérifier amitié, niveau min, cooldown, fonds pour la mise
4. Vérifier que le `combat_log` est bien structuré (array de tours, chaque tour avec attaquant, dégâts, esquive, critique, HP restants)
5. Vérifier que les récompenses sont bien distribuées (XP via `XPService`, coins via transaction)
6. Vérifier que le `BadgeService` est appelé après un combat (badges de type `combat_wins`)
7. Écrire les tests : combat normal, combat avec mise, combat refusé (pas amis, cooldown, fonds insuffisants)
8. Tester avec 2 comptes réels sur l'environnement de staging

#### Critères d'acceptation

- [ ] Le router combat est réactivé et les 4 endpoints répondent
- [ ] `POST /api/combat/challenge` simule un combat et retourne le résultat complet
- [ ] Le combat est refusé si les joueurs ne sont pas amis → 403
- [ ] Le combat est refusé si un joueur est sous le niveau 5 → 400
- [ ] Le combat est refusé si cooldown actif (déjà combattu aujourd'hui) → 429
- [ ] Le combat est refusé si fonds insuffisants pour la mise → 400
- [ ] Le `combat_log` contient un array de tours lisible
- [ ] Les récompenses (XP + coins) sont correctement attribuées au gagnant
- [ ] La mise est transférée du perdant au gagnant
- [ ] L'historique (`GET /api/combat/history`) retourne les combats triés par date
- [ ] Tous les tests passent

#### ⚠️ Go/No-Go — Critères pour le mercredi 26 février

Le combat est **Go** si et seulement si :
1. Les 4 endpoints répondent sans erreur 500
2. La simulation produit un résultat cohérent (un gagnant, HP cohérents)
3. Les récompenses sont distribuées correctement
4. Les validations (amitié, niveau, cooldown) bloquent les cas invalides

Si **un seul** de ces critères n'est pas rempli → **No-Go**. On passe la page combat en "Coming Soon" et Kuro/Shiro réinvestissent le temps restant dans le polish (US-2.8 étendue + fix bugs).

---

### US-2.6 — Combat PvP : frontend (UI minimale)

**Assigné** : Shiro
**Estimation** : 12h
**Priorité** : 🟡 Should (conditionné au Go PvP mercredi 26)
**Dépendances** : US-2.5 (backend combat fonctionnel et validé Go)

#### Contexte technique

**Si Go PvP confirmé**, Shiro construit une UI de combat minimale mais fonctionnelle. L'objectif n'est PAS d'avoir une animation de combat RPG complète — c'est de permettre aux joueurs de lancer un défi et de voir le résultat.

#### Pages et composants

**1. Lancer un combat** — Depuis le profil d'un ami (bouton "Défier") ou page `/combat`

- Écran de pré-combat :
  - Les 2 personnages côte à côte (sprites LPC)
  - Stats résumées de chaque joueur (niveau, HP calculés, force, agilité)
  - Champ de mise optionnel (slider ou input, 0-100 coins)
  - Bouton "Combattre !"
  - Bouton "Annuler"

**2. Résultat du combat** — Écran de résultat

- Header : "Victoire !" ou "Défaite..." avec animation simple (confetti si victoire)
- Les 2 personnages avec HP finaux affichés (barre de vie)
- Résumé : nombre de tours, XP gagné, coins gagné/perdu
- **Log simplifié** : liste scrollable des tours clés (critiques, esquives, KO)
- Bouton "Voir le log complet" (accordion)
- Bouton "Revanche" (relancer un combat)
- Bouton "Retour"

**3. Historique** — Page `/combat` ou onglet dans `/combat`

- Liste des combats récents
- Chaque ligne : adversaire, résultat (V/D), date, XP gagné
- Clic sur un combat → détail avec log

#### Appels API

```typescript
previewCombat(userId)     → GET /api/combat/preview/{user_id}
launchCombat(defenderId, betCoins) → POST /api/combat/challenge
getCombatHistory()        → GET /api/combat/history
getCombatDetail(combatId) → GET /api/combat/{combat_id}
```

#### Tâches concrètes

1. Créer l'écran de pré-combat (`CombatPreview`) avec les 2 personnages et stats
2. Créer le composant de mise (`BetSlider` ou input numérique, 0-100)
3. Implémenter l'appel `POST /api/combat/challenge` avec loading state
4. Créer l'écran de résultat (`CombatResult`) avec vainqueur, HP, XP, coins
5. Créer le composant `CombatLog` (liste de tours, scrollable)
6. Créer la page historique des combats (`CombatHistory`)
7. Intégrer le bouton "Défier" dans la page `/friends` et le profil ami
8. Gérer les erreurs (pas amis, cooldown, fonds insuffisants) avec messages explicites
9. Vérifier le responsive mobile

#### Critères d'acceptation

- [ ] On peut lancer un combat depuis le profil d'un ami
- [ ] L'écran pré-combat affiche les stats des 2 joueurs
- [ ] La mise est configurable (0-100 coins)
- [ ] Le résultat affiche clairement le gagnant, les HP finaux, l'XP et les coins
- [ ] Le log du combat est lisible et scrollable
- [ ] L'historique des combats est accessible et affiche les combats récents
- [ ] Les erreurs (pas amis, cooldown, fonds) affichent un message clair
- [ ] Responsive mobile OK
- [ ] Pas de console error

#### ⚠️ Si No-Go PvP

Si le combat est déclaré No-Go mercredi 26 :
1. Shiro ne commence PAS cette US
2. La page `/combat` affiche un écran "Coming Soon — Le combat PvP arrive bientôt !"
3. Le bouton "Défier" sur les profils amis est masqué ou grisé
4. Shiro réinvestit ses heures dans : polish de l'onboarding, amélioration du responsive, fix bugs visuels

---

### US-2.7 — Page profil ami

**Assigné** : Shiro
**Estimation** : 6h
**Priorité** : 🔴 Must
**Dépendances** : US-2.1, US-2.2 (liste d'amis fonctionnelle)

#### Contexte technique

Quand un utilisateur clique sur un ami dans la liste ou dans le leaderboard, il doit voir le profil de cet ami. L'endpoint `GET /api/users/{id}` existe déjà pour les profils publics.

#### Design attendu

**Page `/profile/{userId}`** :

1. **Header profil** :
   - Personnage LPC de l'ami (sprite avec équipement)
   - Username, niveau, titre (basé sur le palier de niveau)
   - Date d'inscription ("Membre depuis...")

2. **Stats** :
   - Niveau + barre de progression XP
   - Streak actuel + best streak
   - Nombre d'habitudes actives
   - Nombre de badges débloqués

3. **Badges affichés** :
   - Les 3 badges sélectionnés par l'ami (s'il en a)
   - Format : icône + nom + rareté

4. **Équipement** :
   - Afficher les items équipés (arme, armure, casque, accessoire)
   - Nom + rareté de chaque item

5. **Actions** :
   - Bouton "Défier en combat" (si Go PvP et niveau ≥ 5)
   - Bouton "Supprimer de mes amis" (avec confirmation)

#### Appels API

```typescript
getUserProfile(userId)   → GET /api/users/{id}
// Ce endpoint doit retourner : username, level, total_xp, current_streak,
// best_streak, character (avec stats + equipped items), badges affichés,
// created_at
```

#### Tâches concrètes

1. Créer la page `/profile/[userId]` (ou `/friends/[userId]`)
2. Appeler `GET /api/users/{id}` et afficher toutes les infos
3. Afficher le personnage LPC avec l'équipement (réutiliser le composant `LPCCharacter` existant)
4. Afficher les badges sélectionnés
5. Ajouter les boutons d'action (défier, supprimer)
6. Gérer le cas "profil non trouvé" → page 404
7. Vérifier le responsive mobile

#### Critères d'acceptation

- [ ] En cliquant sur un ami dans la liste d'amis ou le leaderboard, on arrive sur son profil
- [ ] Le profil affiche : personnage LPC, username, niveau, streak, badges
- [ ] L'équipement de l'ami est visible
- [ ] Le bouton "Défier" est présent (actif si Go PvP, grisé sinon)
- [ ] Le bouton "Supprimer" fonctionne avec confirmation
- [ ] Profil non trouvé → affichage 404 propre
- [ ] Responsive mobile OK

---

### US-2.8 — Badges : vérifier l'auto-attribution

**Assigné** : Kuro
**Estimation** : 4h
**Priorité** : 🔴 Must
**Dépendances** : Aucune

#### Contexte technique

75 badges sont seeded en base. Le `BadgeService.check_all_badges()` est appelé à chaque complétion d'habitude et de tâche. Mais on n'a **jamais vérifié en conditions réelles** que les badges se débloquent correctement.

Pour la beta, les badges les plus atteignables dans les premiers jours sont :

| Badge | Condition | Type |
|-------|-----------|------|
| Premier Pas | 1ère habitude complétée | completions |
| En Route | 3 habitudes complétées | completions |
| En Feu | Streak de 7 jours | streak |
| Tasker | 1ère tâche complétée | completions |
| Social Butterfly | 1er ami ajouté | social |
| Gladiateur | 1er combat gagné | combat_wins |

#### Tâches concrètes

1. Lister tous les `condition_type` distincts dans la table `badges` et vérifier que chaque type est géré dans `BadgeService`
2. Tester manuellement avec un compte : compléter 1 habitude → le badge "Premier Pas" est-il attribué ?
3. Tester : ajouter un ami → le badge "Social Butterfly" est-il attribué ?
4. Vérifier que `check_all_badges()` ne crash pas si l'utilisateur a déjà le badge (idempotence)
5. Vérifier que le XP reward du badge est bien ajouté via `XPService`
6. Si des badges ne se débloquent pas → identifier le bug et le corriger
7. Écrire un test automatisé : créer un user, compléter N habitudes, vérifier que les badges attendus sont attribués

#### Critères d'acceptation

- [ ] Compléter 1 habitude débloque le badge "Premier Pas" (ou équivalent)
- [ ] Atteindre un streak de 7 jours débloque le badge streak correspondant
- [ ] Ajouter un ami débloque le badge social correspondant
- [ ] Le XP reward du badge est bien ajouté au total de l'utilisateur
- [ ] `check_all_badges()` est idempotent (pas de doublon si appelé 2 fois)
- [ ] Pas de crash si un `condition_type` est inconnu (graceful fallback)
- [ ] Au moins 5 types de conditions testés avec un test automatisé

---

## Sprint 2 — Gate de fin de sprint (vendredi 28 février)

### Test collectif

Ilane + Shiro + Kuro testent avec **2 comptes** le parcours suivant :

1. **Compte A** ajoute **Compte B** en ami via friend_code
2. Compte B accepte la demande
3. Les deux voient l'autre dans leur liste d'amis
4. Les deux apparaissent dans le leaderboard de l'autre
5. Compte A consulte le profil de Compte B
6. **Si Go PvP** : Compte A défie Compte B → le combat se lance, résultat affiché, XP distribué
7. Vérifier qu'au moins 1 badge social s'est débloqué

### Critères Gate Pass

- [ ] Le parcours ci-dessus fonctionne de bout en bout sans erreur
- [ ] Pas d'erreur 500 dans les logs backend
- [ ] Pas de console error côté frontend
- [ ] Les données sont cohérentes (XP du leaderboard = XP réel, etc.)

**Si la gate ne passe pas** → on ne passe PAS au Sprint 3. On reste sur le fix des bugs du Sprint 2 lundi.

---

## Résumé visuel

```
Lundi 24        Mardi 25        Mercredi 26       Jeudi 27        Vendredi 28
─────────────────────────────────────────────────────────────────────────────
KURO:                                                              
  US-2.1         US-2.1          US-2.3            US-2.5           US-2.8
  Friends BE     (fin) +         Leaderboard BE    Combat BE        Badges
                 US-2.3 start                      (si Go)          + Fix

SHIRO:
  US-2.2         US-2.2          US-2.4            US-2.6           US-2.7
  Friends FE     (fin) +         Leaderboard FE    Combat FE        Profil ami
                 US-2.4 start                      (si Go)          + Fix

                                 ⚡ GO/NO-GO PvP
                                 (mercredi PM)
                                                                   🏁 GATE
                                                                   (vendredi)
```
