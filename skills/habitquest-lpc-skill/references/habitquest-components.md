# Composants HabitQuest — Next.js / TypeScript / Tailwind

Patterns de composants prêts à intégrer dans le frontend HabitQuest.
Tous les composants utilisent Next.js 14 App Router, React 18, TypeScript strict, et Tailwind CSS.

---

## Types partagés

```typescript
// frontend/src/types/character.ts

/** Directions du sprite LPC */
export type SpriteDirection = 'up' | 'down' | 'left' | 'right';

/** Animations disponibles dans le spritesheet LPC standard */
export type SpriteAnimation =
  | 'idle'
  | 'walk'
  | 'slash'
  | 'thrust'
  | 'spellcast'
  | 'shoot'
  | 'hurt';

/** Configuration des animations LPC (spritesheet universel 832×1344) */
export const LPC_ANIMATIONS: Record<
  SpriteAnimation,
  { startRow: number; frames: number }
> = {
  spellcast: { startRow: 0, frames: 7 },
  thrust:    { startRow: 4, frames: 8 },
  walk:      { startRow: 8, frames: 9 },
  slash:     { startRow: 12, frames: 6 },
  shoot:     { startRow: 16, frames: 13 },
  hurt:      { startRow: 20, frames: 6 },
  idle:      { startRow: 8, frames: 1 },
};

export const LPC_DIRECTION_OFFSET: Record<SpriteDirection, number> = {
  up: 0,
  left: 1,
  down: 2,
  right: 3,
};

export const LPC_FRAME_SIZE = 64;
export const LPC_SHEET_COLS = 13;
export const LPC_SHEET_ROWS = 21;

/** Équipement du personnage — correspond aux slots visuels LPC */
export interface CharacterEquipment {
  torso: string | null;
  legs: string | null;
  feet: string | null;
  weapon: string | null;
  shield: string | null;
  headGear: string | null;
  cape: string | null;
}

/** Apparence du personnage */
export interface CharacterAppearance {
  bodyType: 'male' | 'female';
  skinColor: string;
  hairStyle: string;
  hairColor: string;
  ears: 'human' | 'elven';
}

/** Personnage HabitQuest complet */
export interface HabitQuestCharacter {
  id: string;
  userId: string;
  name: string;
  level: number;
  xp: number;
  xpToNextLevel: number;
  appearance: CharacterAppearance;
  equipment: CharacterEquipment;
  spriteSheetUrl: string | null;
  createdAt: string;
  updatedAt: string;
}

/** Item de la boutique */
export interface ShopItem {
  id: string;
  name: string;
  slot: keyof CharacterEquipment;
  spriteLayer: string;        // chemin dans le repo LPC
  requiredLevel: number;
  cost: number;               // en pièces d'or (earned via habits)
  description: string;
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
}
```

---

## Hook d'animation Sprite

```typescript
// frontend/src/hooks/useSpriteAnimation.ts
"use client";

import { useRef, useEffect, useCallback } from 'react';
import {
  LPC_ANIMATIONS,
  LPC_DIRECTION_OFFSET,
  LPC_FRAME_SIZE,
  type SpriteAnimation,
  type SpriteDirection,
} from '@/types/character';

interface UseSpriteAnimationOptions {
  spriteSheetUrl: string;
  animation: SpriteAnimation;
  direction: SpriteDirection;
  scale?: number;
  fps?: number;
  paused?: boolean;
}

export function useSpriteAnimation({
  spriteSheetUrl,
  animation,
  direction,
  scale = 2,
  fps = 8,
  paused = false,
}: UseSpriteAnimationOptions) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const spriteRef = useRef<HTMLImageElement | null>(null);
  const frameRef = useRef(0);
  const lastFrameTimeRef = useRef(0);
  const animRef = useRef(animation);
  const dirRef = useRef(direction);

  // Sync refs
  useEffect(() => {
    if (animRef.current !== animation) {
      animRef.current = animation;
      frameRef.current = 0;
    }
  }, [animation]);

  useEffect(() => {
    dirRef.current = direction;
  }, [direction]);

  // Load sprite image
  useEffect(() => {
    if (!spriteSheetUrl) return;
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      spriteRef.current = img;
    };
    img.src = spriteSheetUrl;
  }, [spriteSheetUrl]);

  // Animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const displaySize = LPC_FRAME_SIZE * scale;
    canvas.width = displaySize;
    canvas.height = displaySize;

    const frameInterval = 1000 / fps;
    let animId: number;

    const render = (timestamp: number) => {
      animId = requestAnimationFrame(render);

      if (!spriteRef.current) return;

      // Advance frame
      if (!paused && timestamp - lastFrameTimeRef.current >= frameInterval) {
        lastFrameTimeRef.current = timestamp;
        const anim = LPC_ANIMATIONS[animRef.current];
        frameRef.current = (frameRef.current + 1) % anim.frames;
      }

      // Draw
      ctx.imageSmoothingEnabled = false;
      ctx.clearRect(0, 0, displaySize, displaySize);

      const anim = LPC_ANIMATIONS[animRef.current];
      const dirOffset = animRef.current === 'hurt'
        ? 0
        : LPC_DIRECTION_OFFSET[dirRef.current];
      const row = anim.startRow + dirOffset;
      const sx = frameRef.current * LPC_FRAME_SIZE;
      const sy = row * LPC_FRAME_SIZE;

      ctx.drawImage(
        spriteRef.current,
        sx, sy, LPC_FRAME_SIZE, LPC_FRAME_SIZE,
        0, 0, displaySize, displaySize
      );
    };

    animId = requestAnimationFrame(render);
    return () => cancelAnimationFrame(animId);
  }, [scale, fps, paused]);

  return canvasRef;
}
```

---

## Composant CharacterSprite — Widget d'avatar animé

Le composant de base utilisable partout (dashboard, profil, combat...).

```tsx
// frontend/src/components/character/CharacterSprite.tsx
"use client";

import { useSpriteAnimation } from '@/hooks/useSpriteAnimation';
import type { SpriteAnimation, SpriteDirection } from '@/types/character';

interface CharacterSpriteProps {
  spriteSheetUrl: string;
  animation?: SpriteAnimation;
  direction?: SpriteDirection;
  scale?: number;
  fps?: number;
  paused?: boolean;
  className?: string;
}

export function CharacterSprite({
  spriteSheetUrl,
  animation = 'idle',
  direction = 'down',
  scale = 2,
  fps = 8,
  paused = false,
  className = '',
}: CharacterSpriteProps) {
  const canvasRef = useSpriteAnimation({
    spriteSheetUrl,
    animation,
    direction,
    scale,
    fps,
    paused,
  });

  return (
    <canvas
      ref={canvasRef}
      className={`[image-rendering:pixelated] ${className}`}
      style={{ width: 64 * scale, height: 64 * scale }}
    />
  );
}
```

---

## Composant CharacterPreview — Preview interactive avec contrôles

Pour la page de création/personnalisation du personnage.

```tsx
// frontend/src/components/character/CharacterPreview.tsx
"use client";

import { useState } from 'react';
import { CharacterSprite } from './CharacterSprite';
import type { SpriteAnimation, SpriteDirection } from '@/types/character';

interface CharacterPreviewProps {
  spriteSheetUrl: string;
  scale?: number;
  showAnimControls?: boolean;
  showDirControls?: boolean;
  className?: string;
}

const ANIM_LABELS: { key: SpriteAnimation; label: string; icon: string }[] = [
  { key: 'idle', label: 'Repos', icon: '🧍' },
  { key: 'walk', label: 'Marcher', icon: '🚶' },
  { key: 'slash', label: 'Attaque', icon: '⚔️' },
  { key: 'spellcast', label: 'Sort', icon: '✨' },
  { key: 'hurt', label: 'Dégâts', icon: '💥' },
];

const DIR_LABELS: { key: SpriteDirection; label: string }[] = [
  { key: 'up', label: '↑' },
  { key: 'left', label: '←' },
  { key: 'down', label: '↓' },
  { key: 'right', label: '→' },
];

export function CharacterPreview({
  spriteSheetUrl,
  scale = 3,
  showAnimControls = true,
  showDirControls = true,
  className = '',
}: CharacterPreviewProps) {
  const [animation, setAnimation] = useState<SpriteAnimation>('idle');
  const [direction, setDirection] = useState<SpriteDirection>('down');

  return (
    <div className={`flex flex-col items-center gap-4 ${className}`}>
      {/* Zone de preview avec fond thématique */}
      <div className="relative rounded-xl bg-gradient-to-b from-indigo-900/50 to-purple-900/50 border border-indigo-500/30 p-6">
        <CharacterSprite
          spriteSheetUrl={spriteSheetUrl}
          animation={animation}
          direction={direction}
          scale={scale}
        />

        {/* Effet de sol */}
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 w-16 h-3 rounded-full bg-black/30 blur-sm" />
      </div>

      {/* Contrôles d'animation */}
      {showAnimControls && (
        <div className="flex flex-wrap justify-center gap-2">
          {ANIM_LABELS.map(({ key, label, icon }) => (
            <button
              key={key}
              onClick={() => setAnimation(key)}
              className={`
                px-3 py-1.5 rounded-lg text-xs font-medium transition-all
                ${animation === key
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-200'
                }
              `}
            >
              <span className="mr-1">{icon}</span>
              {label}
            </button>
          ))}
        </div>
      )}

      {/* Contrôles de direction */}
      {showDirControls && (
        <div className="grid grid-cols-3 gap-1 w-24">
          <div /> {/* empty cell */}
          <button
            onClick={() => setDirection('up')}
            className={`p-1.5 rounded text-sm font-bold transition-colors ${
              direction === 'up' ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400'
            }`}
          >
            ↑
          </button>
          <div />
          <button
            onClick={() => setDirection('left')}
            className={`p-1.5 rounded text-sm font-bold transition-colors ${
              direction === 'left' ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400'
            }`}
          >
            ←
          </button>
          <button
            onClick={() => setDirection('down')}
            className={`p-1.5 rounded text-sm font-bold transition-colors ${
              direction === 'down' ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400'
            }`}
          >
            ↓
          </button>
          <button
            onClick={() => setDirection('right')}
            className={`p-1.5 rounded text-sm font-bold transition-colors ${
              direction === 'right' ? 'bg-indigo-600 text-white' : 'bg-gray-800 text-gray-400'
            }`}
          >
            →
          </button>
        </div>
      )}
    </div>
  );
}
```

---

## Composant EquipmentSlot — Slot d'équipement interactif

```tsx
// frontend/src/components/character/EquipmentSlot.tsx
"use client";

import type { CharacterEquipment } from '@/types/character';

interface EquipmentSlotProps {
  slot: keyof CharacterEquipment;
  itemName: string | null;
  icon: string;
  label: string;
  locked?: boolean;
  onClick?: () => void;
}

const RARITY_COLORS: Record<string, string> = {
  common: 'border-gray-500',
  uncommon: 'border-green-500',
  rare: 'border-blue-500',
  epic: 'border-purple-500',
  legendary: 'border-yellow-500',
};

export function EquipmentSlot({
  slot,
  itemName,
  icon,
  label,
  locked = false,
  onClick,
}: EquipmentSlotProps) {
  return (
    <button
      onClick={onClick}
      disabled={locked}
      className={`
        relative flex flex-col items-center gap-1 p-3 rounded-lg
        border-2 transition-all min-w-[80px]
        ${locked
          ? 'border-gray-700 bg-gray-900/50 opacity-50 cursor-not-allowed'
          : itemName
            ? 'border-indigo-500/50 bg-indigo-900/20 hover:bg-indigo-900/40 cursor-pointer'
            : 'border-dashed border-gray-600 bg-gray-900/30 hover:border-gray-400 cursor-pointer'
        }
      `}
    >
      <span className="text-2xl">{locked ? '🔒' : icon}</span>
      <span className="text-[10px] text-gray-400 uppercase tracking-wider">{label}</span>
      {itemName && (
        <span className="text-xs text-indigo-300 truncate max-w-full">{itemName}</span>
      )}
    </button>
  );
}
```

---

## Composant CharacterSheet — Fiche complète du personnage

```tsx
// frontend/src/components/character/CharacterSheet.tsx
"use client";

import { CharacterPreview } from './CharacterPreview';
import { EquipmentSlot } from './EquipmentSlot';
import type { HabitQuestCharacter } from '@/types/character';

interface CharacterSheetProps {
  character: HabitQuestCharacter;
  onEquipmentClick?: (slot: string) => void;
}

export function CharacterSheet({ character, onEquipmentClick }: CharacterSheetProps) {
  const xpPercent = Math.round((character.xp / character.xpToNextLevel) * 100);

  const equipmentSlots = [
    { slot: 'headGear' as const, icon: '👑', label: 'Tête' },
    { slot: 'torso' as const, icon: '🛡️', label: 'Torse' },
    { slot: 'legs' as const, icon: '👖', label: 'Jambes' },
    { slot: 'feet' as const, icon: '👢', label: 'Pieds' },
    { slot: 'weapon' as const, icon: '⚔️', label: 'Arme' },
    { slot: 'shield' as const, icon: '🛡️', label: 'Bouclier' },
    { slot: 'cape' as const, icon: '🧣', label: 'Cape' },
  ];

  return (
    <div className="flex flex-col lg:flex-row gap-8 p-6">
      {/* Colonne gauche : Preview */}
      <div className="flex flex-col items-center gap-4">
        {character.spriteSheetUrl && (
          <CharacterPreview
            spriteSheetUrl={character.spriteSheetUrl}
            scale={3}
          />
        )}

        {/* Nom et niveau */}
        <div className="text-center">
          <h2 className="text-xl font-bold text-white">{character.name}</h2>
          <p className="text-sm text-indigo-400">Niveau {character.level}</p>
        </div>

        {/* Barre d'XP */}
        <div className="w-full max-w-xs">
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>XP</span>
            <span>{character.xp} / {character.xpToNextLevel}</span>
          </div>
          <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-indigo-600 to-purple-500 rounded-full transition-all duration-500"
              style={{ width: `${xpPercent}%` }}
            />
          </div>
        </div>
      </div>

      {/* Colonne droite : Équipement */}
      <div className="flex-1">
        <h3 className="text-lg font-semibold text-white mb-4">Équipement</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {equipmentSlots.map(({ slot, icon, label }) => (
            <EquipmentSlot
              key={slot}
              slot={slot}
              itemName={character.equipment[slot]}
              icon={icon}
              label={label}
              onClick={() => onEquipmentClick?.(slot)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## Widget Dashboard — Avatar animé compact

Pour afficher le personnage dans la sidebar ou le header du dashboard.

```tsx
// frontend/src/components/character/DashboardAvatar.tsx
"use client";

import { CharacterSprite } from './CharacterSprite';
import type { HabitQuestCharacter } from '@/types/character';

interface DashboardAvatarProps {
  character: HabitQuestCharacter;
  size?: 'sm' | 'md' | 'lg';
}

const SCALE_MAP = { sm: 1, md: 2, lg: 3 };

export function DashboardAvatar({ character, size = 'md' }: DashboardAvatarProps) {
  const scale = SCALE_MAP[size];
  const xpPercent = Math.round((character.xp / character.xpToNextLevel) * 100);

  return (
    <div className="flex items-center gap-3 p-2 rounded-lg bg-gray-800/50">
      {character.spriteSheetUrl ? (
        <CharacterSprite
          spriteSheetUrl={character.spriteSheetUrl}
          animation="idle"
          direction="down"
          scale={scale}
        />
      ) : (
        <div
          className="rounded bg-gray-700 flex items-center justify-center text-2xl"
          style={{ width: 64 * scale, height: 64 * scale }}
        >
          🧙
        </div>
      )}

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white truncate">{character.name}</p>
        <p className="text-xs text-indigo-400">Niv. {character.level}</p>
        <div className="mt-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-indigo-500 rounded-full transition-all"
            style={{ width: `${xpPercent}%` }}
          />
        </div>
      </div>
    </div>
  );
}
```

---

## Hook useCharacter — Gestion du personnage + API

```typescript
// frontend/src/hooks/useCharacter.ts
"use client";

import { useState, useEffect, useCallback } from 'react';
import type { HabitQuestCharacter, CharacterEquipment, CharacterAppearance } from '@/types/character';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function useCharacter() {
  const [character, setCharacter] = useState<HabitQuestCharacter | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch character
  const fetchCharacter = useCallback(async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/api/characters/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Failed to fetch character');
      const data: HabitQuestCharacter = await res.json();
      setCharacter(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, []);

  // Update equipment
  const updateEquipment = useCallback(async (equipment: Partial<CharacterEquipment>) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/api/characters/me`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ equipment }),
      });
      if (!res.ok) throw new Error('Failed to update equipment');
      const data: HabitQuestCharacter = await res.json();
      setCharacter(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  }, []);

  // Update appearance
  const updateAppearance = useCallback(async (appearance: Partial<CharacterAppearance>) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/api/characters/me`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ appearance }),
      });
      if (!res.ok) throw new Error('Failed to update appearance');
      const data: HabitQuestCharacter = await res.json();
      setCharacter(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  }, []);

  // Update spritesheet URL
  const updateSpriteSheet = useCallback(async (spriteSheetUrl: string) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${API_BASE}/api/characters/me`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ spriteSheetUrl }),
      });
      if (!res.ok) throw new Error('Failed to update spritesheet');
      const data: HabitQuestCharacter = await res.json();
      setCharacter(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  }, []);

  useEffect(() => {
    fetchCharacter();
  }, [fetchCharacter]);

  return {
    character,
    loading,
    error,
    updateEquipment,
    updateAppearance,
    updateSpriteSheet,
    refetch: fetchCharacter,
  };
}
```

---

## Notes d'intégration

**Ordre d'implémentation recommandé :**

1. `types/character.ts` — Types et constantes LPC
2. `hooks/useSpriteAnimation.ts` — Hook Canvas de base
3. `components/character/CharacterSprite.tsx` — Widget réutilisable
4. `hooks/useCharacter.ts` — Connexion à l'API
5. `components/character/DashboardAvatar.tsx` — Intégration dashboard
6. `components/character/CharacterPreview.tsx` — Pour la page personnage
7. `components/character/EquipmentSlot.tsx` + `CharacterSheet.tsx` — Fiche complète

**Où placer le sprite dans le layout :**
- Dashboard sidebar : `DashboardAvatar` avec `size="sm"`
- Header : `CharacterSprite` avec `scale={1}` et `animation="idle"`
- Page `/character` : `CharacterSheet` complet
- Combat PvP : deux `CharacterSprite` face à face avec animations dynamiques
