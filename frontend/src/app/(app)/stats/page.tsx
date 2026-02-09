'use client';

import { motion } from 'framer-motion';
import { BarChart3, TrendingUp, Target, Calendar, Flame, Trophy, Coins, Sparkles } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, ProgressBar, Badge } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';

const weeklyData = [
  { day: 'Lun', habits: 5, tasks: 2, xp: 85 },
  { day: 'Mar', habits: 4, tasks: 3, xp: 95 },
  { day: 'Mer', habits: 6, tasks: 1, xp: 75 },
  { day: 'Jeu', habits: 5, tasks: 4, xp: 120 },
  { day: 'Ven', habits: 3, tasks: 2, xp: 65 },
  { day: 'Sam', habits: 4, tasks: 0, xp: 50 },
  { day: 'Dim', habits: 2, tasks: 1, xp: 35 },
];

const monthlyStats = {
  totalHabits: 145,
  totalTasks: 42,
  totalXp: 3250,
  totalGold: 890,
  avgDaily: 4.8,
  bestDay: 'Jeudi',
  longestStreak: 14,
};

const habitBreakdown = [
  { name: 'Méditation', completions: 28, total: 30, color: 'bg-purple-500' },
  { name: 'Sport', completions: 22, total: 30, color: 'bg-green-500' },
  { name: 'Lecture', completions: 25, total: 30, color: 'bg-blue-500' },
  { name: 'Eau', completions: 30, total: 30, color: 'bg-cyan-500' },
  { name: 'Sommeil', completions: 20, total: 30, color: 'bg-indigo-500' },
];

export default function StatsPage() {
  const { user } = useAuthStore();
  const maxXp = Math.max(...weeklyData.map((d) => d.xp));

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
          <BarChart3 className="w-8 h-8 text-primary-500" />
          Statistiques
        </h1>
        <p className="text-gray-500 dark:text-gray-400">Analysez votre progression</p>
      </motion.div>

      {/* Summary Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-4"
      >
        <Card variant="bordered" className="text-center">
          <div className="p-4">
            <div className="w-12 h-12 rounded-xl bg-green-100 dark:bg-green-900/30 flex items-center justify-center mx-auto mb-3">
              <Target className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">{monthlyStats.totalHabits}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Habitudes ce mois</p>
          </div>
        </Card>

        <Card variant="bordered" className="text-center">
          <div className="p-4">
            <div className="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mx-auto mb-3">
              <Calendar className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">{monthlyStats.totalTasks}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Tâches complétées</p>
          </div>
        </Card>

        <Card variant="bordered" className="text-center">
          <div className="p-4">
            <div className="w-12 h-12 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center mx-auto mb-3">
              <Sparkles className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">{monthlyStats.totalXp}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">XP gagnés</p>
          </div>
        </Card>

        <Card variant="bordered" className="text-center">
          <div className="p-4">
            <div className="w-12 h-12 rounded-xl bg-yellow-100 dark:bg-yellow-900/30 flex items-center justify-center mx-auto mb-3">
              <Coins className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
            </div>
            <p className="text-3xl font-bold text-gray-900 dark:text-white">{monthlyStats.totalGold}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">Or accumulé</p>
          </div>
        </Card>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weekly Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="lg:col-span-2"
        >
          <Card variant="bordered" padding="lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-primary-500" />
                Activité de la semaine
              </CardTitle>
            </CardHeader>
            <CardContent>
              {/* Simple Bar Chart */}
              <div className="flex items-end justify-between h-48 gap-2">
                {weeklyData.map((day, index) => (
                  <div key={day.day} className="flex-1 flex flex-col items-center">
                    <motion.div
                      initial={{ height: 0 }}
                      animate={{ height: `${(day.xp / maxXp) * 100}%` }}
                      transition={{ delay: index * 0.1, duration: 0.5 }}
                      className="w-full bg-gradient-to-t from-primary-600 to-primary-400 rounded-t-lg relative group"
                    >
                      <div className="absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-gray-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                        {day.xp} XP
                      </div>
                    </motion.div>
                    <span className="text-sm text-gray-500 dark:text-gray-400 mt-2">{day.day}</span>
                  </div>
                ))}
              </div>

              {/* Legend */}
              <div className="flex items-center justify-center gap-6 mt-6 text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-primary-500" />
                  <span className="text-gray-500 dark:text-gray-400">XP gagné</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Quick Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card variant="bordered" padding="lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trophy className="w-5 h-5 text-yellow-500" />
                Records
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50">
                <div className="flex items-center gap-3">
                  <Flame className="w-5 h-5 text-orange-500" />
                  <span className="text-gray-600 dark:text-gray-400">Plus longue série</span>
                </div>
                <span className="font-bold text-gray-900 dark:text-white">{monthlyStats.longestStreak} jours</span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50">
                <div className="flex items-center gap-3">
                  <Target className="w-5 h-5 text-green-500" />
                  <span className="text-gray-600 dark:text-gray-400">Moyenne quotidienne</span>
                </div>
                <span className="font-bold text-gray-900 dark:text-white">{monthlyStats.avgDaily} habitudes</span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50">
                <div className="flex items-center gap-3">
                  <Calendar className="w-5 h-5 text-blue-500" />
                  <span className="text-gray-600 dark:text-gray-400">Meilleur jour</span>
                </div>
                <span className="font-bold text-gray-900 dark:text-white">{monthlyStats.bestDay}</span>
              </div>

              <div className="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50">
                <div className="flex items-center gap-3">
                  <TrendingUp className="w-5 h-5 text-purple-500" />
                  <span className="text-gray-600 dark:text-gray-400">Série actuelle</span>
                </div>
                <span className="font-bold text-orange-500">{user?.streak} jours 🔥</span>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Habit Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card variant="bordered" padding="lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-primary-500" />
              Détail par habitude (ce mois)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {habitBreakdown.map((habit, index) => {
                const percentage = Math.round((habit.completions / habit.total) * 100);
                return (
                  <motion.div
                    key={habit.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900 dark:text-white">{habit.name}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          {habit.completions}/{habit.total}
                        </span>
                        <Badge variant={percentage === 100 ? 'success' : percentage >= 80 ? 'info' : 'default'} size="sm">
                          {percentage}%
                        </Badge>
                      </div>
                    </div>
                    <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${percentage}%` }}
                        transition={{ duration: 0.5, delay: index * 0.1 }}
                        className={`h-full rounded-full ${habit.color}`}
                      />
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
