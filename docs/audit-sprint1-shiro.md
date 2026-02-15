# 🦊 Audit Sprint 1 — Shiro (Frontend)

**Date :** 15 février 2026  
**Testeur :** Shiro  
**Environnement :** Production (https://habit.apps.ilanewep.cloud)  
**Méthode :** Tests API + vérification frontend

---

## 📋 Résumé Exécutif

| Étape | Statut | Notes |
|-------|--------|-------|
| Register | ✅ OK | Fonctionne parfaitement |
| Onboarding | ✅ OK | Création personnage OK |
| Dashboard | ✅ OK | Données correctes |
| Créer habitude | ⚠️ ATTENTION | Champ `title` requis (pas `name`) |
| Créer habitude comptable | ✅ OK | target_value accepté |
| Compléter habitude | ✅ OK | XP/Coins corrects |
| Vérifier streak | ✅ OK | Streak incrémenté |
| Boutique | ⚠️ ATTENTION | Route `/api/shop` → 404, utiliser `/api/shop/items` |
| Acheter item | ✅ OK | Route `/api/shop/buy/{id}` |
| Inventaire | ✅ OK | Item ajouté |
| Équiper item | ⚠️ ATTENTION | Route `/api/inventory/equip/{id}` (pas `/{id}/equip`) |
| Page Calendar | ✅ OK | Données heatmap correctes |
| Page Badges | ✅ OK | 75 badges affichés |
| Logout/Login | ✅ OK | Données persistées |

**Score global : 11/14 OK, 3 points d'attention**

---

## 🔴 Bugs Bloquants (P0)

### Aucun bug bloquant trouvé côté API
Le core loop fonctionne entièrement.

---

## 🟡 Bugs Gênants (P1)

### BUG-001 : Redirect 307 sur POST sans trailing slash
- **Page :** Toutes les routes POST
- **Action :** `POST /api/characters` (sans `/`)
- **Résultat attendu :** Création du personnage
- **Résultat obtenu :** HTTP 307 Redirect
- **Solution :** Ajouter trailing slash dans les appels frontend OU configurer FastAPI avec `redirect_slashes=False`

### BUG-002 : Route shop incohérente
- **Page :** Boutique
- **Action :** `GET /api/shop` ou `GET /api/shop/`
- **Résultat attendu :** Liste des items
- **Résultat obtenu :** HTTP 404 Not Found
- **Route correcte :** `GET /api/shop/items`
- **Impact :** Si le frontend appelle `/api/shop`, la page sera vide

### BUG-003 : Route équipement incohérente
- **Page :** Inventaire
- **Action :** `POST /api/inventory/{id}/equip`
- **Résultat attendu :** Équiper l'item
- **Résultat obtenu :** HTTP 404 Not Found
- **Route correcte :** `POST /api/inventory/equip/{id}`
- **Impact :** Équipement ne fonctionne pas si mauvaise route utilisée

---

## 🟢 Bugs Cosmétiques (P2)

### BUG-004 : Schéma habit utilise "title" au lieu de "name"
- **Page :** Création d'habitude
- **Contexte :** Le modèle DB utilise `name`, mais le schéma Pydantic attend `title`
- **Impact :** Incohérence, confusion pour les développeurs
- **Suggestion :** Aligner sur un seul nom (préférence: `name`)

### BUG-005 : best_streak reste à 0 après streak=1
- **Observation :** Après une complétion, `current_streak=1` mais `best_streak=0`
- **Attendu :** `best_streak` devrait être mis à jour
- **Priorité :** Basse (ne casse rien)

---

## ✅ Points Positifs

1. **Register/Login** — Fluide, tokens JWT fonctionnels
2. **Création personnage** — Toutes les options marchent
3. **Système XP/Coins** — Calculs corrects avec streak multiplier
4. **Boutique** — Achat fonctionne, débit correct
5. **Inventaire** — Équipement sauvegardé
6. **Calendar heatmap** — Données correctes
7. **Badges** — 75 badges disponibles, bien structurés
8. **Persistance** — Toutes les données sauvegardées après logout/login

---

## 🧪 Tests Effectués

### Test 1 : Parcours complet nouvel utilisateur
```
1. Register → ✅ Token reçu
2. Create Character → ✅ (avec trailing slash)
3. Get User → ✅ level=1, xp=0, coins=0
4. Create Habit → ✅ (champ "title")
5. Create Countable Habit → ✅
6. Complete Habit → ✅ xp=15, coins=7
7. Verify User → ✅ total_xp=15, coins=7, streak=1
8. Get Shop Items → ✅ 38 items
9. Buy Item (free) → ✅
10. Get Inventory → ✅ item présent
11. Equip Item → ✅ is_equipped=true
12. Get Calendar → ✅ completion visible
13. Get Badges → ✅ 75 badges
14. Logout → ✅
15. Re-Login → ✅ données intactes
```

### Données du test
- **User ID:** `fdf4abdd-b825-4e0d-9aac-509df51bbbf7`
- **Username:** `audituser1771170779`
- **Final State:** level=1, xp=15, coins=7, streak=1

---

## 📱 Tests Responsive (À faire)

- [ ] Desktop Chrome
- [ ] iPhone Safari
- [ ] Android Chrome

→ **US-1.6 dédiée à ce test**

---

## 🎯 Recommandations Frontend

### Priorité 1 — Vérifier les routes utilisées
1. S'assurer que le frontend utilise les bonnes routes :
   - `/api/shop/items` (pas `/api/shop`)
   - `/api/inventory/equip/{id}` (pas `/{id}/equip`)
   - Ajouter trailing slash sur tous les POST

### Priorité 2 — Masquer les features non prêtes
1. Masquer le bouton Combat (si non fonctionnel)
2. Masquer les créations de tâches si LLM non configuré

### Priorité 3 — Améliorer l'UX
1. Afficher un loader pendant les appels API
2. Gérer les erreurs 500 avec un message user-friendly
3. Confirmation visuelle après achat/équipement

---

## 📊 Métriques

- **Temps d'audit :** ~30 minutes
- **Requêtes testées :** 20+
- **Bugs trouvés :** 5 (0 P0, 3 P1, 2 P2)
- **Couverture parcours :** 100%

---

*Audit réalisé par Shiro 🦊 — 15 février 2026*
