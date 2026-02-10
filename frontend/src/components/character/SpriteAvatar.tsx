'use client';

import { useMemo } from 'react';
import { cn } from '@/lib/utils';

// Sprite configuration types
export interface SpriteConfig {
  bodyType: 'male' | 'female';
  skinTone: number; // 0-5
  hairStyle: number; // 0-7
  hairColor: number; // 0-5
  outfit: number; // 0-3 (based on class)
}

// Default sprite configurations for each class
export const CLASS_SPRITES: Record<string, SpriteConfig> = {
  warrior: { bodyType: 'male', skinTone: 2, hairStyle: 1, hairColor: 3, outfit: 0 },
  mage: { bodyType: 'female', skinTone: 1, hairStyle: 4, hairColor: 1, outfit: 1 },
  ranger: { bodyType: 'male', skinTone: 3, hairStyle: 2, hairColor: 2, outfit: 2 },
  paladin: { bodyType: 'male', skinTone: 0, hairStyle: 0, hairColor: 4, outfit: 3 },
  assassin: { bodyType: 'female', skinTone: 4, hairStyle: 6, hairColor: 0, outfit: 0 },
};

// Color palettes
const SKIN_TONES = [
  '#FFDFC4', // Light
  '#F0C8A8', // Fair
  '#D4A574', // Medium
  '#A67C52', // Tan
  '#8B5A2B', // Brown
  '#5C3A21', // Dark
];

const HAIR_COLORS = [
  '#1a1a1a', // Black
  '#8B4513', // Brown
  '#DAA520', // Blonde
  '#B22222', // Red
  '#808080', // Gray
  '#4169E1', // Blue (fantasy)
];

const CLASS_COLORS: Record<string, string> = {
  warrior: '#DC2626', // Red
  mage: '#7C3AED', // Purple
  ranger: '#059669', // Green
  paladin: '#F59E0B', // Gold
  assassin: '#6366F1', // Indigo
};

interface SpriteAvatarProps {
  config?: Partial<SpriteConfig>;
  characterClass?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  animated?: boolean;
}

export function SpriteAvatar({
  config,
  characterClass = 'warrior',
  size = 'md',
  className,
  animated = false,
}: SpriteAvatarProps) {
  // Merge with class defaults
  const spriteConfig = useMemo(() => {
    const classDefault = CLASS_SPRITES[characterClass] || CLASS_SPRITES.warrior;
    return { ...classDefault, ...config };
  }, [config, characterClass]);

  const skinColor = SKIN_TONES[spriteConfig.skinTone] || SKIN_TONES[2];
  const hairColor = HAIR_COLORS[spriteConfig.hairColor] || HAIR_COLORS[0];
  const classColor = CLASS_COLORS[characterClass] || CLASS_COLORS.warrior;

  const sizes = {
    sm: 'w-12 h-12',
    md: 'w-16 h-16',
    lg: 'w-24 h-24',
    xl: 'w-32 h-32',
  };

  const innerSizes = {
    sm: 'w-8 h-8',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
    xl: 'w-24 h-24',
  };

  return (
    <div
      className={cn(
        'relative rounded-full flex items-center justify-center overflow-hidden',
        sizes[size],
        animated && 'animate-bounce-slow',
        className
      )}
      style={{
        background: `linear-gradient(135deg, ${classColor}40, ${classColor}20)`,
        border: `3px solid ${classColor}`,
      }}
    >
      {/* Body/Head */}
      <svg
        viewBox="0 0 64 64"
        className={innerSizes[size]}
        style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))' }}
      >
        {/* Face */}
        <ellipse cx="32" cy="28" rx="14" ry="16" fill={skinColor} />
        
        {/* Hair based on style */}
        <HairStyle style={spriteConfig.hairStyle} color={hairColor} />
        
        {/* Eyes */}
        <circle cx="27" cy="26" r="2" fill="#1a1a1a" />
        <circle cx="37" cy="26" r="2" fill="#1a1a1a" />
        <circle cx="27.5" cy="25.5" r="0.7" fill="white" />
        <circle cx="37.5" cy="25.5" r="0.7" fill="white" />
        
        {/* Mouth */}
        <path
          d="M 28 34 Q 32 37 36 34"
          stroke="#1a1a1a"
          strokeWidth="1.5"
          fill="none"
          strokeLinecap="round"
        />
        
        {/* Body/Armor hint */}
        <path
          d="M 20 48 Q 32 44 44 48 L 44 64 L 20 64 Z"
          fill={classColor}
        />
        <path
          d="M 24 48 Q 32 46 40 48 L 40 56 L 24 56 Z"
          fill={`${classColor}CC`}
        />
      </svg>
      
      {/* Class icon overlay */}
      <div
        className="absolute bottom-0 right-0 w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold"
        style={{ backgroundColor: classColor }}
      >
        {characterClass.charAt(0).toUpperCase()}
      </div>
    </div>
  );
}

// Hair styles as SVG paths
function HairStyle({ style, color }: { style: number; color: string }) {
  const hairStyles = [
    // 0: Short/Bald
    null,
    // 1: Short spiky
    <path key="1" d="M 18 22 Q 20 8 32 10 Q 44 8 46 22 Q 44 16 32 18 Q 20 16 18 22" fill={color} />,
    // 2: Medium
    <path key="2" d="M 16 28 Q 14 12 32 10 Q 50 12 48 28 Q 46 20 32 22 Q 18 20 16 28" fill={color} />,
    // 3: Long
    <>
      <path key="3a" d="M 14 28 Q 12 8 32 6 Q 52 8 50 28 Q 48 16 32 18 Q 16 16 14 28" fill={color} />
      <path key="3b" d="M 14 28 Q 12 40 18 52 L 22 48 Q 18 36 18 28" fill={color} />
      <path key="3c" d="M 50 28 Q 52 40 46 52 L 42 48 Q 46 36 46 28" fill={color} />
    </>,
    // 4: Ponytail
    <>
      <path key="4a" d="M 16 24 Q 16 10 32 8 Q 48 10 48 24 Q 44 16 32 18 Q 20 16 16 24" fill={color} />
      <ellipse key="4b" cx="50" cy="32" rx="6" ry="12" fill={color} />
    </>,
    // 5: Mohawk
    <path key="5" d="M 28 6 Q 32 2 36 6 L 36 22 Q 32 24 28 22 Z" fill={color} />,
    // 6: Pigtails
    <>
      <path key="6a" d="M 18 20 Q 18 10 32 10 Q 46 10 46 20 Q 42 14 32 16 Q 22 14 18 20" fill={color} />
      <ellipse key="6b" cx="14" cy="30" rx="5" ry="8" fill={color} />
      <ellipse key="6c" cx="50" cy="30" rx="5" ry="8" fill={color} />
    </>,
    // 7: Curly
    <>
      <circle key="7a" cx="20" cy="16" r="6" fill={color} />
      <circle key="7b" cx="32" cy="12" r="7" fill={color} />
      <circle key="7c" cx="44" cy="16" r="6" fill={color} />
      <circle key="7d" cx="16" cy="26" r="5" fill={color} />
      <circle key="7e" cx="48" cy="26" r="5" fill={color} />
    </>,
  ];

  return hairStyles[style] || null;
}

// Predefined avatar options for selection
export const AVATAR_PRESETS = [
  { id: 'warrior_m1', class: 'warrior', config: { bodyType: 'male' as const, skinTone: 2, hairStyle: 1, hairColor: 3, outfit: 0 } },
  { id: 'warrior_f1', class: 'warrior', config: { bodyType: 'female' as const, skinTone: 1, hairStyle: 3, hairColor: 1, outfit: 0 } },
  { id: 'mage_m1', class: 'mage', config: { bodyType: 'male' as const, skinTone: 0, hairStyle: 7, hairColor: 4, outfit: 1 } },
  { id: 'mage_f1', class: 'mage', config: { bodyType: 'female' as const, skinTone: 3, hairStyle: 4, hairColor: 1, outfit: 1 } },
  { id: 'ranger_m1', class: 'ranger', config: { bodyType: 'male' as const, skinTone: 3, hairStyle: 2, hairColor: 2, outfit: 2 } },
  { id: 'ranger_f1', class: 'ranger', config: { bodyType: 'female' as const, skinTone: 2, hairStyle: 6, hairColor: 0, outfit: 2 } },
  { id: 'paladin_m1', class: 'paladin', config: { bodyType: 'male' as const, skinTone: 1, hairStyle: 0, hairColor: 4, outfit: 3 } },
  { id: 'paladin_f1', class: 'paladin', config: { bodyType: 'female' as const, skinTone: 0, hairStyle: 3, hairColor: 3, outfit: 3 } },
  { id: 'assassin_m1', class: 'assassin', config: { bodyType: 'male' as const, skinTone: 4, hairStyle: 5, hairColor: 0, outfit: 0 } },
  { id: 'assassin_f1', class: 'assassin', config: { bodyType: 'female' as const, skinTone: 2, hairStyle: 4, hairColor: 5, outfit: 0 } },
];

// Get presets for a specific class
export function getPresetsForClass(characterClass: string) {
  return AVATAR_PRESETS.filter(p => p.class === characterClass);
}
