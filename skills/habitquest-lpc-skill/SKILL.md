---
name: HabitQuest LPC Character System
description: >
  Skill spécialisé pour le projet HabitQuest (https://github.com/Asuura666/game_habits).
  Génère des composants Next.js/TypeScript/Tailwind pour l'intégration de personnages
  pixel-art LPC (Liberated Pixel Cup) dans l'application HabitQuest — un habit tracker
  gamifié avec système RPG. Couvre : création de personnage, animation sprite, progression
  XP/niveaux, boutique d'équipements, et intégration avec l'API FastAPI backend.
  Active ce skill dès que l'utilisateur mentionne : personnage HabitQuest, avatar, sprite,
  équipement, niveau, XP, boutique, character creator, animation, ou toute modification
  du système de personnage dans game_habits.
---

# HabitQuest LPC Character System

Skill pour intégrer des personnages pixel-art LPC dans le projet **HabitQuest** :
un habit tracker gamifié où compléter des habitudes fait gagner de l'XP, monter de niveau,
et débloquer des équipements pour son avatar.

## Architecture du projet HabitQuest

```
game_habits/
├── backend/                 # FastAPI + Python 3.11 + SQLAlchemy + PostgreSQL
│   ├── app/
│   │   ├── main.py          # Point d'entrée FastAPI
│   │   ├── models/          # Modèles SQLAlchemy (User, Habit, Character...)
│   │   ├── schemas/         # Schémas Pydantic V2
│   │   ├── routers/         # Routes API
│   │   └── services/        # Logique métier
│   ├── alembic/             # Migrations DB
│   └── requirements.txt
├── frontend/                # Next.js 14 + React 18 + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── app/             # App Router Next.js 14
│   │   ├── components/      # Composants React
│   │   ├── hooks/           # Custom hooks
│   │   ├── lib/             # Utilitaires, API client
│   │   ├── types/           # Types TypeScript
│   │   └── styles/          # Styles globaux
│   └── package.json
├── docker-compose.yml       # Docker (PostgreSQL + Redis + API + Frontend)
└── docs/                    # Documentation
```

**Stack :**
- Frontend : Next.js 14, React 18, TypeScript 5, Tailwind CSS
- Backend : FastAPI, Python 3.11+, SQLAlchemy, Pydantic V2
- DB : PostgreSQL 16, Redis (cache)
- Deploy : Docker, Nginx, https://habit.apps.ilanewep.cloud

**API Character endpoints existants :**
```
GET    /api/characters/me     → Profil personnage du user connecté
PATCH  /api/characters/me     → Modifier apparence/équipement
GET    /api/stats/overview    → XP, niveau, streaks
```

## Le standard LPC (Liberated Pixel Cup)

Sprites pixel-art open source avec animations standardisées.
- Frames 64×64 pixels, spritesheet universel 832×1344 (13 cols × 21 rows)
- Animations : walk(9f), spellcast(7f), thrust(8f), slash(6f), shoot(13f), hurt(6f)
- 4 directions : up, left, down, right
- Layers superposables : body → legs → torso → hair → weapon → shield
- Licences : CC-BY-SA 3.0, GPL 3.0, CC0, OGA-BY (crédits obligatoires)
- Générateur en ligne : https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator/

## Workflow — Création de personnage HabitQuest

### Étape 1 — Analyse du besoin

Détermine ce que l'utilisateur veut parmi ces scénarios :

| Scénario | Action |
|----------|--------|
| Nouveau composant Character Creator | Génère le composant complet avec preview animée |
| Modifier l'apparence du perso | Génère le code de mise à jour + appel API PATCH |
| Système de progression XP | Génère les hooks et composants de level-up |
| Boutique d'équipements | Génère la page Shop avec déblocage par niveau |
| Animation sur le dashboard | Génère le widget avatar animé pour le dashboard |
| Page personnage complète | Génère la page `/character` avec stats + équipement + preview |

### Étape 2 — Configuration du personnage

Construis la config en s'appuyant sur `references/lpc-assets-catalog.md` :

```typescript
// frontend/src/types/character.ts
interface CharacterConfig {
  name: string;
  body: {
    type: 'male' | 'female' | 'muscular' | 'child' | 'teen' | 'elderly';
    skinColor: string;  // light, medium, dark, orc, etc.
  };
  hair: {
    style: string;      // longhawk, pixie, curly, etc.
    color: string;
  };
  ears: 'human' | 'elven' | 'none';
  equipment: {
    torso: string;      // leather_armor, chain, robe, etc.
    legs: string;       // pants_teal, shorts, etc.
    feet: string;       // boots_brown, sandals, etc.
    weapon: string;     // longsword, staff, bow, etc.
    shield: string;
    headGear: string;
    cape: string;
  };
  // Lié à la progression HabitQuest
  level: number;
  xp: number;
  unlockedItems: string[];
}
```

### Étape 3 — Génération des composants

Génère des composants **Next.js + TypeScript + Tailwind** qui s'intègrent
dans l'architecture existante de HabitQuest.

**Principes :**
- TypeScript strict (pas de `any`)
- Tailwind CSS uniquement (pas de CSS inline sauf pour Canvas)
- `"use client"` pour les composants interactifs
- Custom hooks pour la logique d'animation
- Appels API via le client existant (`lib/api.ts`)
- Responsive (mobile-first, l'app tourne aussi sur mobile)

Consulte `references/habitquest-components.md` pour les patterns de composants.

### Étape 4 — Intégration API Backend

Le backend FastAPI gère la persistance du personnage. Le skill peut aussi
générer les modèles SQLAlchemy et schémas Pydantic si nécessaire.

Consulte `references/habitquest-api-integration.md` pour les patterns backend.

### Étape 5 — Système de progression

Le cœur de HabitQuest : compléter des habitudes → gagner XP → monter de niveau
→ débloquer des équipements LPC pour son avatar.

Consulte `references/habitquest-progression.md` pour le système complet.

### Étape 6 — Livraison

Génère les fichiers directement dans la structure du projet :

```
# Composants frontend
frontend/src/components/character/
  ├── CharacterSprite.tsx      # Widget d'animation sprite
  ├── CharacterCreator.tsx     # Page de création
  ├── CharacterPreview.tsx     # Preview avec contrôles
  ├── EquipmentSlot.tsx        # Slot d'équipement
  └── CharacterSheet.tsx       # Fiche complète du perso

frontend/src/hooks/
  ├── useSpriteAnimation.ts    # Hook d'animation Canvas
  └── useCharacter.ts          # Hook de gestion perso + API

frontend/src/types/
  └── character.ts             # Types TypeScript

# Backend (si nécessaire)
backend/app/models/character.py
backend/app/schemas/character.py
backend/app/routers/characters.py
```

## Règles critiques

1. **TypeScript strict** — Tous les composants doivent être typés. Interfaces
   dans `types/character.ts`. Pas de `any`.

2. **Tailwind only** — Styling via classes Tailwind. Exception : propriétés
   Canvas (`imageSmoothingEnabled`) et `image-rendering: pixelated`.

3. **"use client"** — Les composants avec Canvas/hooks d'état DOIVENT avoir
   `"use client"` en première ligne (Next.js 14 App Router).

4. **Pixel-perfect** — Toujours appliquer `image-rendering: pixelated` et
   `ctx.imageSmoothingEnabled = false` pour le rendu des sprites.

5. **Crédits LPC** — Inclure les crédits dans un fichier dédié et un lien
   dans l'interface. Voir `references/licensing.md`.

6. **Approche spritesheet** — Privilégier l'approche "PNG composite" :
   - L'utilisateur génère son sprite sur le générateur LPC en ligne
   - Le PNG est uploadé et stocké (ou une URL est sauvegardée)
   - Le code anime ce PNG unique
   - Alternative : chargement dynamique des layers depuis le CDN GitHub

7. **Responsive** — Le sprite doit s'adapter. Utiliser des tailles relatives
   ou des breakpoints Tailwind (`scale` via props).

8. **Performance** — Utiliser `requestAnimationFrame`, cleanup dans `useEffect`,
   `useCallback` pour les handlers d'animation.

## Fichiers de référence

| Fichier | Contenu | Quand le lire |
|---------|---------|---------------|
| `references/habitquest-components.md` | Composants Next.js/TS/Tailwind | Toujours pour du frontend |
| `references/habitquest-api-integration.md` | Modèles et routes FastAPI | Quand on touche au backend |
| `references/habitquest-progression.md` | Système XP/niveaux/boutique | Progression et gamification |
| `references/lpc-assets-catalog.md` | Catalogue des sprites LPC | Choix d'apparence/équipement |
| `references/animation-frames.md` | Détail des frames par animation | Code d'animation |
| `references/web-integration.md` | Patterns Canvas/CSS génériques | Référence bas niveau |
| `references/licensing.md` | Licences LPC et crédits | Toujours (crédits obligatoires) |
| `references/svg-character-guide.md` | Alternative SVG (non pixel-art) | Si l'utilisateur veut du moderne |

**Lis les fichiers pertinents selon le contexte — pas tous systématiquement.**
