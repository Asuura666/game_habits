'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Sword, Zap, Heart, Star, Award, Crown, Sparkles, Target, Loader2 } from 'lucide-react';
import { Card, ProgressBar, Badge } from '@/components/ui';
import { SpriteAvatar, AVATAR_PRESETS } from '@/components/character';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';

interface CharacterStats {
  strength: number;
  intelligence: number;
  agility: number;
  vitality: number;
  luck: number;
}

interface CharacterData {
  id: string;
  user_id: string;
  name: string;
  character_class: string;
  title: string | null;
  avatar_id: string;
  level: number;
  current_xp: number;
  xp_to_next_level: number;
  total_xp: number;
  hp: number;
  max_hp: number;
  stats: CharacterStats;
  unallocated_points: number;
  coins: number;
  gems: number;
  created_at: string;
  updated_at: string;
}

const classInfo: Record<string, { name: string; icon: typeof Sword; color: string; bgColor: string }> = {
  warrior: { name: 'Guerrier', icon: Sword, color: 'text-red-500', bgColor: 'from-red-500 to-orange-500' },
  mage: { name: 'Mage', icon: Zap, color: 'text-blue-500', bgColor: 'from-blue-500 to-purple-500' },
  ranger: { name: 'Rôdeur', icon: Target, color: 'text-green-500', bgColor: 'from-green-500 to-emerald-500' },
  paladin: { name: 'Paladin', icon: Shield, color: 'text-yellow-500', bgColor: 'from-yellow-500 to-amber-500' },
  assassin: { name: 'Assassin', icon: Sparkles, color: 'text-purple-500', bgColor: 'from-purple-500 to-pink-500' },
  rogue: { name: 'Voleur', icon: Star, color: 'text-purple-500', bgColor: 'from-purple-500 to-pink-500' },
  healer: { name: 'Soigneur', icon: Heart, color: 'text-green-500', bgColor: 'from-green-500 to-teal-500' },
};

const statConfig = {
  strength: { label: 'Force', icon: Sword, color: 'from-red-500 to-orange-500' },
  intelligence: { label: 'Intelligence', icon: Zap, color: 'from-blue-500 to-cyan-500' },
  agility: { label: 'Agilité', icon: Target, color: 'from-purple-500 to-pink-500' },
  vitality: { label: 'Vitalité', icon: Heart, color: 'from-green-500 to-emerald-500' },
  luck: { label: 'Chance', icon: Star, color: 'from-yellow-500 to-amber-500' },
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
  const { user, accessToken } = useAuthStore();
  const [character, setCharacter] = useState<CharacterData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCharacter = async () => {
      if (!accessToken) return;

      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/characters/me`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch character');
        }

        const data = await response.json();
        setCharacter(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCharacter();
  }, [accessToken]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-primary-500 mx-auto mb-4" />
          <p className="text-gray-400">Chargement du personnage...</p>
        </div>
      </div>
    );
  }

  if (error || !character) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <p className="text-red-400 mb-4">{error || 'Personnage non trouvé'}</p>
        </div>
      </div>
    );
  }

  const classData = classInfo[character.character_class] || classInfo.warrior;
  const ClassIcon = classData.icon;

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
              <SpriteAvatar
                characterClass={character.character_class}
                size="xl"
                className="mx-auto"
              />
              <div className="absolute -bottom-2 left-1/2 -translate-x-1/2">
                <Badge variant="info" className="gap-1">
                  <Crown className="w-3 h-3" />
                  Niveau {character.level}
                </Badge>
              </div>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
              {character.name}
            </h2>
            
            {character.title && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-2 italic">
                "{character.title}"
              </p>
            )}
            
            <div className={cn('flex items-center justify-center gap-2 mb-6', classData.color)}>
              <ClassIcon className="w-5 h-5" />
              <span className="font-medium">{classData.name}</span>
            </div>

            {/* XP Progress */}
            <div className="mb-6">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-500 dark:text-gray-400">Expérience</span>
                <span className="text-game-xp font-medium">
                  {character.current_xp} / {character.xp_to_next_level}
                </span>
              </div>
              <ProgressBar 
                value={character.current_xp} 
                max={character.xp_to_next_level} 
                variant="xp" 
              />
            </div>

            {/* HP */}
            <div className="mb-6">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-game-hp">Points de vie</span>
                <span>{character.hp} / {character.max_hp}</span>
              </div>
              <ProgressBar value={character.hp} max={character.max_hp} variant="hp" />
            </div>

            {/* Gold & Points */}
            <div className="flex items-center justify-center gap-6 pt-6 border-t border-gray-200 dark:border-gray-700">
              <div className="text-center">
                <p className="text-2xl font-bold text-game-gold">🪙 {character.coins}</p>
                <p className="text-xs text-gray-500">Or</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-500">💎 {character.gems}</p>
                <p className="text-xs text-gray-500">Gemmes</p>
              </div>
              {character.unallocated_points > 0 && (
                <div className="text-center">
                  <p className="text-2xl font-bold text-primary-500">⬆️ {character.unallocated_points}</p>
                  <p className="text-xs text-gray-500">Points</p>
                </div>
              )}
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
                {character.unallocated_points > 0 && (
                  <Badge variant="warning" className="ml-2">
                    {character.unallocated_points} points à distribuer
                  </Badge>
                )}
              </h3>
              
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {(Object.entries(character.stats) as [keyof CharacterStats, number][]).map(([stat, value]) => {
                  const config = statConfig[stat];
                  if (!config) return null;
                  const Icon = config.icon;

                  return (
                    <div
                      key={stat}
                      className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 text-center"
                    >
                      <div
                        className={cn(
                          'w-12 h-12 rounded-full mx-auto mb-2 flex items-center justify-center bg-gradient-to-br text-white',
                          config.color
                        )}
                      >
                        <Icon className="w-6 h-6" />
                      </div>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{config.label}</p>
                    </div>
                  );
                })}
              </div>
            </Card>
          </motion.div>

          {/* Total XP Card */}
          <motion.div variants={itemVariants}>
            <Card variant="bordered" padding="lg">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Star className="w-5 h-5 text-yellow-500" />
                Progression totale
              </h3>
              
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                  <p className="text-3xl font-bold text-primary-500">{character.total_xp.toLocaleString()}</p>
                  <p className="text-sm text-gray-500">XP Total</p>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                  <p className="text-3xl font-bold text-game-gold">{character.level}</p>
                  <p className="text-sm text-gray-500">Niveau</p>
                </div>
                <div className="text-center p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
                  <p className="text-3xl font-bold text-green-500">{user?.streak || 0}</p>
                  <p className="text-sm text-gray-500">🔥 Streak</p>
                </div>
              </div>
            </Card>
          </motion.div>

          {/* Class Bonus Info */}
          <motion.div variants={itemVariants}>
            <Card variant="bordered" padding="lg" className="bg-gradient-to-r from-primary-500/10 to-accent-500/10">
              <div className="flex items-center gap-4">
                <div className={cn(
                  'w-16 h-16 rounded-xl bg-gradient-to-br flex items-center justify-center',
                  classData.bgColor
                )}>
                  <ClassIcon className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Bonus de classe : {classData.name}
                  </h3>
                  <p className="text-gray-500 dark:text-gray-400">
                    {character.character_class === 'warrior' && '+20% XP des tâches, bonus de force'}
                    {character.character_class === 'mage' && '+20% pièces d\'or, bonus d\'intelligence'}
                    {character.character_class === 'ranger' && '+20% XP des habitudes, bonus d\'agilité'}
                    {character.character_class === 'paladin' && '+10% tout XP, stats équilibrées'}
                    {character.character_class === 'assassin' && '+30% bonus de streak, bonus de chance'}
                  </p>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
}
