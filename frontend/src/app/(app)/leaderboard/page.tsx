'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Trophy, Medal, Crown, Flame, Sparkles, TrendingUp } from 'lucide-react';
import { Card, Badge } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';

const leaderboardData = {
  xp: [
    { rank: 1, username: 'Dragon_Master', level: 45, xp: 125000, streak: 180, avatarEmoji: '🐉' },
    { rank: 2, username: 'ZenWarrior', level: 42, xp: 118500, streak: 150, avatarEmoji: '🧘' },
    { rank: 3, username: 'IronWill', level: 40, xp: 112000, streak: 200, avatarEmoji: '💪' },
    { rank: 4, username: 'StarChaser', level: 38, xp: 98000, streak: 90, avatarEmoji: '⭐' },
    { rank: 5, username: 'MindfulMage', level: 35, xp: 89000, streak: 75, avatarEmoji: '🔮' },
    { rank: 6, username: 'FocusKing', level: 32, xp: 78000, streak: 60, avatarEmoji: '👑' },
    { rank: 7, username: 'HabitHero', level: 30, xp: 72000, streak: 45, avatarEmoji: '🦸' },
    { rank: 8, username: 'DailyGrinder', level: 28, xp: 65000, streak: 120, avatarEmoji: '⚡' },
    { rank: 9, username: 'Persistor', level: 25, xp: 58000, streak: 30, avatarEmoji: '🎯' },
    { rank: 10, username: 'RisingStar', level: 22, xp: 50000, streak: 25, avatarEmoji: '🌟' },
  ],
  streak: [
    { rank: 1, username: 'IronWill', level: 40, xp: 112000, streak: 200, avatarEmoji: '💪' },
    { rank: 2, username: 'Dragon_Master', level: 45, xp: 125000, streak: 180, avatarEmoji: '🐉' },
    { rank: 3, username: 'ZenWarrior', level: 42, xp: 118500, streak: 150, avatarEmoji: '🧘' },
    { rank: 4, username: 'DailyGrinder', level: 28, xp: 65000, streak: 120, avatarEmoji: '⚡' },
    { rank: 5, username: 'StarChaser', level: 38, xp: 98000, streak: 90, avatarEmoji: '⭐' },
    { rank: 6, username: 'MindfulMage', level: 35, xp: 89000, streak: 75, avatarEmoji: '🔮' },
    { rank: 7, username: 'FocusKing', level: 32, xp: 78000, streak: 60, avatarEmoji: '👑' },
    { rank: 8, username: 'HabitHero', level: 30, xp: 72000, streak: 45, avatarEmoji: '🦸' },
    { rank: 9, username: 'Persistor', level: 25, xp: 58000, streak: 30, avatarEmoji: '🎯' },
    { rank: 10, username: 'RisingStar', level: 22, xp: 50000, streak: 25, avatarEmoji: '🌟' },
  ],
};

const rankStyles: Record<number, { bg: string; border: string; icon: typeof Trophy }> = {
  1: { bg: 'bg-yellow-50 dark:bg-yellow-900/20', border: 'border-yellow-400', icon: Crown },
  2: { bg: 'bg-gray-50 dark:bg-gray-800/50', border: 'border-gray-400', icon: Medal },
  3: { bg: 'bg-orange-50 dark:bg-orange-900/20', border: 'border-orange-400', icon: Medal },
};

export default function LeaderboardPage() {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState<'xp' | 'streak'>('xp');

  const data = leaderboardData[activeTab];

  // Mock user rank
  const userRank = { rank: 42, xp: 450, streak: 7 };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-yellow-100 dark:bg-yellow-900/30 mb-4"
        >
          <Trophy className="w-8 h-8 text-yellow-500" />
        </motion.div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Classement</h1>
        <p className="text-gray-500 dark:text-gray-400 mt-2">
          Les meilleurs aventuriers de HabitQuest
        </p>
      </div>

      {/* Your Rank */}
      <Card variant="elevated" className="bg-gradient-to-r from-primary-600 to-accent-600 text-white">
        <div className="p-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-full bg-white/20 flex items-center justify-center text-2xl font-bold">
              #{userRank.rank}
            </div>
            <div>
              <p className="font-bold text-lg">{user?.username}</p>
              <p className="text-white/80 text-sm">Votre classement actuel</p>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold">{user?.level}</p>
                <p className="text-xs text-white/80">Niveau</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{user?.xp}</p>
                <p className="text-xs text-white/80">XP</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{user?.streak}</p>
                <p className="text-xs text-white/80">Streak</p>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Tabs */}
      <div className="flex gap-2 justify-center">
        <button
          onClick={() => setActiveTab('xp')}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
            activeTab === 'xp'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
          }`}
        >
          <Sparkles className="w-5 h-5" />
          Par XP
        </button>
        <button
          onClick={() => setActiveTab('streak')}
          className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
            activeTab === 'streak'
              ? 'bg-orange-500 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
          }`}
        >
          <Flame className="w-5 h-5" />
          Par Streak
        </button>
      </div>

      {/* Top 3 Podium */}
      <div className="flex items-end justify-center gap-4 py-8">
        {/* 2nd Place */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="text-center"
        >
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center text-3xl mx-auto mb-2">
            {data[1].avatarEmoji}
          </div>
          <p className="font-bold text-gray-900 dark:text-white">{data[1].username}</p>
          <p className="text-sm text-gray-500">Niv. {data[1].level}</p>
          <div className="mt-2 w-20 h-24 bg-gray-200 dark:bg-gray-700 rounded-t-lg flex items-center justify-center">
            <span className="text-4xl font-bold text-gray-400">2</span>
          </div>
        </motion.div>

        {/* 1st Place */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-center"
        >
          <Crown className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
          <div className="w-24 h-24 rounded-full bg-gradient-to-br from-yellow-400 to-yellow-500 flex items-center justify-center text-4xl mx-auto mb-2 ring-4 ring-yellow-300">
            {data[0].avatarEmoji}
          </div>
          <p className="font-bold text-gray-900 dark:text-white text-lg">{data[0].username}</p>
          <p className="text-sm text-gray-500">Niv. {data[0].level}</p>
          <div className="mt-2 w-24 h-32 bg-yellow-400 rounded-t-lg flex items-center justify-center">
            <span className="text-5xl font-bold text-yellow-700">1</span>
          </div>
        </motion.div>

        {/* 3rd Place */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-center"
        >
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-orange-300 to-orange-400 flex items-center justify-center text-3xl mx-auto mb-2">
            {data[2].avatarEmoji}
          </div>
          <p className="font-bold text-gray-900 dark:text-white">{data[2].username}</p>
          <p className="text-sm text-gray-500">Niv. {data[2].level}</p>
          <div className="mt-2 w-20 h-20 bg-orange-300 rounded-t-lg flex items-center justify-center">
            <span className="text-4xl font-bold text-orange-600">3</span>
          </div>
        </motion.div>
      </div>

      {/* Full Leaderboard */}
      <Card variant="bordered" padding="none">
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {data.slice(3).map((entry, index) => (
            <motion.div
              key={entry.username}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 * index }}
              className="flex items-center gap-4 p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <span className="w-8 text-center font-bold text-gray-500 dark:text-gray-400">
                {entry.rank}
              </span>
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-xl">
                {entry.avatarEmoji}
              </div>
              <div className="flex-1">
                <p className="font-bold text-gray-900 dark:text-white">{entry.username}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Niveau {entry.level}</p>
              </div>
              <div className="text-right">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1">
                    <Sparkles className="w-4 h-4 text-game-xp" />
                    <span className="font-medium text-gray-900 dark:text-white">
                      {entry.xp.toLocaleString()}
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Flame className="w-4 h-4 text-orange-500" />
                    <span className="font-medium text-gray-900 dark:text-white">{entry.streak}</span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </Card>
    </div>
  );
}
