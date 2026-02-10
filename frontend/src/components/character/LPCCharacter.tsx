'use client';

import { useMemo } from 'react';
import { cn } from '@/lib/utils';

// LPC Spritesheet configuration
// Standard LPC sprites are 64x64 per frame
const FRAME_SIZE = 64;
const IDLE_ROW = 2; // Row 2 is usually front-facing idle

// Sprite paths
const SPRITES = {
  body: {
    male: '/sprites/body/male.png',
    female: '/sprites/body/female.png',
  },
  hair: {
    male: '/sprites/hair/bangslong_male.png',
    female: '/sprites/hair/bangslong_female.png',
    ponytail: '/sprites/hair/ponytail_female.png',
  },
  armor: {
    none: null,
    robe: { male: '/sprites/armor/robe_male.png', female: '/sprites/armor/robe_female.png' },
    leather: { male: '/sprites/armor/leather_male.png', female: '/sprites/armor/leather_female.png' },
    plate: { male: '/sprites/armor/plate_male.png', female: '/sprites/armor/plate_female.png' },
  },
};

// Class configurations
const CLASS_CONFIG: Record<string, {
  defaultGender: 'male' | 'female';
  defaultArmor: 'none' | 'robe' | 'leather' | 'plate';
  defaultHair: string;
  ringColor: string;
}> = {
  warrior: { defaultGender: 'male', defaultArmor: 'plate', defaultHair: 'male', ringColor: 'ring-red-500' },
  mage: { defaultGender: 'female', defaultArmor: 'robe', defaultHair: 'ponytail', ringColor: 'ring-purple-500' },
  ranger: { defaultGender: 'male', defaultArmor: 'leather', defaultHair: 'male', ringColor: 'ring-green-500' },
  paladin: { defaultGender: 'male', defaultArmor: 'plate', defaultHair: 'male', ringColor: 'ring-yellow-500' },
  assassin: { defaultGender: 'female', defaultArmor: 'leather', defaultHair: 'female', ringColor: 'ring-pink-500' },
};

// Equipment tier based on level
const getArmorTier = (level: number): 'none' | 'robe' | 'leather' | 'plate' => {
  if (level >= 15) return 'plate';
  if (level >= 8) return 'leather';
  if (level >= 3) return 'robe';
  return 'none';
};

const getTierRing = (level: number) => {
  if (level >= 20) return { ring: 'ring-yellow-400', glow: 'shadow-yellow-500/50', name: 'Légendaire' };
  if (level >= 15) return { ring: 'ring-purple-400', glow: 'shadow-purple-500/50', name: 'Épique' };
  if (level >= 10) return { ring: 'ring-blue-400', glow: 'shadow-blue-500/50', name: 'Rare' };
  if (level >= 5) return { ring: 'ring-green-400', glow: 'shadow-green-500/50', name: 'Peu commun' };
  return { ring: 'ring-gray-400', glow: '', name: 'Commun' };
};

interface LPCCharacterProps {
  characterClass?: string;
  gender?: 'male' | 'female';
  level?: number;
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  showLevel?: boolean;
  animated?: boolean;
  className?: string;
}

const SIZES = {
  sm: { container: 48, scale: 0.75 },
  md: { container: 64, scale: 1 },
  lg: { container: 96, scale: 1.5 },
  xl: { container: 128, scale: 2 },
  '2xl': { container: 160, scale: 2.5 },
};

export function LPCCharacter({
  characterClass = 'warrior',
  gender,
  level = 1,
  size = 'lg',
  showLevel = false,
  animated = true,
  className,
}: LPCCharacterProps) {
  const config = CLASS_CONFIG[characterClass] || CLASS_CONFIG.warrior;
  const sizeConfig = SIZES[size];
  const tierConfig = getTierRing(level);
  
  // Determine character properties
  const charGender = gender || config.defaultGender;
  const armorType = getArmorTier(level);
  
  // Get sprite URLs
  const bodySprite = SPRITES.body[charGender];
  const hairSprite = charGender === 'female' && config.defaultHair === 'ponytail' 
    ? SPRITES.hair.ponytail 
    : SPRITES.hair[charGender];
  const armorSprite = armorType !== 'none' && SPRITES.armor[armorType] 
    ? SPRITES.armor[armorType][charGender] 
    : null;

  // Sprite layer style - shows single frame from spritesheet
  const spriteStyle = useMemo(() => ({
    width: FRAME_SIZE,
    height: FRAME_SIZE,
    backgroundSize: `${13 * FRAME_SIZE}px auto`, // 13 columns in LPC sheet
    backgroundPosition: `0 -${IDLE_ROW * FRAME_SIZE}px`, // Front-facing idle
    imageRendering: 'pixelated' as const,
  }), []);

  return (
    <div className={cn('relative inline-flex flex-col items-center gap-2', className)}>
      {/* Character container */}
      <div
        className={cn(
          'relative rounded-full overflow-hidden',
          'ring-4',
          tierConfig.ring,
          tierConfig.glow && `shadow-lg ${tierConfig.glow}`,
          'bg-gray-800',
          animated && 'transition-all duration-300 hover:scale-110',
        )}
        style={{
          width: sizeConfig.container,
          height: sizeConfig.container,
        }}
      >
        {/* Sprite layers container */}
        <div 
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
          style={{
            width: FRAME_SIZE * sizeConfig.scale,
            height: FRAME_SIZE * sizeConfig.scale,
          }}
        >
          {/* Body layer */}
          <div
            className="absolute inset-0 bg-no-repeat"
            style={{
              ...spriteStyle,
              backgroundImage: `url(${bodySprite})`,
              transform: `scale(${sizeConfig.scale})`,
              transformOrigin: 'top left',
            }}
          />
          
          {/* Armor layer */}
          {armorSprite && (
            <div
              className="absolute inset-0 bg-no-repeat"
              style={{
                ...spriteStyle,
                backgroundImage: `url(${armorSprite})`,
                transform: `scale(${sizeConfig.scale})`,
                transformOrigin: 'top left',
              }}
            />
          )}
          
          {/* Hair layer */}
          <div
            className="absolute inset-0 bg-no-repeat"
            style={{
              ...spriteStyle,
              backgroundImage: `url(${hairSprite})`,
              transform: `scale(${sizeConfig.scale})`,
              transformOrigin: 'top left',
            }}
          />
        </div>

        {/* Shine effect */}
        {animated && (
          <div className="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/20 to-white/0 opacity-0 hover:opacity-100 transition-opacity" />
        )}
      </div>

      {/* Level badge */}
      {showLevel && (
        <div className={cn(
          'absolute -bottom-1 -right-1',
          'bg-gray-900 border-2',
          tierConfig.ring.replace('ring-', 'border-'),
          'rounded-full px-2 py-0.5',
          'text-xs font-bold text-white',
        )}>
          {level}
        </div>
      )}
    </div>
  );
}

// Export types for customization
export type { LPCCharacterProps };
