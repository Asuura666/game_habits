'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Medal, Flame, TrendingUp, Crown, Star } from 'lucide-react';
import { Card, Badge } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';
import type { LeaderboardEntry } from '@/types';

const mockLeaderboard: LeaderboardEntry[] = [
  { rank: 1, userId: '1', username: 'LegendaryHero', level: 42, xp: 125000, streak: 180 },
  { rank: 2, userId: '2', username: 'QuestMaster99', level: 38, xp: 98000, streak: 95 },
  { rank: 3, userId: '3', username: 'DragonKnight', level: 35, xp: 87000, streak: 60 },
  { rank: 4, userId: '4', username: 'ShadowWalker', level: 32, xp: 76000, streak: 45 },
  { rank: 5, userId: '5', username: 'PhoenixRider', level: 30, xp: 68000, streak: 30 },
  { rank: 6, userId: '6', username: 'StormBringer', level: 28, xp: 62000, streak: 28 },
  { rank: 7, userId: '7', username: 'MoonWarrior', level: 25, xp: 54000, streak: 21 },
  { rank: 8, userId: '8', username: 'SunChaser', level: 23, xp: 48000, streak: 18 },
  { rank: 9, userId: '9', username: 'StarGazer', level: 20, xp: 42000, streak: 14 },
  { rank: 10, userId: '10', username: 'NightHunter', level: 18, xp: 36000, streak: 10 },
];

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

const getRankStyle = (rank: number) => {
  switch (rank) {
    case 1:
      return 'bg-gradient-to-r from-yellow-500/20 to-orange-500/20 border-yellow-500/50';
    case 2:
      return 'bg-gradient-to-r from-gray-400/20 to-gray-300/20 border-gray-400/50';
    case 3:
      return 'bg-gradient-to-r from-amber-600/20 to-orange-600/20 border-amber-600/50';
    default:
      return '';
  }
};

type LeaderboardType = 'xp' | 'streak';

export default function LeaderboardPage() {
  const { user } = useAuthStore();
  const [type, setType] = useState<LeaderboardType>('xp');

  const sortedLeaderboard = [...mockLeaderboard].sort((a, b) => {
    if (type === 'xp') return b.xp - a.xp;
    return b.streak - a.streak;
  }).map((entry, index) => ({ ...entry, rank: index + 1 }));

  // Find current user's rank (mock)
  const userRank = 15;

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center justify-center gap-3">
          <Trophy className="w-8 h-8 text-yellow-500" />
          Classement
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Les meilleurs aventuriers de HabitQuest
        </p>
      </div>

      {/* Type Toggle */}
      <div className="flex justify-center gap-2">
        <button
          onClick={() => setType('xp')}
          className={cn(
            'flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all',
            type === 'xp'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
          )}
        >
          <TrendingUp className="w-5 h-5" />
          Par XP
        </button>
        <button
          onClick={() => setType('streak')}
          className={cn(
            'flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all',
            type === 'streak'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
          )}
        >
          <Flame className="w-5 h-5" />
          Par Série
        </button>
      </div>

      {/* Top 3 Podium */}
      <div className="flex justify-center items-end gap-4 py-6">
        {/* 2nd Place */}
        <motion.div
          initial={{ y: 50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-center"
        >
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-gray-400 to-gray-500 flex items-center justify-center text-2xl font-bold text-white mx-auto mb-2">
            {sortedLeaderboard[1]?.username.charAt(0)}
          </div>
          <Medal className="w-8 h-8 text-gray-400 mx-auto mb-1" />
          <p className="font-semibold text-gray-900 dark:text-white text-sm truncate max-w-[100px]">
            {sortedLeaderboard[1]?.username}
          </p>
          <p className="text-xs text-gray-500">Niveau {sortedLeaderboard[1]?.level}</p>
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
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center text-3xl font-bold text-white mx-auto mb-2 ring-4 ring-yellow-300">
            {sortedLeaderboard[0]?.username.charAt(0)}
          </div>
          <Crown className="w-10 h-10 text-yellow-500 mx-auto mb-1" />
          <p className="font-bold text-gray-900 dark:text-white truncate max-w-[120px]">
            {sortedLeaderboard[0]?.username}
          </p>
          <p className="text-sm text-gray-500">Niveau {sortedLeaderboard[0]?.level}</p>
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
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center text-2xl font-bold text-white mx-auto mb-2">
            {sortedLeaderboard[2]?.username.charAt(0)}
          </div>
          <Medal className="w-8 h-8 text-amber-600 mx-auto mb-1" />
          <p className="font-semibold text-gray-900 dark:text-white text-sm truncate max-w-[100px]">
            {sortedLeaderboard[2]?.username}
          </p>
          <p className="text-xs text-gray-500">Niveau {sortedLeaderboard[2]?.level}</p>
          <div className="h-16 w-24 bg-amber-600/30 rounded-t-lg mt-2 flex items-center justify-center">
            <span className="text-2xl font-bold text-amber-600">3</span>
          </div>
        </motion.div>
      </div>

      {/* Leaderboard List */}
      <Card variant="bordered" padding="none" className="overflow-hidden">
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {sortedLeaderboard.slice(3).map((entry, index) => (
            <motion.div
              key={entry.userId}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="flex items-center gap-4 p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <div className="w-10 flex justify-center">
                {getRankIcon(entry.rank)}
              </div>
              
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-lg font-bold text-white">
                {entry.username.charAt(0)}
              </div>

              <div className="flex-1 min-w-0">
                <p className="font-semibold text-gray-900 dark:text-white truncate">
                  {entry.username}
                </p>
                <div className="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
                  <span>Niveau {entry.level}</span>
                  <span className="flex items-center gap-1">
                    <Flame className="w-4 h-4 text-orange-500" />
                    {entry.streak} jours
                  </span>
                </div>
              </div>

              <div className="text-right">
                <p className="font-bold text-game-xp">
                  {type === 'xp' ? `${(entry.xp / 1000).toFixed(1)}K XP` : `${entry.streak} jours`}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </Card>

      {/* Current User Position */}
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
              <Badge size="sm" variant="info">Vous</Badge>
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Niveau {user?.level} • {user?.streak} jours de série
            </p>
          </div>

          <div className="text-right">
            <p className="font-bold text-game-xp">{user?.xp} XP</p>
          </div>
        </div>
      </Card>
    </div>
  );
}
