'use client';

import { cn } from '@/lib/utils';
import { Sword, Wand2, Target, Shield, Zap } from 'lucide-react';

// Class configurations
const CLASS_CONFIG: Record<string, {
  gradient: string;
  ringColor: string;
  icon: typeof Sword;
  emoji: string;
}> = {
  warrior: {
    gradient: 'from-red-600 to-orange-500',
    ringColor: 'ring-red-500/50',
    icon: Sword,
    emoji: '⚔️',
  },
  mage: {
    gradient: 'from-blue-600 to-purple-500',
    ringColor: 'ring-purple-500/50',
    icon: Wand2,
    emoji: '🔮',
  },
  ranger: {
    gradient: 'from-green-600 to-emerald-500',
    ringColor: 'ring-green-500/50',
    icon: Target,
    emoji: '🏹',
  },
  paladin: {
    gradient: 'from-yellow-500 to-amber-400',
    ringColor: 'ring-yellow-500/50',
    icon: Shield,
    emoji: '🛡️',
  },
  assassin: {
    gradient: 'from-purple-600 to-pink-500',
    ringColor: 'ring-pink-500/50',
    icon: Zap,
    emoji: '🗡️',
  },
};

// Equipment tier based on level
const getTierConfig = (level: number) => {
  if (level >= 20) return { name: 'legendary', ring: 'ring-yellow-400', glow: 'shadow-yellow-500/50' };
  if (level >= 15) return { name: 'epic', ring: 'ring-purple-400', glow: 'shadow-purple-500/50' };
  if (level >= 10) return { name: 'rare', ring: 'ring-blue-400', glow: 'shadow-blue-500/50' };
  if (level >= 5) return { name: 'uncommon', ring: 'ring-green-400', glow: 'shadow-green-500/50' };
  return { name: 'common', ring: 'ring-gray-400', glow: '' };
};

interface LPCCharacterProps {
  characterClass: string;
  level?: number;
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  showLevel?: boolean;
  showClass?: boolean;
  animated?: boolean;
  className?: string;
}

const SIZES = {
  sm: { container: 'w-12 h-12', icon: 'w-6 h-6', level: 'text-[10px] -bottom-1 -right-1 px-1.5' },
  md: { container: 'w-16 h-16', icon: 'w-8 h-8', level: 'text-xs -bottom-1 -right-1 px-2' },
  lg: { container: 'w-24 h-24', icon: 'w-12 h-12', level: 'text-sm -bottom-2 -right-2 px-2.5 py-0.5' },
  xl: { container: 'w-32 h-32', icon: 'w-16 h-16', level: 'text-base -bottom-2 -right-2 px-3 py-1' },
  '2xl': { container: 'w-40 h-40', icon: 'w-20 h-20', level: 'text-lg -bottom-3 -right-3 px-4 py-1' },
};

export function LPCCharacter({
  characterClass = 'warrior',
  level = 1,
  size = 'lg',
  showLevel = false,
  showClass = false,
  animated = true,
  className,
}: LPCCharacterProps) {
  const config = CLASS_CONFIG[characterClass] || CLASS_CONFIG.warrior;
  const sizeConfig = SIZES[size];
  const tierConfig = getTierConfig(level);
  const Icon = config.icon;

  return (
    <div className={cn('relative inline-flex flex-col items-center gap-2', className)}>
      {/* Character avatar */}
      <div
        className={cn(
          sizeConfig.container,
          'relative rounded-full overflow-hidden',
          'bg-gradient-to-br',
          config.gradient,
          'ring-4',
          tierConfig.ring,
          tierConfig.glow && `shadow-lg ${tierConfig.glow}`,
          animated && 'transition-all duration-300 hover:scale-110 hover:shadow-xl',
        )}
      >
        {/* Inner circle with icon */}
        <div className="absolute inset-2 rounded-full bg-gray-900/40 flex items-center justify-center backdrop-blur-sm">
          <Icon className={cn(sizeConfig.icon, 'text-white drop-shadow-lg')} />
        </div>
        
        {/* Animated shine effect */}
        {animated && (
          <div className="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/30 to-white/0 -translate-x-full animate-shine" />
        )}
        
        {/* Sparkle particles for legendary */}
        {tierConfig.name === 'legendary' && (
          <>
            <div className="absolute top-1 left-1 w-1 h-1 bg-yellow-300 rounded-full animate-ping" />
            <div className="absolute top-2 right-2 w-1 h-1 bg-yellow-300 rounded-full animate-ping delay-300" />
            <div className="absolute bottom-2 left-2 w-1 h-1 bg-yellow-300 rounded-full animate-ping delay-500" />
          </>
        )}
      </div>

      {/* Level badge */}
      {showLevel && (
        <div className={cn(
          'absolute',
          sizeConfig.level,
          'bg-gray-900 border-2',
          tierConfig.ring.replace('ring-', 'border-'),
          'rounded-full font-bold text-white',
          'flex items-center justify-center',
        )}>
          {level}
        </div>
      )}
      
      {/* Class name */}
      {showClass && (
        <span className="text-sm font-medium text-gray-400 capitalize">
          {characterClass}
        </span>
      )}
    </div>
  );
}

// Add to globals.css:
// @keyframes shine {
//   to { transform: translateX(200%); }
// }
// .animate-shine {
//   animation: shine 2s ease-in-out infinite;
// }
