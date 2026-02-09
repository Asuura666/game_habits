# Documentation Fonctionnelle - Habit Tracker

> Application de suivi d'habitudes gamifiée avec personnage RPG évolutif, système de tâches évaluées par IA, combat PvP entre amis, et statistiques avancées.

---

## 1. Vue d'ensemble

### Concept de l'application

Habit Tracker est une application web qui transforme le développement personnel en aventure RPG. Chaque habitude accomplie, chaque tâche terminée fait progresser votre personnage dans un univers gamifié où la productivité devient un jeu.

**Philosophie** : "Chaque petite victoire compte" — l'application récompense la régularité plutôt que la perfection.

### Proposition de valeur

| Problème | Solution Habit Tracker |
|----------|------------------------|
| Difficulté à maintenir les habitudes | Système de streaks et récompenses visuelles |
| Manque de motivation | XP, niveaux, personnage évolutif |
| Procrastination | Évaluation IA des tâches avec récompenses adaptées |
| Isolement dans l'effort | Combat PvP et leaderboards entre amis |
| Difficulté à visualiser ses progrès | Statistiques détaillées et heatmap |

### Cible utilisateurs

**Persona principal** : Jeune actif (18-35 ans), familier avec les jeux vidéo, souhaitant améliorer sa productivité de manière ludique.

- 🎮 **Gamers** : Habitués aux systèmes de progression RPG
- 📱 **Digital natives** : À l'aise avec les outils numériques
- 🎯 **Self-improvers** : Intéressés par le développement personnel
- 👥 **Compétitifs** : Motivés par les défis entre amis

---

## 2. Parcours utilisateur

### Onboarding

**Étape 1 — Inscription**
```
📧 Email / Authentification sociale (Google, Apple)
👤 Choix du pseudo unique
🌍 Configuration du fuseau horaire
```

**Étape 2 — Création du personnage**
```
🏷️ Nom du personnage
⚔️ Choix de la classe (Guerrier, Mage, Ranger, Paladin, Assassin)
🎨 Personnalisation de l'apparence (genre, couleur de peau, coiffure, yeux)
```

**Étape 3 — Première habitude**
```
💡 L'application suggère de créer une première habitude simple
📝 Exemple guidé : "Boire 2L d'eau par jour"
✅ Premier check-in pour découvrir le système de récompenses
```

### Cycle quotidien

**Matin**
```
🌅 Ouverture de l'app → Vue dashboard
📋 Liste des habitudes du jour à accomplir
📌 Tâches en attente avec leur priorité
```

**Journée**
```
✅ Check-in des habitudes au fur et à mesure
📝 Création de nouvelles tâches si besoin
🤖 L'IA évalue automatiquement les tâches
```

**Soir**
```
🎯 Revue des accomplissements de la journée
🔥 Mise à jour du streak si toutes les habitudes sont faites
💰 Collecte des récompenses (XP + Coins)
```

### Gamification loop

```
┌─────────────────────────────────────────────────────┐
│  ACCOMPLIR ──► RÉCOMPENSE ──► PROGRESSION ──►  │
│       ▲                                         │
│       └──────────── MOTIVATION ◄────────────────┘
└─────────────────────────────────────────────────────┘

1. L'utilisateur accomplit une habitude/tâche
2. Il reçoit XP + Coins + renforcement du streak
3. Son personnage progresse (level up, nouveaux items)
4. La progression motive à continuer
5. Le cycle recommence
```

---

## 3. Habitudes

### Création d'une habitude

Pour créer une habitude, l'utilisateur renseigne :

| Champ | Description | Exemple |
|-------|-------------|---------|
| **Nom** | Titre court (max 100 caractères) | "Méditer" |
| **Description** | Détails optionnels | "10 minutes de pleine conscience" |
| **Icône** | Emoji représentatif | 🧘 |
| **Couleur** | Code couleur pour le visuel | #6366F1 (violet) |
| **Catégorie** | Classification | Bien-être, Sport, Travail, Social... |

**Exemple concret** :
> 📚 **Lire 30 minutes**
> *Catégorie : Développement personnel*
> *Objectif : 30 minutes par jour*

### Types de fréquences

| Type | Description | Exemple |
|------|-------------|---------|
| **Quotidien** | Tous les jours | Boire de l'eau |
| **Hebdomadaire** | 1 fois par semaine | Grand ménage |
| **Jours spécifiques** | Certains jours uniquement | Lundi, Mercredi, Vendredi |
| **X fois par semaine** | Objectif hebdo flexible | 3 fois par semaine (sport) |

**Configuration technique** :
- `frequency_type`: daily, weekly, specific_days, x_per_week
- `frequency_days`: [0, 2, 4] (Lundi, Mercredi, Vendredi)
- `frequency_count`: 3 (pour x_per_week)

### Système de streak

Le **streak** représente le nombre de jours consécutifs où l'habitude a été accomplie.

**Règles** :
- ✅ Habitude complétée → Streak +1
- ❌ Habitude manquée → Streak remis à 0
- ❄️ **Streak Freeze** : Protection d'un jour (1 disponible par défaut)

**Bonus de streak** :
| Streak | Multiplicateur XP |
|--------|-------------------|
| 1-6 jours | ×1.0 |
| 7-13 jours | ×1.1 |
| 14-29 jours | ×1.25 |
| 30+ jours | ×1.5 |

**Record personnel** : Le `best_streak` garde en mémoire le plus long streak atteint.

### Check-in et complétion

**Habitude binaire (oui/non)** :
```
[✓] Méditer 10 minutes
    → Clic pour marquer comme fait
    → +25 XP, +5 Coins
```

**Habitude avec objectif** :
```
[🔘──────] Boire 2L d'eau
           Progression : 500ml / 2000ml
           → Slider ou saisie de valeur
           → XP proportionnel à la complétion
```

**Rappels** : Optionnellement, une notification peut être programmée à une heure précise.

---

## 4. Tâches

### Création de tâche libre

Contrairement aux habitudes récurrentes, les **tâches** sont des actions ponctuelles.

| Champ | Description | Exemple |
|-------|-------------|---------|
| **Titre** | Description de la tâche (max 200 car.) | "Préparer présentation client" |
| **Description** | Détails optionnels | "Slides sur le nouveau produit" |
| **Catégorie** | Classification | Travail, Personnel, Admin... |
| **Priorité** | Niveau d'urgence | Basse, Moyenne, Haute, Urgente |
| **Date d'échéance** | Deadline optionnelle | 15 février 2026, 14h00 |

### Évaluation par IA (difficulté, XP)

Dès la création d'une tâche, **Claude 3.5 Haiku** l'analyse automatiquement.

**Ce que l'IA évalue** :
- Complexité de la tâche
- Temps estimé
- Effort cognitif requis

**Échelle de difficulté** :

| Difficulté | XP Base | Coins Base | Exemple |
|------------|---------|------------|---------|
| Triviale | 5 | 1 | Envoyer un email rapide |
| Facile | 15 | 3 | Ranger son bureau |
| Moyenne | 30 | 6 | Rédiger un rapport |
| Difficile | 50 | 10 | Préparer une présentation |
| Épique | 100 | 20 | Livrer un projet complet |
| Légendaire | 200 | 50 | Accomplissement majeur |

**Ajustement utilisateur** : L'utilisateur peut modifier manuellement les récompenses s'il estime que l'IA s'est trompée.

**Exemple d'évaluation** :
```
📝 Tâche : "Nettoyer le garage"
🤖 IA : Difficulté DIFFICILE
   └─ Raisonnement : "Tâche physique et longue, 
      nécessitant tri et organisation"
💰 Récompenses : 50 XP, 10 Coins
```

### Sous-tâches

Les tâches complexes peuvent être découpées en sous-tâches.

**Création** :
- L'IA peut suggérer des sous-tâches automatiquement
- L'utilisateur peut en ajouter manuellement

**Exemple** :
```
📦 Déménagement
├── ☐ Commander les cartons
├── ☐ Trier les affaires
├── ☐ Emballer pièce par pièce
├── ☐ Réserver le camion
└── ☐ Changer l'adresse postale

Progression : 2/5 sous-tâches complétées
```

**Récompenses** : L'XP est distribué proportionnellement à la complétion des sous-tâches.

---

## 5. Système de progression

### Niveaux (1-50)

Le niveau représente la progression globale du joueur.

| Niveau | Palier | Titre |
|--------|--------|-------|
| 1-10 | Débutant | Novice |
| 11-20 | Intermédiaire | Aventurier |
| 21-30 | Confirmé | Expert |
| 31-40 | Avancé | Maître |
| 41-50 | Élite | Légende |

**Déblocage par niveau** :
- Niveau 5 : Accès au combat PvP
- Niveau 10 : Items rares en boutique
- Niveau 20 : Items épiques
- Niveau 30 : Items légendaires
- Niveau 50 : Badge ultime "Maître des Habitudes"

### XP et formules

**Gains d'XP** :
- Habitude complétée : 20-50 XP (selon difficulté)
- Tâche complétée : 5-200 XP (selon évaluation IA)
- Badge débloqué : 25-500 XP (selon rareté)
- Combat PvP gagné : 50-100 XP

**Formule XP pour niveau suivant** :
```
XP_requis(niveau) = 100 × niveau × 1.5^(niveau/10)
```

| Niveau | XP cumulé requis |
|--------|------------------|
| 2 | 150 |
| 5 | 750 |
| 10 | 2,370 |
| 20 | 12,600 |
| 30 | 47,800 |
| 50 | 395,000 |

### Multiplicateurs de streak

La régularité est récompensée par des multiplicateurs.

| Streak Global | Multiplicateur |
|---------------|----------------|
| 0-6 jours | ×1.0 |
| 7+ jours | ×1.1 |
| 14+ jours | ×1.25 |
| 30+ jours | ×1.5 |
| 100+ jours | ×2.0 |

**Exemple** :
> Tâche valant 50 XP + Streak de 30 jours
> → 50 × 1.5 = **75 XP** gagnés

### Coins

Les **Coins** sont la monnaie virtuelle du jeu.

**Gagner des Coins** :
| Source | Montant |
|--------|---------|
| Habitude quotidienne | 5-15 coins |
| Tâche complétée | 1-50 coins |
| Combat gagné | 20-100 coins |
| Badge débloqué | 10-100 coins |
| Connexion quotidienne | 5 coins |

**Dépenser des Coins** :
- Acheter des équipements en boutique
- Parier sur les combats PvP
- Acheter des Streak Freeze (futur)

---

## 6. Personnage RPG

### Classes disponibles

Chaque classe offre des bonus de départ et un style de jeu unique.

| Classe | Spécialité | Bonus stats de départ |
|--------|------------|----------------------|
| ⚔️ **Guerrier** | Combat physique | +3 Force, +2 Endurance |
| 🧙 **Mage** | Intelligence | +4 Intelligence, +1 Charisme |
| 🏹 **Ranger** | Agilité | +3 Agilité, +2 Endurance |
| 🛡️ **Paladin** | Équilibre | +2 Force, +2 Endurance, +1 Charisme |
| 🗡️ **Assassin** | Critique | +4 Agilité, +1 Force |

### Stats (Force, Endurance, Agilité, Intelligence, Charisme)

| Stat | Effet en combat | Effet hors combat |
|------|-----------------|-------------------|
| **Force** 💪 | Dégâts physiques (+2 dmg/pt) | — |
| **Endurance** 🛡️ | Points de vie (+5 HP/pt) | Résistance au reset de streak |
| **Agilité** 🏃 | Chance d'esquive, initiative | — |
| **Intelligence** 🧠 | Dégâts magiques, critique | Bonus XP sur tâches |
| **Charisme** ✨ | Bonus coins en combat | Bonus coins généraux |

**Points de stats** :
- +2 points non alloués par level up
- Maximum par stat : 100

### Apparence (LPC sprites)

L'application utilise le système **Liberated Pixel Cup (LPC)** pour les sprites.

**Personnalisation** :
| Élément | Options disponibles |
|---------|---------------------|
| Genre | Masculin, Féminin, Neutre |
| Couleur de peau | Claire, Bronzée, Foncée, Fantaisie |
| Style de cheveux | 15+ coiffures |
| Couleur cheveux | Noir, Brun, Blond, Roux, Fantaisie |
| Couleur yeux | Bleu, Vert, Marron, Gris, Fantaisie |

Les équipements s'affichent en **layers** superposés au sprite de base.

### Équipements

Le personnage peut équiper :

| Slot | Type | Exemple |
|------|------|---------|
| 🗡️ Main | Arme | Épée, Bâton, Arc, Dagues |
| 🛡️ Corps | Armure | Cuir, Cotte de mailles, Robe |
| ⛑️ Tête | Casque | Capuche, Heaume, Couronne |
| 💍 Accessoire | Bijou | Anneau, Amulette, Cape |
| 🐾 Compagnon | Pet | Chat, Dragon, Fantôme |

---

## 7. Boutique

### Types d'items

| Catégorie | Description |
|-----------|-------------|
| **Armes** | Augmentent Force ou Intelligence |
| **Armures** | Augmentent Endurance et défense |
| **Casques** | Bonus variés |
| **Accessoires** | Effets spéciaux et Charisme |
| **Pets** | Compagnons avec bonus passifs |

### Raretés

| Rareté | Couleur | Multiplicateur stats | Prix moyen |
|--------|---------|---------------------|------------|
| Commun | ⚪ Gris | ×1.0 | 50-100 |
| Peu commun | 🟢 Vert | ×1.2 | 150-300 |
| Rare | 🔵 Bleu | ×1.5 | 400-800 |
| Épique | 🟣 Violet | ×2.0 | 1,000-2,500 |
| Légendaire | 🟡 Or | ×3.0 | 5,000-10,000 |

### Effets des équipements

**Bonus de stats** :
```
🗡️ Épée de Flamme (Rare)
   +8 Force
   +3 Agilité
   Prix : 600 coins
   Niveau requis : 15
```

**Items limités** :
Certains items sont disponibles uniquement pendant des événements saisonniers (Halloween, Noël, etc.).

---

## 8. Combat PvP

### Défi entre amis

**Comment lancer un défi** :
1. Aller sur le profil d'un ami
2. Cliquer sur "Défier en combat"
3. Optionnellement, parier des Coins
4. Le combat se simule instantanément

**Conditions** :
- Les deux joueurs doivent être amis
- Niveau minimum : 5
- Cooldown : 1 combat par ami par jour

### Simulation tour par tour

Le combat est **automatique** et simulé instantanément.

**Déroulement** :
```
⚔️ Combat : @Alice vs @Bob

Tour 1:
  Alice attaque → 45 dégâts
  Bob contre-attaque → 32 dégâts

Tour 2:
  Alice (Critique!) → 78 dégâts
  Bob attaque → 28 dégâts

[...continues...]

Tour 8:
  Bob est KO !

🏆 Victoire de Alice !
```

**Nombre de tours** : Maximum 20 tours. Si personne n'est KO, celui avec le plus de HP gagne.

### Calcul des dégâts

**Formule de base** :
```
Dégâts = (Force × 2) + (Intelligence × 1.5) + bonus_arme
Réduction = Endurance × 0.5
Dégâts_finaux = max(Dégâts - Réduction, 1)
```

**Chances critiques** :
- Base : 5%
- +1% par point d'Agilité au-delà de 20
- Dégâts critiques : ×2

**Esquive** :
- Base : 2%
- +0.5% par point d'Agilité au-delà de 30

### Récompenses

| Résultat | XP | Coins | Remarque |
|----------|-----|-------|----------|
| Victoire | 50-100 | 20-50 | + Mise (si pari) |
| Défaite | 10 | 0 | Perte de la mise |
| Match nul | 25 | 10 | Remboursement mise |

**Bonus** :
- Première victoire du jour : +25 XP
- Victoire contre niveau supérieur : ×1.5 XP

---

## 9. Social

### Système d'amis

**Fonctionnalités** :
- Liste d'amis avec statut en ligne
- Voir le profil et les stats des amis
- Défier en combat PvP
- Comparer les progressions

**États de relation** :
| Status | Description |
|--------|-------------|
| `pending` | Demande envoyée, en attente |
| `accepted` | Amitié active |
| `rejected` | Demande refusée |
| `blocked` | Utilisateur bloqué |

### Code ami

Chaque utilisateur possède un **code ami unique** (généré à l'inscription).

**Format** : 8-12 caractères alphanumériques
**Exemple** : `SHIRO-2K6F-XY9Q`

**Utilisation** :
1. Partager son code avec un ami
2. L'ami saisit le code dans "Ajouter un ami"
3. Une demande d'ami est envoyée
4. Acceptation requise pour finaliser

### Leaderboards

**Classements disponibles** :

| Leaderboard | Critère | Période |
|-------------|---------|---------|
| 🏆 XP Total | XP accumulé | Tout temps |
| 🔥 Streak | Streak actuel | En cours |
| ⚔️ PvP | Victoires combat | Semaine/Mois |
| 📈 Habitudes | Complétion % | Semaine |

**Filtres** :
- 🌍 Global (tous les utilisateurs publics)
- 👥 Amis uniquement
- 🏠 Personnel (historique)

---

## 10. Badges & Achievements

### Types de badges

| Type | Description | Exemple |
|------|-------------|---------|
| **Streak** | Basé sur les streaks | 7 jours, 30 jours, 100 jours |
| **Complétion** | Nombre d'habitudes/tâches | 100 habitudes, 50 tâches |
| **Niveau** | Paliers de niveau | Niveau 10, 25, 50 |
| **Combat** | Victoires PvP | 10 victoires, 50 victoires |
| **Social** | Amis et interactions | 5 amis, 20 amis |
| **Secret** | Conditions cachées | ??? (découverte) |
| **Saisonnier** | Événements temporaires | Halloween 2026 |

### Conditions de déblocage

**Exemples concrets** :

| Badge | Condition | Rareté | Récompense |
|-------|-----------|--------|------------|
| 🌅 **Early Bird** | 7 jours consécutifs | Commun | 25 XP |
| 🔥 **En Feu** | 30 jours de streak | Rare | 100 XP, 50 Coins |
| 💯 **Centurion** | 100 habitudes complétées | Épique | 250 XP, 100 Coins |
| ⚔️ **Gladiateur** | 25 combats gagnés | Rare | 150 XP |
| 🏆 **Légende** | Atteindre niveau 50 | Légendaire | 500 XP, 250 Coins |
| 🦉 **Noctambule** | Check-in après minuit 10× | Secret | 75 XP |
| 🎃 **Citrouille** | Actif pendant Halloween | Saisonnier | Costume exclusif |

**Affichage** :
- Badges affichables sur le profil (max 3)
- Progression visible vers le prochain badge
- Badges secrets révélés seulement après déblocage

---

## 11. Statistiques

### Dashboard overview

**Vue principale** :
```
┌─────────────────────────────────────────────────┐
│  📊 Aujourd'hui                                 │
│  ───────────────────                            │
│  Habitudes : 4/6 complétées (67%)               │
│  Tâches : 2/3 terminées                         │
│  XP gagné : 145 XP                              │
│  Coins : +35                                    │
│                                                 │
│  🔥 Streak actuel : 12 jours                    │
│  📈 Niveau : 15 (2,450/3,000 XP)                │
└─────────────────────────────────────────────────┘
```

**Widgets disponibles** :
- Progression quotidienne (habitudes + tâches)
- Streak et record personnel
- XP et niveau actuels
- Derniers badges débloqués
- Classement amis (top 3)

### Heatmap calendrier

Visualisation annuelle des complétion à la façon GitHub contributions.

```
        Jan     Fév     Mar     ...
Lu      ⬜🟩🟩   🟩🟩⬜   🟨🟩🟩
Ma      🟩🟩🟩   🟩🟩🟩   🟩🟩🟩
Me      🟩🟩🟨   🟨🟩🟩   🟩🟩🟩
Je      🟩⬜🟩   🟩🟩🟩   🟩🟨🟩
Ve      🟩🟩🟩   🟩🟨🟩   🟩🟩🟩
Sa      🟨🟩🟩   🟩🟩⬜   ⬜🟩🟩
Di      ⬜⬜⬜   ⬜⬜⬜   ⬜🟩⬜

Légende :
⬜ Aucune activité
🟨 Partiellement complété
🟩 100% complété
```

**Drill-down** : Clic sur un jour → détail des habitudes/tâches.

### Tendances et insights

**Graphiques disponibles** :
- 📈 Évolution du niveau sur 6 mois
- 📊 Taux de complétion par semaine
- 🔥 Historique des streaks
- ⚔️ Ratio victoires/défaites PvP

**Insights automatiques** :
> 💡 "Tu es 23% plus régulier le matin. Essaie de planifier tes habitudes importantes avant 10h !"

> 💡 "Ton meilleur jour de la semaine est le Mardi avec 94% de complétion."

> 💡 "Tu as gagné 5 320 XP ce mois-ci, soit +12% par rapport au mois dernier."

**Export** : Possibilité d'exporter les données en CSV pour analyse externe.

---

## Annexes

### Glossaire

| Terme | Définition |
|-------|------------|
| **Streak** | Série de jours consécutifs d'accomplissement |
| **XP** | Points d'expérience pour progresser en niveau |
| **Coins** | Monnaie virtuelle pour la boutique |
| **Check-in** | Action de marquer une habitude comme faite |
| **LPC** | Liberated Pixel Cup, format de sprites pixel art |

### Formules de référence

```javascript
// XP requis pour le niveau suivant
xpRequired = 100 * level * Math.pow(1.5, level / 10)

// Multiplicateur de streak
streakMultiplier = streak >= 100 ? 2.0 :
                   streak >= 30 ? 1.5 :
                   streak >= 14 ? 1.25 :
                   streak >= 7 ? 1.1 : 1.0

// Puissance de combat
combatPower = (strength * 2) + (endurance * 1.5) + 
              (agility * 1.5) + (intelligence * 1) + 
              (charisma * 0.5)
```

---

*Documentation rédigée pour Habit Tracker v1.0*  
*Dernière mise à jour : Février 2026*
