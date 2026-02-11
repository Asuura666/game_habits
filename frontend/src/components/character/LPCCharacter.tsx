'use client';

import { useEffect, useRef, useState } from 'react';
import { cn } from '@/lib/utils';
import {
  type CharacterClass,
  type SpriteAnimation,
  type SpriteDirection,
  CLASS_CONFIG,
  getTierByLevel,
  getArmorByLevel,
  LPC_FRAME_SIZE,
  LPC_ANIMATIONS,
  LPC_DIRECTION_OFFSET,
} from '@/types/character';

// Sprite paths (layers)
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

const SIZES = {
  sm: { container: 48, scale: 0.75 },
  md: { container: 64, scale: 1 },
  lg: { container: 96, scale: 1.5 },
  xl: { container: 128, scale: 2 },
  '2xl': { container: 192, scale: 3 },
};

interface LPCCharacterProps {
  /** URL du spritesheet complet (ignoré pour l'instant, prêt pour future extension) */
  spriteSheetUrl?: string;
  characterClass?: CharacterClass | string;
  gender?: 'male' | 'female';
  level?: number;
  size?: keyof typeof SIZES;
  showLevel?: boolean;
  animation?: SpriteAnimation;
  direction?: SpriteDirection;
  animated?: boolean;
  fps?: number;
  className?: string;
}

export function LPCCharacter({
  characterClass = 'warrior',
  gender,
  level = 1,
  size = 'lg',
  showLevel = false,
  animation = 'idle',
  direction = 'down',
  animated = true,
  spriteSheetUrl,
  fps = 8,
  className,
}: LPCCharacterProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [frame, setFrame] = useState(0);
  const animationRef = useRef<number | null>(null);
  const lastFrameTime = useRef(0);
  
  const config = CLASS_CONFIG[characterClass as CharacterClass] || CLASS_CONFIG.warrior;
  const sizeConfig = SIZES[size];
  const tierConfig = getTierByLevel(level);
  
  const charGender = gender || config.defaultGender;
  const armorType = getArmorByLevel(level);
  
  // Current animation state
  const currentAnim = isHovered && animated ? 'walk' : animation;
  const animConfig = LPC_ANIMATIONS[currentAnim];
  const dirOffset = currentAnim === 'hurt' ? 0 : LPC_DIRECTION_OFFSET[direction];
  const row = animConfig.startRow + dirOffset;

  // Animation loop
  useEffect(() => {
    if (!animated) return;
    
    const frameInterval = 1000 / fps;
    
    const animate = (timestamp: number) => {
      if (timestamp - lastFrameTime.current >= frameInterval) {
        lastFrameTime.current = timestamp;
        setFrame(f => (f + 1) % animConfig.frames);
      }
      animationRef.current = requestAnimationFrame(animate);
    };
    
    animationRef.current = requestAnimationFrame(animate);
    
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [animated, fps, animConfig.frames, currentAnim]);

  // Reset frame when animation changes
  useEffect(() => {
    setFrame(0);
  }, [currentAnim]);

  // Get sprite URLs
  const bodySprite = SPRITES.body[charGender];
  const hairSprite = charGender === 'female' && config.defaultHair === 'ponytail' 
    ? SPRITES.hair.ponytail 
    : SPRITES.hair[charGender];
  const armorSprite = armorType !== 'none' && SPRITES.armor[armorType] 
    ? SPRITES.armor[armorType]![charGender] 
    : null;

  // Calculate sprite position
  const spriteX = frame * LPC_FRAME_SIZE;
  const spriteY = row * LPC_FRAME_SIZE;

  const layerStyle = {
    width: LPC_FRAME_SIZE,
    height: LPC_FRAME_SIZE,
    backgroundSize: `${13 * LPC_FRAME_SIZE}px auto`,
    backgroundPosition: `-${spriteX}px -${spriteY}px`,
    imageRendering: 'pixelated' as const,
    transform: `scale(${sizeConfig.scale})`,
    transformOrigin: 'top left',
  };

  return (
    <div 
      className={cn('relative inline-flex flex-col items-center gap-2', className)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Character container with rarity ring */}
      <div
        className={cn(
          'relative rounded-full overflow-hidden',
          'ring-4',
          tierConfig.ring,
          tierConfig.glow && `shadow-lg ${tierConfig.glow}`,
          'bg-gradient-to-br from-gray-700 to-gray-900',
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
            width: LPC_FRAME_SIZE * sizeConfig.scale,
            height: LPC_FRAME_SIZE * sizeConfig.scale,
          }}
        >
          {/* Body layer */}
          <div
            className="absolute inset-0 bg-no-repeat"
            style={{
              ...layerStyle,
              backgroundImage: `url(${bodySprite})`,
            }}
          />
          
          {/* Armor layer */}
          {armorSprite && (
            <div
              className="absolute inset-0 bg-no-repeat"
              style={{
                ...layerStyle,
                backgroundImage: `url(${armorSprite})`,
              }}
            />
          )}
          
          {/* Hair layer */}
          <div
            className="absolute inset-0 bg-no-repeat"
            style={{
              ...layerStyle,
              backgroundImage: `url(${hairSprite})`,
            }}
          />
        </div>

        {/* Shine effect on hover */}
        {animated && (
          <div className="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/20 to-white/0 opacity-0 hover:opacity-100 transition-opacity duration-300" />
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
          'shadow-lg',
        )}>
          {level}
        </div>
      )}
    </div>
  );
}

export type { LPCCharacterProps };
