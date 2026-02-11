// ============================================
// HabitQuest LPC Character Types
// Fusion du code actuel + skill HabitQuest LPC
// ============================================

/** Directions du sprite LPC (4 directions) */
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
export const LPC_ANIMATIONS: Record<SpriteAnimation, { startRow: number; frames: number }> = {
  spellcast: { startRow: 0, frames: 7 },
  thrust:    { startRow: 4, frames: 8 },
  walk:      { startRow: 8, frames: 9 },
  slash:     { startRow: 12, frames: 6 },
  shoot:     { startRow: 16, frames: 13 },
  hurt:      { startRow: 20, frames: 6 },
  idle:      { startRow: 8, frames: 1 },  // Walk frame 0 = idle
};

/** Offset de direction dans le spritesheet */
export const LPC_DIRECTION_OFFSET: Record<SpriteDirection, number> = {
  up: 0,
  left: 1,
  down: 2,
  right: 3,
};

/** Constantes LPC */
export const LPC_FRAME_SIZE = 64;
export const LPC_SHEET_COLS = 13;
export const LPC_SHEET_ROWS = 21;

/** Classes de personnage HabitQuest */
export type CharacterClass = 'warrior' | 'mage' | 'ranger' | 'paladin' | 'assassin';

/** Configuration par classe */
export const CLASS_CONFIG: Record<CharacterClass, {
  name: string;
  defaultGender: 'male' | 'female';
  defaultArmor: 'none' | 'robe' | 'leather' | 'plate';
  defaultHair: string;
  ringColor: string;
  bonus: string;
}> = {
  warrior:  { name: 'Guerrier',  defaultGender: 'male',   defaultArmor: 'plate',   defaultHair: 'male',     ringColor: 'ring-red-500',    bonus: '+20% XP tâches' },
  mage:     { name: 'Mage',      defaultGender: 'female', defaultArmor: 'robe',    defaultHair: 'ponytail', ringColor: 'ring-purple-500', bonus: '+20% pièces' },
  ranger:   { name: 'Rôdeur',    defaultGender: 'male',   defaultArmor: 'leather', defaultHair: 'male',     ringColor: 'ring-green-500',  bonus: '+20% XP habitudes' },
  paladin:  { name: 'Paladin',   defaultGender: 'male',   defaultArmor: 'plate',   defaultHair: 'male',     ringColor: 'ring-yellow-500', bonus: '+10% tout XP' },
  assassin: { name: 'Assassin',  defaultGender: 'female', defaultArmor: 'leather', defaultHair: 'female',   ringColor: 'ring-pink-500',   bonus: '+30% streak' },
};

/** Tier de rareté selon le niveau */
export type RarityTier = 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';

export const LEVEL_TIERS: { minLevel: number; tier: RarityTier; ring: string; glow: string }[] = [
  { minLevel: 20, tier: 'legendary', ring: 'ring-yellow-400', glow: 'shadow-yellow-500/50' },
  { minLevel: 15, tier: 'epic',      ring: 'ring-purple-400', glow: 'shadow-purple-500/50' },
  { minLevel: 10, tier: 'rare',      ring: 'ring-blue-400',   glow: 'shadow-blue-500/50' },
  { minLevel: 5,  tier: 'uncommon',  ring: 'ring-green-400',  glow: 'shadow-green-500/50' },
  { minLevel: 0,  tier: 'common',    ring: 'ring-gray-400',   glow: '' },
];

export function getTierByLevel(level: number) {
  return LEVEL_TIERS.find(t => level >= t.minLevel) || LEVEL_TIERS[LEVEL_TIERS.length - 1];
}

/** Armure selon le niveau */
export type ArmorTier = 'none' | 'robe' | 'leather' | 'plate';

export function getArmorByLevel(level: number): ArmorTier {
  if (level >= 15) return 'plate';
  if (level >= 8) return 'leather';
  if (level >= 3) return 'robe';
  return 'none';
}

/** Équipement du personnage */
export interface CharacterEquipment {
  weapon: string | null;
  armor: string | null;
  helmet: string | null;
  accessory: string | null;
  pet: string | null;
}

/** Apparence du personnage */
export interface CharacterAppearance {
  gender: 'male' | 'female';
  skinColor: string;
  hairStyle: string;
  hairColor: string;
  eyeColor: string;
}

/** Stats du personnage */
export interface CharacterStats {
  strength: number;
  intelligence: number;
  agility: number;
  vitality: number;
  luck: number;
}

/** Personnage HabitQuest complet */
export interface HabitQuestCharacter {
  id: string;
  userId: string;
  name: string;
  characterClass: CharacterClass;
  title?: string;
  level: number;
  currentXp: number;
  xpToNextLevel: number;
  totalXp: number;
  hp: number;
  maxHp: number;
  coins: number;
  gems: number;
  appearance: CharacterAppearance;
  equipment: CharacterEquipment;
  stats: CharacterStats;
  unallocatedPoints: number;
  spriteSheetUrl?: string;
  createdAt: string;
  updatedAt: string;
}

/** Item de la boutique */
export interface ShopItem {
  id: string;
  name: string;
  description: string;
  slot: keyof CharacterEquipment;
  spriteLayer?: string;
  requiredLevel: number;
  cost: number;
  rarity: RarityTier;
  statBonus?: Partial<CharacterStats>;
}
