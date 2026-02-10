'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Medal, Flame, TrendingUp, Crown, Calendar, Target, Loader2 } from 'lucide-react';
import { Card, Badge } from '@/components/ui';
import { SpriteAvatar } from '@/components/character';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  username: string;
  avatar_url: string | null;
  character_name: string | null;
  character_class: string | null;
  level: number;
  score: number;
  metric_value: number;
  metric_label: string;
  is_current_user: boolean;
  is_friend: boolean;
}

interface LeaderboardResponse {
  leaderboard_type: string;
  time_range: string;
  entries: LeaderboardEntry[];
  user_rank: number | null;
  total_participants: number;
  updated_at: string;
}

type LeaderboardType = 'xp_weekly' | 'xp_monthly' | 'streak' | 'completion';

const LEADERBOARD_CONFIG = {
  xp_weekly: { label: 'XP Semaine', icon: TrendingUp, endpoint: '/leaderboard/xp/weekly' },
  xp_monthly: { label: 'XP Mois', icon: Calendar, endpoint: '/leaderboard/xp/monthly' },
  streak: { label: 'Série', icon: Flame, endpoint: '/leaderboard/streak' },
  completion: { label: 'Complétion', icon: Target, endpoint: '/leaderboard/completion' },
};

const getRankIcon = (rank: number) => {
  switch (rank) {
    case 1:
      return <Crown className="w-6 h-6 text-yellow-500" />;
    case 2:
      return <Medal className="w-6 h-6 text-gray-400" />;
    case 3:
      return <Medal className="w-6 h-6 text-amber-600" />;
    default:
      return <span className="text-lg font-bold text-gray-500">#{rank}</span>;
  }
};

export default function LeaderboardPage() {
  const { user, accessToken } = useAuthStore();
  const [type, setType] = useState<LeaderboardType>('xp_weekly');
  const [leaderboard, setLeaderboard] = useState<LeaderboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  useEffect(() => {
    const fetchLeaderboard = async () => {
      if (!accessToken) return;
      setIsLoading(true);
      setError('');

      try {
        const config = LEADERBOARD_CONFIG[type];
        const res = await fetch(`${API_URL}${config.endpoint}`, {
          headers: { Authorization: `Bearer ${accessToken}` }
        });

        if (res.ok) {
          const data = await res.json();
          setLeaderboard(data);
        } else {
          setError('Impossible de charger le classement');
        }
      } catch (err) {
        setError('Erreur de connexion');
      } finally {
        setIsLoading(false);
      }
    };

    fetchLeaderboard();
  }, [accessToken, type, API_URL]);

  const entries = leaderboard?.entries || [];
  const userRank = leaderboard?.user_rank;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center justify-center gap-3">
          <Trophy className="w-8 h-8 text-yellow-500" />
          Classement Amis
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          {leaderboard ? `${leaderboard.total_participants} participants` : 'Compare-toi avec tes amis'}
        </p>
      </div>

      {/* Type Toggle */}
      <div className="flex flex-wrap justify-center gap-2">
        {(Object.entries(LEADERBOARD_CONFIG) as [LeaderboardType, typeof LEADERBOARD_CONFIG.xp_weekly][]).map(([key, config]) => {
          const Icon = config.icon;
          return (
            <button
              key={key}
              onClick={() => setType(key)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all text-sm',
                type === key
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              )}
            >
              <Icon className="w-4 h-4" />
              {config.label}
            </button>
          );
        })}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        </div>
      ) : error ? (
        <Card variant="bordered" padding="lg" className="text-center">
          <p className="text-gray-500">{error}</p>
          <p className="text-sm text-gray-400 mt-2">Ajoute des amis pour voir le classement !</p>
        </Card>
      ) : entries.length === 0 ? (
        <Card variant="bordered" padding="lg" className="text-center">
          <Trophy className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">Pas encore de données</p>
          <p className="text-sm text-gray-400 mt-2">Complète des habitudes pour apparaître au classement !</p>
        </Card>
      ) : (
        <>
          {/* Top 3 Podium */}
          {entries.length >= 3 && (
            <div className="flex justify-center items-end gap-4 py-6">
              {/* 2nd Place */}
              <motion.div
                initial={{ y: 50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-center"
              >
                {entries[1]?.character_class ? (
                  <SpriteAvatar characterClass={entries[1].character_class} size="lg" className="mx-auto mb-2" />
                ) : (
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-gray-400 to-gray-500 flex items-center justify-center text-2xl font-bold text-white mx-auto mb-2">
                    {entries[1]?.username.charAt(0)}
                  </div>
                )}
                <Medal className="w-8 h-8 text-gray-400 mx-auto mb-1" />
                <p className="font-semibold text-gray-900 dark:text-white text-sm truncate max-w-[100px]">
                  {entries[1]?.character_name || entries[1]?.username}
                </p>
                <p className="text-xs text-gray-500">Niveau {entries[1]?.level}</p>
                <div className="h-20 w-24 bg-gray-400/30 rounded-t-lg mt-2 flex items-center justify-center">
                  <span className="text-2xl font-bold text-gray-400">2</span>
                </div>
              </motion.div>

              {/* 1st Place */}
              <motion.div
                initial={{ y: 50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="text-center"
              >
                {entries[0]?.character_class ? (
                  <SpriteAvatar characterClass={entries[0].character_class} size="xl" className="mx-auto mb-2 ring-4 ring-yellow-300 rounded-full" />
                ) : (
                  <div className="w-24 h-24 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-3xl font-bold text-white mx-auto mb-2 ring-4 ring-yellow-300">
                    {entries[0]?.username.charAt(0)}
                  </div>
                )}
                <Crown className="w-10 h-10 text-yellow-500 mx-auto mb-1" />
                <p className="font-bold text-gray-900 dark:text-white truncate max-w-[120px]">
                  {entries[0]?.character_name || entries[0]?.username}
                </p>
                <p className="text-sm text-gray-500">Niveau {entries[0]?.level}</p>
                <div className="h-28 w-28 bg-yellow-500/30 rounded-t-lg mt-2 flex items-center justify-center">
                  <span className="text-3xl font-bold text-yellow-500">1</span>
                </div>
              </motion.div>

              {/* 3rd Place */}
              <motion.div
                initial={{ y: 50, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="text-center"
              >
                {entries[2]?.character_class ? (
                  <SpriteAvatar characterClass={entries[2].character_class} size="lg" className="mx-auto mb-2" />
                ) : (
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center text-2xl font-bold text-white mx-auto mb-2">
                    {entries[2]?.username.charAt(0)}
                  </div>
                )}
                <Medal className="w-8 h-8 text-amber-600 mx-auto mb-1" />
                <p className="font-semibold text-gray-900 dark:text-white text-sm truncate max-w-[100px]">
                  {entries[2]?.character_name || entries[2]?.username}
                </p>
                <p className="text-xs text-gray-500">Niveau {entries[2]?.level}</p>
                <div className="h-16 w-24 bg-amber-600/30 rounded-t-lg mt-2 flex items-center justify-center">
                  <span className="text-2xl font-bold text-amber-600">3</span>
                </div>
              </motion.div>
            </div>
          )}

          {/* Leaderboard List */}
          <Card variant="bordered" padding="none" className="overflow-hidden">
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {entries.slice(3).map((entry, index) => (
                <motion.div
                  key={entry.user_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={cn(
                    'flex items-center gap-4 p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors',
                    entry.is_current_user && 'bg-primary-500/10'
                  )}
                >
                  <div className="w-10 flex justify-center">
                    {getRankIcon(entry.rank)}
                  </div>
                  
                  {entry.character_class ? (
                    <SpriteAvatar characterClass={entry.character_class} size="md" />
                  ) : (
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-lg font-bold text-white">
                      {entry.username.charAt(0)}
                    </div>
                  )}

                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-gray-900 dark:text-white truncate flex items-center gap-2">
                      {entry.character_name || entry.username}
                      {entry.is_current_user && <Badge size="sm" variant="info">Toi</Badge>}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Niveau {entry.level}
                    </p>
                  </div>

                  <div className="text-right">
                    <p className="font-bold text-game-xp">
                      {entry.score.toLocaleString()} {entry.metric_label}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </Card>

          {/* Current User Position (if not in top) */}
          {userRank && userRank > 10 && (
            <Card variant="bordered" padding="md" className="bg-primary-500/10 border-primary-500/30">
              <div className="flex items-center gap-4">
                <div className="w-10 flex justify-center">
                  <span className="text-lg font-bold text-primary-500">#{userRank}</span>
                </div>
                
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-lg font-bold text-white">
                  {user?.username.charAt(0).toUpperCase()}
                </div>

                <div className="flex-1">
                  <p className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    {user?.username}
                    <Badge size="sm" variant="info">Toi</Badge>
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Niveau {user?.level}
                  </p>
                </div>
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
