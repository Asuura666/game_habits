'use client';

import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, Target, CheckSquare, Flame, Trophy, Calendar, Sparkles } from 'lucide-react';
import { Card, ProgressBar, Badge } from '@/components/ui';
import { CalendarHeatmap } from '@/components/habits';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';
import type { UserStats, DailyStats } from '@/types';

const mockStats: UserStats = {
  totalHabitsCompleted: 156,
  totalTasksCompleted: 89,
  longestStreak: 15,
  currentStreak: 7,
  totalXpEarned: 4500,
  totalGoldEarned: 1250,
  dailyStats: [
    { date: '2024-01-01', habitsCompleted: 5, tasksCompleted: 3, xpEarned: 120, goldEarned: 45 },
    { date: '2024-01-02', habitsCompleted: 4, tasksCompleted: 2, xpEarned: 95, goldEarned: 35 },
    { date: '2024-01-03', habitsCompleted: 6, tasksCompleted: 4, xpEarned: 150, goldEarned: 55 },
    { date: '2024-01-04', habitsCompleted: 5, tasksCompleted: 1, xpEarned: 100, goldEarned: 40 },
    { date: '2024-01-05', habitsCompleted: 3, tasksCompleted: 5, xpEarned: 130, goldEarned: 50 },
    { date: '2024-01-06', habitsCompleted: 5, tasksCompleted: 2, xpEarned: 110, goldEarned: 42 },
    { date: '2024-01-07', habitsCompleted: 6, tasksCompleted: 3, xpEarned: 140, goldEarned: 52 },
  ],
};

const weekDays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];

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

export default function StatsPage() {
  const { user } = useAuthStore();
  const stats = mockStats;

  const maxHabits = Math.max(...stats.dailyStats.map((d) => d.habitsCompleted));
  const maxXp = Math.max(...stats.dailyStats.map((d) => d.xpEarned));

  const achievements = [
    { icon: '🔥', name: 'Première semaine', description: '7 jours consécutifs', unlocked: true },
    { icon: '⭐', name: '100 habitudes', description: 'Compléter 100 habitudes', unlocked: true },
    { icon: '🏆', name: 'Champion', description: 'Atteindre niveau 10', unlocked: false },
    { icon: '🐉', name: 'Tueur de dragons', description: 'Vaincre 10 boss', unlocked: false },
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-6xl mx-auto space-y-6"
    >
      {/* Header */}
      <motion.div variants={itemVariants}>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
          <BarChart3 className="w-8 h-8 text-primary-500" />
          Statistiques
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Suivez votre progression et vos accomplissements
        </p>
      </motion.div>

      {/* Summary Cards */}
      <motion.div variants={itemVariants} className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card variant="elevated" className="text-center bg-gradient-to-br from-green-500/10 to-emerald-500/10">
          <Target className="w-8 h-8 text-green-500 mx-auto mb-2" />
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.totalHabitsCompleted}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">Habitudes complétées</p>
        </Card>
        
        <Card variant="elevated" className="text-center bg-gradient-to-br from-blue-500/10 to-cyan-500/10">
          <CheckSquare className="w-8 h-8 text-blue-500 mx-auto mb-2" />
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.totalTasksCompleted}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">Tâches terminées</p>
        </Card>
        
        <Card variant="elevated" className="text-center bg-gradient-to-br from-orange-500/10 to-red-500/10">
          <Flame className="w-8 h-8 text-orange-500 mx-auto mb-2" />
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.longestStreak}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">Record de série</p>
        </Card>
        
        <Card variant="elevated" className="text-center bg-gradient-to-br from-purple-500/10 to-pink-500/10">
          <Sparkles className="w-8 h-8 text-purple-500 mx-auto mb-2" />
          <p className="text-3xl font-bold text-game-xp">{stats.totalXpEarned}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">XP total gagné</p>
        </Card>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Activity Chart */}
        <motion.div variants={itemVariants}>
          <Card variant="bordered" padding="lg">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-primary-500" />
              Activité de la semaine
            </h3>
            
            <div className="space-y-4">
              {/* Habits Chart */}
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Habitudes complétées</p>
                <div className="flex items-end gap-2 h-24">
                  {stats.dailyStats.map((day, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center">
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: `${(day.habitsCompleted / maxHabits) * 100}%` }}
                        transition={{ delay: index * 0.1, duration: 0.5 }}
                        className="w-full bg-gradient-to-t from-green-500 to-emerald-400 rounded-t"
                        style={{ minHeight: '8px' }}
                      />
                      <span className="text-xs text-gray-500 mt-2">{weekDays[index]}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* XP Chart */}
              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">XP gagné</p>
                <div className="flex items-end gap-2 h-24">
                  {stats.dailyStats.map((day, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center">
                      <motion.div
                        initial={{ height: 0 }}
                        animate={{ height: `${(day.xpEarned / maxXp) * 100}%` }}
                        transition={{ delay: index * 0.1 + 0.3, duration: 0.5 }}
                        className="w-full bg-gradient-to-t from-primary-500 to-accent-400 rounded-t"
                        style={{ minHeight: '8px' }}
                      />
                      <span className="text-xs text-gray-500 mt-2">{day.xpEarned}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Progress Overview */}
        <motion.div variants={itemVariants}>
          <Card variant="bordered" padding="lg">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-primary-500" />
              Progression
            </h3>
            
            <div className="space-y-6">
              {/* Level Progress */}
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-gray-600 dark:text-gray-400">Niveau {user?.level}</span>
                  <span className="text-game-xp font-medium">{user?.xp} / {user?.xpToNextLevel} XP</span>
                </div>
                <ProgressBar value={user?.xp || 0} max={user?.xpToNextLevel || 100} variant="xp" />
              </div>

              {/* Current Streak */}
              <div className="p-4 rounded-xl bg-orange-500/10">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-orange-500/20 flex items-center justify-center">
                      <Flame className="w-6 h-6 text-orange-500" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">Série actuelle</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">Continue comme ça !</p>
                    </div>
                  </div>
                  <p className="text-3xl font-bold text-orange-500">{stats.currentStreak}</p>
                </div>
              </div>

              {/* Gold Earned */}
              <div className="flex items-center justify-between p-4 rounded-xl bg-yellow-500/10">
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">Or total gagné</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Depuis le début</p>
                </div>
                <p className="text-2xl font-bold text-game-gold">🪙 {stats.totalGoldEarned}</p>
              </div>
            </div>
          </Card>
        </motion.div>
      </div>

      {/* Achievements */}
      {/* Calendar Heatmap */}
      <motion.div variants={itemVariants}>
        <CalendarHeatmap />
      </motion.div>

      <motion.div variants={itemVariants}>
        <Card variant="bordered" padding="lg">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
            <Trophy className="w-5 h-5 text-yellow-500" />
            Succès
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {achievements.map((achievement, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className={cn(
                  'p-4 rounded-xl text-center transition-all',
                  achievement.unlocked
                    ? 'bg-yellow-500/10 border border-yellow-500/30'
                    : 'bg-gray-100 dark:bg-gray-800/50 opacity-50'
                )}
              >
                <div className="text-3xl mb-2">{achievement.icon}</div>
                <p className="font-medium text-gray-900 dark:text-white text-sm">
                  {achievement.name}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {achievement.description}
                </p>
                {achievement.unlocked && (
                  <Badge size="sm" variant="success" className="mt-2">
                    Débloqué
                  </Badge>
                )}
              </motion.div>
            ))}
          </div>
        </Card>
      </motion.div>
    </motion.div>
  );
}
