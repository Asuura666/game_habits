'use client';

import { useMemo, useState } from 'react';
import { cn } from '@/lib/utils';
import { useSpriteAnimation } from '@/hooks/useSpriteAnimation';
import {
  type CharacterClass,
  type SpriteAnimation,
  type SpriteDirection,
  CLASS_CONFIG,
  getTierByLevel,
  getArmorByLevel,
  LPC_FRAME_SIZE,
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
  /** Classe du personnage */
  characterClass?: CharacterClass | string;
  /** Genre (override le défaut de la classe) */
  gender?: 'male' | 'female';
  /** Niveau (affecte armure et ring de rareté) */
  level?: number;
  /** Taille du composant */
  size?: keyof typeof SIZES;
  /** Afficher le badge de niveau */
  showLevel?: boolean;
  /** Animation à jouer (idle, walk, slash, etc.) */
  animation?: SpriteAnimation;
  /** Direction du sprite */
  direction?: SpriteDirection;
  /** URL du spritesheet complet (si fourni, ignore les layers) */
  spriteSheetUrl?: string;
  /** Activer les animations au hover */
  animated?: boolean;
  /** FPS de l'animation */
  fps?: number;
  /** Classes CSS additionnelles */
  className?: string;
  /** Callback quand l'animation se termine */
  onAnimationComplete?: () => void;
}

export function LPCCharacter({
  characterClass = 'warrior',
  gender,
  level = 1,
  size = 'lg',
  showLevel = false,
  animation = 'idle',
  direction = 'down',
  spriteSheetUrl,
  animated = true,
  fps = 8,
  className,
  onAnimationComplete,
}: LPCCharacterProps) {
  const [isHovered, setIsHovered] = useState(false);
  
  const config = CLASS_CONFIG[characterClass as CharacterClass] || CLASS_CONFIG.warrior;
  const sizeConfig = SIZES[size];
  const tierConfig = getTierByLevel(level);
  
  const charGender = gender || config.defaultGender;
  const armorType = getArmorByLevel(level);
  
  // Si on a un spritesheet complet, utiliser l'animation Canvas
  const canvasRef = useSpriteAnimation({
    spriteSheetUrl: spriteSheetUrl || null,
    animation: isHovered && animated ? 'walk' : animation,
    direction,
    scale: sizeConfig.scale,
    fps,
    paused: !spriteSheetUrl,
    onAnimationComplete,
  });

  // Sprite layer style (pour l'approche layers)
  const spriteStyle = useMemo(() => ({
    width: LPC_FRAME_SIZE,
    height: LPC_FRAME_SIZE,
    backgroundSize: `${13 * LPC_FRAME_SIZE}px auto`,
    backgroundPosition: `0 -${2 * LPC_FRAME_SIZE}px`, // Idle = walk row, frame 0
    imageRendering: 'pixelated' as const,
  }), []);

  // Récupérer les URLs des sprites
  const bodySprite = SPRITES.body[charGender];
  const hairSprite = charGender === 'female' && config.defaultHair === 'ponytail' 
    ? SPRITES.hair.ponytail 
    : SPRITES.hair[charGender];
  const armorSprite = armorType !== 'none' && SPRITES.armor[armorType] 
    ? SPRITES.armor[armorType]![charGender] 
    : null;

  return (
    <div 
      className={cn('relative inline-flex flex-col items-center gap-2', className)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Character container avec ring de rareté */}
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
        {spriteSheetUrl ? (
          // Mode Canvas (spritesheet complet avec animation)
          <canvas
            ref={canvasRef}
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
            style={{ imageRendering: 'pixelated' }}
          />
        ) : (
          // Mode Layers (body + armor + hair superposés)
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
        )}

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
