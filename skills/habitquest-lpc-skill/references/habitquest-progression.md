# Système de Progression HabitQuest

Comment les habitudes quotidiennes alimentent la progression RPG et le déverrouillage
des équipements LPC pour l'avatar du joueur.

---

## Boucle de gameplay

```
┌──────────────────────────────────────────────────────────────┐
│  Compléter une habitude                                       │
│       │                                                       │
│       ├──→ +XP (selon difficulté + streak)                   │
│       ├──→ +Gold (pour la boutique)                          │
│       └──→ +Streak (bonus cumulatif)                         │
│                                                               │
│  XP ≥ seuil du niveau ?                                      │
│       │                                                       │
│       ├── OUI → LEVEL UP ! 🎉                                │
│       │      ├── Déblocage nouveaux items dans la boutique   │
│       │      ├── Animation de level-up sur l'avatar          │
│       │      └── Notification toast                          │
│       │                                                       │
│       └── NON → Barre d'XP avance (feedback visuel)         │
│                                                               │
│  Gold suffisant + Niveau requis ?                            │
│       │                                                       │
│       └── OUI → Achat en boutique → Nouvel équipement LPC    │
│              └── Le sprite du personnage est mis à jour      │
└──────────────────────────────────────────────────────────────┘
```

---

## Table de progression XP

| Niveau | XP requis | XP cumulé | Items débloqués |
|--------|-----------|-----------|-----------------|
| 1      | 100       | 0         | Pantalon basique |
| 2      | 150       | 100       | Bottes en cuir |
| 3      | 200       | 250       | Chemise blanche |
| 4      | 250       | 450       | Dague |
| 5      | 325       | 700       | Armure de cuir |
| 7      | 425       | 1,450     | Épée longue |
| 8      | 475       | 1,875     | Bouclier rond |
| 10     | 700       | 2,825     | Cotte de mailles, Cape bleue |
| 12     | 800       | 4,325     | Casque en acier |
| 15     | 1,075     | 7,200     | Armure de plaques |
| 18     | 1,350     | 11,075    | Épée à deux mains |
| 20     | 2,000     | 13,775    | Couronne d'or |
| 25     | 2,750     | 24,275    | Cape royale |

**Formule :** `xp_needed = 100 × (1 + (level - 1) × 0.5) + 50 × floor(level / 5)`

---

## XP et Gold par habitude

### XP

| Difficulté | XP de base | Avec streak ×5 | Avec streak ×10 (max) |
|-----------|-----------|----------------|----------------------|
| Facile    | 10        | 15             | 20                   |
| Moyen     | 20        | 30             | 40                   |
| Difficile | 40        | 60             | 80                   |
| Épique    | 75        | 112            | 150                  |

**Bonus streak :** +10% par jour consécutif, plafonné à +100% (10 jours).

### Gold

| Difficulté | Gold |
|-----------|------|
| Facile    | 5    |
| Moyen     | 10   |
| Difficile | 20   |
| Épique    | 40   |

---

## Composant LevelUpNotification

Toast animé qui apparaît lors d'un level-up, avec l'avatar qui exécute une animation de victoire.

```tsx
// frontend/src/components/character/LevelUpNotification.tsx
"use client";

import { useEffect, useState } from 'react';
import { CharacterSprite } from './CharacterSprite';

interface LevelUpNotificationProps {
  newLevel: number;
  spriteSheetUrl: string;
  unlockedItems: string[];
  onClose: () => void;
}

export function LevelUpNotification({
  newLevel,
  spriteSheetUrl,
  unlockedItems,
  onClose,
}: LevelUpNotificationProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Entrée animée
    requestAnimationFrame(() => setVisible(true));
    // Auto-fermeture après 5s
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onClose, 300);
    }, 5000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div
      className={`
        fixed inset-0 z-50 flex items-center justify-center
        bg-black/60 backdrop-blur-sm transition-opacity duration-300
        ${visible ? 'opacity-100' : 'opacity-0'}
      `}
      onClick={onClose}
    >
      <div
        className={`
          bg-gradient-to-b from-indigo-900 to-purple-900
          border-2 border-yellow-400 rounded-2xl p-8
          text-center shadow-2xl shadow-yellow-500/20
          transform transition-all duration-500
          ${visible ? 'scale-100 translate-y-0' : 'scale-75 translate-y-8'}
        `}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Étoiles décoratives */}
        <div className="text-4xl mb-2">⭐ ✨ ⭐</div>

        {/* Titre */}
        <h2 className="text-3xl font-bold text-yellow-400 mb-4">
          Niveau {newLevel} !
        </h2>

        {/* Avatar animé - animation de victoire (spellcast) */}
        <div className="flex justify-center mb-4">
          <CharacterSprite
            spriteSheetUrl={spriteSheetUrl}
            animation="spellcast"
            direction="down"
            scale={3}
          />
        </div>

        {/* Items débloqués */}
        {unlockedItems.length > 0 && (
          <div className="mt-4">
            <p className="text-sm text-indigo-300 mb-2">Nouveaux items débloqués :</p>
            <div className="flex flex-wrap justify-center gap-2">
              {unlockedItems.map((item) => (
                <span
                  key={item}
                  className="px-3 py-1 bg-indigo-800/50 rounded-full text-sm text-yellow-300"
                >
                  🎁 {item}
                </span>
              ))}
            </div>
          </div>
        )}

        <button
          onClick={onClose}
          className="mt-6 px-6 py-2 bg-yellow-500 text-black font-bold rounded-lg hover:bg-yellow-400 transition-colors"
        >
          Continuer l'aventure
        </button>
      </div>
    </div>
  );
}
```

---

## Composant XPBar — Barre d'XP avec animation

```tsx
// frontend/src/components/character/XPBar.tsx
"use client";

import { useEffect, useState } from 'react';

interface XPBarProps {
  currentXP: number;
  xpToNextLevel: number;
  level: number;
  className?: string;
  showLabel?: boolean;
  animated?: boolean;
}

export function XPBar({
  currentXP,
  xpToNextLevel,
  level,
  className = '',
  showLabel = true,
  animated = true,
}: XPBarProps) {
  const [displayPercent, setDisplayPercent] = useState(0);
  const targetPercent = Math.min((currentXP / xpToNextLevel) * 100, 100);

  useEffect(() => {
    if (animated) {
      // Animation douce de la barre
      const timer = setTimeout(() => setDisplayPercent(targetPercent), 100);
      return () => clearTimeout(timer);
    } else {
      setDisplayPercent(targetPercent);
    }
  }, [targetPercent, animated]);

  return (
    <div className={`w-full ${className}`}>
      {showLabel && (
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs font-medium text-indigo-400">
            Niv. {level}
          </span>
          <span className="text-xs text-gray-400">
            {currentXP} / {xpToNextLevel} XP
          </span>
        </div>
      )}
      <div className="relative h-4 bg-gray-800 rounded-full overflow-hidden border border-gray-700">
        <div
          className="absolute inset-y-0 left-0 bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-500 rounded-full transition-all duration-1000 ease-out"
          style={{ width: `${displayPercent}%` }}
        >
          {/* Effet de brillance */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse" />
        </div>
      </div>
    </div>
  );
}
```

---

## Composant ShopPage — Page Boutique

```tsx
// frontend/src/app/shop/page.tsx
"use client";

import { useState, useEffect } from 'react';
import { useCharacter } from '@/hooks/useCharacter';
import { CharacterPreview } from '@/components/character/CharacterPreview';
import type { ShopItem } from '@/types/character';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const RARITY_STYLES: Record<string, { bg: string; border: string; text: string }> = {
  common:    { bg: 'bg-gray-800', border: 'border-gray-600', text: 'text-gray-300' },
  uncommon:  { bg: 'bg-green-900/30', border: 'border-green-600', text: 'text-green-400' },
  rare:      { bg: 'bg-blue-900/30', border: 'border-blue-500', text: 'text-blue-400' },
  epic:      { bg: 'bg-purple-900/30', border: 'border-purple-500', text: 'text-purple-400' },
  legendary: { bg: 'bg-yellow-900/30', border: 'border-yellow-500', text: 'text-yellow-400' },
};

const SLOT_ICONS: Record<string, string> = {
  torso: '🛡️', legs: '👖', feet: '👢', weapon: '⚔️',
  shield: '🛡️', headGear: '👑', cape: '🧣',
};

export default function ShopPage() {
  const { character, refetch } = useCharacter();
  const [items, setItems] = useState<ShopItem[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
  const [purchasing, setPurchasing] = useState<string | null>(null);

  useEffect(() => {
    fetchItems();
  }, []);

  async function fetchItems() {
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE}/api/shop/items`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) setItems(await res.json());
  }

  async function handlePurchase(itemId: string) {
    setPurchasing(itemId);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/api/shop/purchase`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ itemId }),
      });
      if (res.ok) {
        await refetch();
        // TODO: show success toast
      } else {
        const err = await res.json();
        alert(err.detail); // Replace with toast in production
      }
    } finally {
      setPurchasing(null);
    }
  }

  const filteredItems = selectedSlot
    ? items.filter((i) => i.slot === selectedSlot)
    : items;

  const slots = ['torso', 'legs', 'feet', 'weapon', 'shield', 'headGear', 'cape'];

  return (
    <div className="min-h-screen bg-gray-950 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">🏪 Boutique</h1>
        <p className="text-gray-400 mb-6">
          Dépensez votre or pour équiper votre personnage.
          Complétez des habitudes pour gagner plus d'or !
        </p>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar : Preview personnage + gold */}
          <div className="lg:w-64 flex-shrink-0">
            {character?.spriteSheetUrl && (
              <CharacterPreview
                spriteSheetUrl={character.spriteSheetUrl}
                scale={3}
                showAnimControls={false}
                showDirControls={false}
              />
            )}
            <div className="mt-4 p-3 bg-gray-800/50 rounded-lg text-center">
              <span className="text-yellow-400 text-2xl">🪙</span>
              <span className="ml-2 text-xl font-bold text-yellow-300">
                {character?.gold ?? 0}
              </span>
              <p className="text-xs text-gray-400 mt-1">Or disponible</p>
            </div>

            {/* Filtre par slot */}
            <div className="mt-4 flex flex-wrap gap-1">
              <button
                onClick={() => setSelectedSlot(null)}
                className={`px-2 py-1 rounded text-xs ${
                  !selectedSlot ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400'
                }`}
              >
                Tout
              </button>
              {slots.map((s) => (
                <button
                  key={s}
                  onClick={() => setSelectedSlot(s)}
                  className={`px-2 py-1 rounded text-xs ${
                    selectedSlot === s ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400'
                  }`}
                >
                  {SLOT_ICONS[s]} {s}
                </button>
              ))}
            </div>
          </div>

          {/* Grille d'items */}
          <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredItems.map((item) => {
              const style = RARITY_STYLES[item.rarity] || RARITY_STYLES.common;
              const owned = character?.unlockedItems?.includes(item.id);
              const canAfford = (character?.gold ?? 0) >= item.cost;
              const levelOk = (character?.level ?? 1) >= item.requiredLevel;

              return (
                <div
                  key={item.id}
                  className={`
                    ${style.bg} border ${style.border} rounded-xl p-4
                    transition-all hover:shadow-lg
                    ${owned ? 'opacity-60' : ''}
                  `}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-semibold text-white">{item.name}</h3>
                      <span className={`text-xs ${style.text} uppercase`}>
                        {item.rarity}
                      </span>
                    </div>
                    <span className="text-lg">{SLOT_ICONS[item.slot] || '📦'}</span>
                  </div>

                  <p className="text-sm text-gray-400 mb-3">{item.description}</p>

                  <div className="flex items-center justify-between">
                    <div className="text-sm">
                      <span className="text-yellow-400">🪙 {item.cost}</span>
                      <span className="text-gray-500 ml-2">Niv. {item.requiredLevel}</span>
                    </div>

                    {owned ? (
                      <span className="text-xs text-green-400 font-medium">✅ Possédé</span>
                    ) : (
                      <button
                        onClick={() => handlePurchase(item.id)}
                        disabled={!canAfford || !levelOk || purchasing === item.id}
                        className={`
                          px-3 py-1 rounded-lg text-xs font-medium transition-colors
                          ${canAfford && levelOk
                            ? 'bg-indigo-600 text-white hover:bg-indigo-500'
                            : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                          }
                        `}
                      >
                        {purchasing === item.id ? '...' : !levelOk ? `Niv. ${item.requiredLevel}` : 'Acheter'}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

## Hook useLevelUp — Détection et gestion du level-up côté client

```typescript
// frontend/src/hooks/useLevelUp.ts
"use client";

import { useState, useCallback, useRef } from 'react';
import type { HabitQuestCharacter } from '@/types/character';

interface LevelUpInfo {
  newLevel: number;
  unlockedItems: string[];
}

export function useLevelUp() {
  const [levelUpInfo, setLevelUpInfo] = useState<LevelUpInfo | null>(null);
  const previousLevelRef = useRef<number>(0);

  /** 
   * Appelle cette fonction après chaque réponse API qui contient le character.
   * Elle détecte si le niveau a augmenté.
   */
  const checkLevelUp = useCallback((character: HabitQuestCharacter, newItems: string[] = []) => {
    if (previousLevelRef.current > 0 && character.level > previousLevelRef.current) {
      setLevelUpInfo({
        newLevel: character.level,
        unlockedItems: newItems,
      });
    }
    previousLevelRef.current = character.level;
  }, []);

  const dismissLevelUp = useCallback(() => {
    setLevelUpInfo(null);
  }, []);

  return {
    levelUpInfo,
    checkLevelUp,
    dismissLevelUp,
  };
}
```

---

## Intégration dans le flux de complétion d'habitude

Quand l'utilisateur coche une habitude, le backend :
1. Marque l'habitude comme complétée
2. Calcule XP + Gold gagnés
3. Ajoute au personnage
4. Vérifie le level-up
5. Retourne le character mis à jour

```python
# Dans le endpoint POST /api/completions
from app.services.progression import (
    xp_for_habit_completion,
    gold_for_habit_completion,
    check_level_up,
    calculate_xp_to_next_level,
)

# ... après avoir créé la completion ...
xp_gained = xp_for_habit_completion(habit.difficulty, streak_count)
gold_gained = gold_for_habit_completion(habit.difficulty)

character.xp += xp_gained
character.gold += gold_gained

leveled_up = check_level_up(character)
newly_unlocked = []
if leveled_up:
    # Trouver les items débloqués au nouveau niveau
    newly_unlocked = db.query(ShopItem).filter(
        ShopItem.required_level == character.level
    ).all()

db.commit()

return {
    "completion": completion,
    "xpGained": xp_gained,
    "goldGained": gold_gained,
    "leveledUp": leveled_up,
    "newLevel": character.level if leveled_up else None,
    "newlyUnlockedItems": [i.name for i in newly_unlocked],
    "character": character,
}
```
