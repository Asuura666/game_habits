'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trophy, Flame, TrendingUp, Star, Users, Globe, Loader2, Crown } from 'lucide-react';
import { Card, Badge } from '@/components/ui';
import { SpriteAvatar } from '@/components/character';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';

// Types
interface LeaderboardEntry {
  rank: number;
  user_id: string;
  username: string;
  character_name: string | null;
  character_class: string | null;
  level: number;
  value: number;
  is_current_user: boolean;
}

interface LeaderboardResponse {
  entries: LeaderboardEntry[];
  total_participants: number;
}

interface MyPosition {
  rank: number;
  value: number;
  type: string;
}

type LeaderboardType = 'xp' | 'streak' | 'level';
type LeaderboardScope = 'global' | 'friends';

// Config
const TYPE_CONFIG: Record<LeaderboardType, { label: string; icon: typeof TrendingUp; unit: string }> = {
  xp: { label: 'XP Total', icon: TrendingUp, unit: 'XP' },
  streak: { label: 'Streak', icon: Flame, unit: 'jours' },
  level: { label: 'Niveau', icon: Star, unit: '' },
};

// Medal colors
const MEDAL_COLORS = {
  gold: '#FFD700',
  silver: '#C0C0C0',
  bronze: '#CD7F32',
};

// Avatar color generator based on username
const getAvatarColor = (username: string): string => {
  const colors = [
    'from-red-400 to-red-600',
    'from-blue-400 to-blue-600',
    'from-green-400 to-green-600',
    'from-purple-400 to-purple-600',
    'from-orange-400 to-orange-600',
    'from-pink-400 to-pink-600',
    'from-cyan-400 to-cyan-600',
    'from-indigo-400 to-indigo-600',
  ];
  const index = username.charCodeAt(0) % colors.length;
  return colors[index];
};

// Medal component for top 3
const MedalIcon = ({ rank }: { rank: number }) => {
  const config = {
    1: { color: MEDAL_COLORS.gold, icon: Crown, size: 'w-8 h-8' },
    2: { color: MEDAL_COLORS.silver, icon: Trophy, size: 'w-7 h-7' },
    3: { color: MEDAL_COLORS.bronze, icon: Trophy, size: 'w-6 h-6' },
  }[rank];

  if (!config) return null;

  const Icon = config.icon;
  return (
    <div className="relative">
      <Icon className={config.size} style={{ color: config.color }} />
      <span 
        className="absolute -bottom-1 -right-1 text-xs font-bold rounded-full w-4 h-4 flex items-center justify-center"
        style={{ backgroundColor: config.color, color: rank === 1 ? '#000' : '#fff' }}
      >
        {rank}
      </span>
    </div>
  );
};

// Avatar component with initials
const PlayerAvatar = ({ 
  username, 
  characterClass, 
  size = 'md',
  isTop3 = false,
  rank = 0
}: { 
  username: string; 
  characterClass: string | null; 
  size?: 'sm' | 'md' | 'lg';
  isTop3?: boolean;
  rank?: number;
}) => {
  const sizeClasses = {
    sm: 'w-10 h-10 text-sm',
    md: 'w-12 h-12 text-lg',
    lg: 'w-16 h-16 text-2xl',
  };

  const ringClasses: Record<number, string> = {
    1: 'ring-4 ring-yellow-400',
    2: 'ring-4 ring-gray-400',
    3: 'ring-4 ring-amber-600',
  };

  const ringClass = isTop3 && rank >= 1 && rank <= 3 ? ringClasses[rank] : '';

  if (characterClass) {
    return (
      <SpriteAvatar 
        characterClass={characterClass} 
        size={size} 
        className={ringClass}
      />
    );
  }

  return (
    <div 
      className={cn(
        'rounded-full bg-gradient-to-br flex items-center justify-center font-bold text-white',
        sizeClasses[size],
        getAvatarColor(username),
        ringClass
      )}
    >
      {username.charAt(0).toUpperCase()}
    </div>
  );
};

export default function LeaderboardPage() {
  const { user, accessToken } = useAuthStore();
  const [type, setType] = useState<LeaderboardType>('xp');
  const [scope, setScope] = useState<LeaderboardScope>('global');
  const [leaderboard, setLeaderboard] = useState<LeaderboardResponse | null>(null);
  const [myPosition, setMyPosition] = useState<MyPosition | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  const fetchLeaderboard = useCallback(async () => {
    if (!accessToken) return;
    setIsLoading(true);
    setError('');

    try {
      // Fetch leaderboard
      const leaderboardRes = await fetch(
        `${API_URL}/leaderboard?type=${type}&scope=${scope}`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );

      if (!leaderboardRes.ok) {
        throw new Error('Impossible de charger le classement');
      }

      const leaderboardData = await leaderboardRes.json();
      setLeaderboard(leaderboardData);

      // Fetch my position
      const myPosRes = await fetch(
        `${API_URL}/leaderboard/me?type=${type}&scope=${scope}`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );

      if (myPosRes.ok) {
        const myPosData = await myPosRes.json();
        setMyPosition(myPosData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de connexion');
    } finally {
      setIsLoading(false);
    }
  }, [accessToken, type, scope, API_URL]);

  useEffect(() => {
    fetchLeaderboard();
  }, [fetchLeaderboard]);

  const entries = leaderboard?.entries || [];
  const top3 = entries.slice(0, 3);
  const restEntries = entries.slice(3);
  const currentUserInTop = entries.some(e => e.is_current_user);
  const showMyPosition = myPosition && !currentUserInTop && myPosition.rank > 10;

  const typeConfig = TYPE_CONFIG[type];
  const TypeIcon = typeConfig.icon;

  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-20">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center justify-center gap-3">
          <Trophy className="w-8 h-8 text-yellow-500" />
          Classement
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          {leaderboard ? `${leaderboard.total_participants} participants` : 'Compare-toi aux autres'}
        </p>
      </div>

      {/* Scope Toggle (Global vs Friends) */}
      <div className="flex justify-center">
        <div className="inline-flex rounded-xl bg-gray-100 dark:bg-gray-800 p-1">
          <button
            onClick={() => setScope('global')}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all text-sm',
              scope === 'global'
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            )}
          >
            <Globe className="w-4 h-4" />
            Global
          </button>
          <button
            onClick={() => setScope('friends')}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all text-sm',
              scope === 'friends'
                ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            )}
          >
            <Users className="w-4 h-4" />
            Amis
          </button>
        </div>
      </div>

      {/* Type Tabs */}
      <div className="flex flex-wrap justify-center gap-2">
        {(Object.entries(TYPE_CONFIG) as [LeaderboardType, typeof TYPE_CONFIG.xp][]).map(([key, config]) => {
          const Icon = config.icon;
          return (
            <button
              key={key}
              onClick={() => setType(key)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all text-sm',
                type === key
                  ? 'bg-primary-600 text-white shadow-lg shadow-primary-500/30'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              )}
            >
              <Icon className="w-4 h-4" />
              {config.label}
            </button>
          );
        })}
      </div>

      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center justify-center py-20"
          >
            <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
          </motion.div>
        ) : error ? (
          <motion.div
            key="error"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <Card variant="bordered" padding="lg" className="text-center">
              <p className="text-gray-500">{error}</p>
            </Card>
          </motion.div>
        ) : entries.length === 0 ? (
          <motion.div
            key="empty"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <Card variant="bordered" padding="lg" className="text-center">
              <Trophy className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500 font-medium">
                {scope === 'friends' ? 'Aucun ami dans le classement' : 'Pas encore de données'}
              </p>
              <p className="text-sm text-gray-400 mt-2">
                {scope === 'friends' 
                  ? 'Ajoute des amis pour voir le classement !' 
                  : 'Complète des habitudes pour apparaître au classement !'}
              </p>
            </Card>
          </motion.div>
        ) : (
          <motion.div
            key={`${type}-${scope}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {/* Top 3 Podium */}
            {top3.length >= 3 && (
              <div className="flex justify-center items-end gap-3 md:gap-6 py-6">
                {/* 2nd Place */}
                <motion.div
                  initial={{ y: 50, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="text-center flex-1 max-w-[120px]"
                >
                  <PlayerAvatar 
                    username={top3[1].username}
                    characterClass={top3[1].character_class}
                    size="lg"
                    isTop3
                    rank={2}
                  />
                  <MedalIcon rank={2} />
                  <p className="font-semibold text-gray-900 dark:text-white text-sm truncate mt-2">
                    {top3[1].character_name || top3[1].username}
                  </p>
                  {top3[1].is_current_user && (
                    <Badge size="sm" variant="info" className="mt-1">Toi</Badge>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    {top3[1].value.toLocaleString()} {typeConfig.unit}
                  </p>
                  <div 
                    className="h-16 md:h-20 w-full rounded-t-lg mt-2 flex items-center justify-center"
                    style={{ backgroundColor: `${MEDAL_COLORS.silver}30` }}
                  >
                    <span className="text-2xl font-bold" style={{ color: MEDAL_COLORS.silver }}>2</span>
                  </div>
                </motion.div>

                {/* 1st Place */}
                <motion.div
                  initial={{ y: 50, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.1 }}
                  className="text-center flex-1 max-w-[140px]"
                >
                  <div className="relative">
                    <PlayerAvatar 
                      username={top3[0].username}
                      characterClass={top3[0].character_class}
                      size="lg"
                      isTop3
                      rank={1}
                    />
                    <motion.div
                      animate={{ rotate: [0, -10, 10, -10, 0] }}
                      transition={{ repeat: Infinity, duration: 2, repeatDelay: 3 }}
                      className="absolute -top-2 -right-2"
                    >
                      <Crown className="w-8 h-8" style={{ color: MEDAL_COLORS.gold }} />
                    </motion.div>
                  </div>
                  <p className="font-bold text-gray-900 dark:text-white truncate mt-3">
                    {top3[0].character_name || top3[0].username}
                  </p>
                  {top3[0].is_current_user && (
                    <Badge size="sm" variant="info" className="mt-1">Toi</Badge>
                  )}
                  <p className="text-sm font-semibold mt-1" style={{ color: MEDAL_COLORS.gold }}>
                    {top3[0].value.toLocaleString()} {typeConfig.unit}
                  </p>
                  <div 
                    className="h-24 md:h-28 w-full rounded-t-lg mt-2 flex items-center justify-center"
                    style={{ backgroundColor: `${MEDAL_COLORS.gold}30` }}
                  >
                    <span className="text-3xl font-bold" style={{ color: MEDAL_COLORS.gold }}>1</span>
                  </div>
                </motion.div>

                {/* 3rd Place */}
                <motion.div
                  initial={{ y: 50, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.3 }}
                  className="text-center flex-1 max-w-[120px]"
                >
                  <PlayerAvatar 
                    username={top3[2].username}
                    characterClass={top3[2].character_class}
                    size="lg"
                    isTop3
                    rank={3}
                  />
                  <MedalIcon rank={3} />
                  <p className="font-semibold text-gray-900 dark:text-white text-sm truncate mt-2">
                    {top3[2].character_name || top3[2].username}
                  </p>
                  {top3[2].is_current_user && (
                    <Badge size="sm" variant="info" className="mt-1">Toi</Badge>
                  )}
                  <p className="text-xs text-gray-500 mt-1">
                    {top3[2].value.toLocaleString()} {typeConfig.unit}
                  </p>
                  <div 
                    className="h-12 md:h-16 w-full rounded-t-lg mt-2 flex items-center justify-center"
                    style={{ backgroundColor: `${MEDAL_COLORS.bronze}30` }}
                  >
                    <span className="text-2xl font-bold" style={{ color: MEDAL_COLORS.bronze }}>3</span>
                  </div>
                </motion.div>
              </div>
            )}

            {/* Rest of Leaderboard List */}
            {restEntries.length > 0 && (
              <Card variant="bordered" padding="none" className="overflow-hidden">
                <div className="divide-y divide-gray-200 dark:divide-gray-700">
                  {restEntries.map((entry, index) => (
                    <motion.div
                      key={entry.user_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.03 }}
                      className={cn(
                        'flex items-center gap-3 md:gap-4 p-3 md:p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors',
                        entry.is_current_user && 'bg-primary-500/10'
                      )}
                    >
                      {/* Rank */}
                      <div className="w-8 md:w-10 flex justify-center shrink-0">
                        <span className="text-lg font-bold text-gray-500">#{entry.rank}</span>
                      </div>
                      
                      {/* Avatar */}
                      <PlayerAvatar 
                        username={entry.username}
                        characterClass={entry.character_class}
                        size="md"
                      />

                      {/* Name & Level */}
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-gray-900 dark:text-white truncate flex items-center gap-2">
                          {entry.character_name || entry.username}
                          {entry.is_current_user && <Badge size="sm" variant="info">Toi</Badge>}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          Niveau {entry.level}
                        </p>
                      </div>

                      {/* Value */}
                      <div className="text-right shrink-0">
                        <p className="font-bold text-primary-600 dark:text-primary-400">
                          {entry.value.toLocaleString()}
                        </p>
                        <p className="text-xs text-gray-500">{typeConfig.unit}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </Card>
            )}

            {/* Current User Position (if not in top 10) */}
            {showMyPosition && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <Card variant="bordered" padding="md" className="bg-primary-500/10 border-primary-500/30">
                  <div className="flex items-center gap-4">
                    <div className="w-10 flex justify-center">
                      <span className="text-lg font-bold text-primary-500">#{myPosition.rank}</span>
                    </div>
                    
                    <PlayerAvatar 
                      username={user?.username || ''}
                      characterClass={null}
                      size="md"
                    />

                    <div className="flex-1">
                      <p className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                        {user?.username}
                        <Badge size="sm" variant="info">Toi</Badge>
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Niveau {user?.level || 1}
                      </p>
                    </div>

                    <div className="text-right">
                      <p className="font-bold text-primary-600 dark:text-primary-400">
                        {myPosition.value.toLocaleString()}
                      </p>
                      <p className="text-xs text-gray-500">{typeConfig.unit}</p>
                    </div>
                  </div>
                </Card>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
