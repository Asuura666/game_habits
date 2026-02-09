'use client';

import { motion } from 'framer-motion';
import { Shield, Sword, Zap, Heart, Star, Award, Crown, Sparkles } from 'lucide-react';
import { Card, ProgressBar, Badge } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import { cn, getRarityColor } from '@/lib/utils';
import type { Character, Equipment, CharacterClass } from '@/types';

const mockCharacter: Character = {
  id: '1',
  userId: '1',
  name: 'Aventurier',
  class: 'warrior',
  level: 5,
  strength: 15,
  intelligence: 8,
  agility: 12,
  vitality: 18,
  equipment: [
    {
      id: '1',
      name: 'Épée du Débutant',
      type: 'weapon',
      rarity: 'uncommon',
      stats: { attack: 5, critChance: 2 },
    },
    {
      id: '2',
      name: 'Armure en Cuir',
      type: 'armor',
      rarity: 'common',
      stats: { defense: 3, hp: 10 },
    },
    {
      id: '3',
      name: 'Amulette de Focus',
      type: 'accessory',
      rarity: 'rare',
      stats: { xpBonus: 5, manaRegen: 2 },
    },
  ],
};

const classInfo: Record<CharacterClass, { name: string; icon: typeof Sword; color: string }> = {
  warrior: { name: 'Guerrier', icon: Sword, color: 'text-red-500' },
  mage: { name: 'Mage', icon: Zap, color: 'text-blue-500' },
  rogue: { name: 'Voleur', icon: Star, color: 'text-purple-500' },
  healer: { name: 'Soigneur', icon: Heart, color: 'text-green-500' },
};

const statIcons = {
  strength: Sword,
  intelligence: Zap,
  agility: Star,
  vitality: Heart,
};

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export default function CharacterPage() {
  const { user } = useAuthStore();
  const character = mockCharacter;
  const ClassIcon = classInfo[character.class].icon;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-6xl mx-auto space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Mon Personnage</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Gérez votre personnage et son équipement
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Character Card */}
        <motion.div variants={itemVariants} className="lg:col-span-1">
          <Card variant="bordered" padding="lg" className="text-center">
            {/* Avatar */}
            <div className="relative inline-block mb-4">
              <div className="w-32 h-32 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-5xl font-bold text-white mx-auto">
                {user?.username.charAt(0).toUpperCase()}
              </div>
              <div className="absolute -bottom-2 left-1/2 -translate-x-1/2">
                <Badge variant="info" className="gap-1">
                  <Crown className="w-3 h-3" />
                  Niveau {user?.level}
                </Badge>
              </div>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {user?.username}
            </h2>
            
            <div className={cn('flex items-center justify-center gap-2 mb-6', classInfo[character.class].color)}>
              <ClassIcon className="w-5 h-5" />
              <span className="font-medium">{classInfo[character.class].name}</span>
            </div>

            {/* XP Progress */}
            <div className="mb-6">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-500 dark:text-gray-400">Expérience</span>
                <span className="text-game-xp font-medium">{user?.xp} / {user?.xpToNextLevel}</span>
              </div>
              <ProgressBar value={user?.xp || 0} max={user?.xpToNextLevel || 100} variant="xp" />
            </div>

            {/* HP & Mana */}
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-game-hp">Points de vie</span>
                  <span>{user?.hp} / {user?.maxHp}</span>
                </div>
                <ProgressBar value={user?.hp || 0} max={user?.maxHp || 100} variant="hp" />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-game-mana">Mana</span>
                  <span>{user?.mana} / {user?.maxMana}</span>
                </div>
                <ProgressBar value={user?.mana || 0} max={user?.maxMana || 100} variant="mana" />
              </div>
            </div>

            {/* Gold & Streak */}
            <div className="flex items-center justify-center gap-6 mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <div className="text-center">
                <p className="text-2xl font-bold text-game-gold">🪙 {user?.gold}</p>
                <p className="text-xs text-gray-500">Or</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-orange-500">🔥 {user?.streak}</p>
                <p className="text-xs text-gray-500">Jours</p>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Stats & Equipment */}
        <div className="lg:col-span-2 space-y-6">
          {/* Stats */}
          <motion.div variants={itemVariants}>
            <Card variant="bordered" padding="lg">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Award className="w-5 h-5 text-primary-500" />
                Statistiques
              </h3>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {(Object.entries(character) as [string, number][])
                  .filter(([key]) => ['strength', 'intelligence', 'agility', 'vitality'].includes(key))
                  .map(([stat, value]) => {
                    const Icon = statIcons[stat as keyof typeof statIcons];
                    const labels: Record<string, string> = {
                      strength: 'Force',
                      intelligence: 'Intelligence',
                      agility: 'Agilité',
                      vitality: 'Vitalité',
                    };
                    const colors: Record<string, string> = {
                      strength: 'from-red-500 to-orange-500',
                      intelligence: 'from-blue-500 to-cyan-500',
                      agility: 'from-purple-500 to-pink-500',
                      vitality: 'from-green-500 to-emerald-500',
                    };

                    return (
                      <div
                        key={stat}
                        className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 text-center"
                      >
                        <div
                          className={cn(
                            'w-12 h-12 rounded-full mx-auto mb-2 flex items-center justify-center bg-gradient-to-br text-white',
                            colors[stat]
                          )}
                        >
                          <Icon className="w-6 h-6" />
                        </div>
                        <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">{labels[stat]}</p>
                      </div>
                    );
                  })}
              </div>
            </Card>
          </motion.div>

          {/* Equipment */}
          <motion.div variants={itemVariants}>
            <Card variant="bordered" padding="lg">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary-500" />
                Équipement
              </h3>
              
              <div className="space-y-3">
                {character.equipment.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl"
                  >
                    <div className="w-14 h-14 rounded-lg bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                      {item.type === 'weapon' && <Sword className="w-7 h-7 text-gray-500" />}
                      {item.type === 'armor' && <Shield className="w-7 h-7 text-gray-500" />}
                      {item.type === 'accessory' && <Sparkles className="w-7 h-7 text-gray-500" />}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h4 className={cn('font-semibold', getRarityColor(item.rarity))}>
                          {item.name}
                        </h4>
                        <Badge size="sm" variant={item.rarity === 'legendary' ? 'warning' : 'default'}>
                          {item.rarity}
                        </Badge>
                      </div>
                      <div className="flex gap-3 mt-1 text-sm text-gray-500 dark:text-gray-400">
                        {Object.entries(item.stats).map(([stat, value]) => (
                          <span key={stat}>+{value} {stat}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </motion.div>

          {/* Achievements Teaser */}
          <motion.div variants={itemVariants}>
            <Card variant="bordered" padding="lg" className="bg-gradient-to-r from-primary-500/10 to-accent-500/10">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <Star className="w-5 h-5 text-yellow-500" />
                    Succès débloqués
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400">12 / 50 succès</p>
                </div>
                <div className="flex -space-x-2">
                  {['🏆', '⭐', '🎯', '🔥'].map((emoji, i) => (
                    <div
                      key={i}
                      className="w-10 h-10 rounded-full bg-gray-800 border-2 border-gray-700 flex items-center justify-center text-lg"
                    >
                      {emoji}
                    </div>
                  ))}
                  <div className="w-10 h-10 rounded-full bg-gray-700 border-2 border-gray-600 flex items-center justify-center text-sm font-medium text-gray-300">
                    +8
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
