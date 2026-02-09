'use client';

import { motion } from 'framer-motion';
import { Target, CheckSquare, Flame, Trophy, TrendingUp, Calendar, Sparkles, Coins } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, ProgressBar, Badge } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import type { Habit, Task } from '@/types';

// Mock data for demonstration
const mockHabits: Habit[] = [
  {
    id: '1',
    userId: '1',
    title: 'Méditation matinale',
    description: '10 minutes de méditation',
    difficulty: 'easy',
    frequency: 'daily',
    positive: true,
    negative: false,
    streak: 7,
    completedToday: true,
    xpReward: 15,
    goldReward: 5,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    userId: '1',
    title: 'Sport',
    description: '30 minutes d\'exercice',
    difficulty: 'medium',
    frequency: 'daily',
    positive: true,
    negative: false,
    streak: 3,
    completedToday: false,
    xpReward: 25,
    goldReward: 10,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '3',
    userId: '1',
    title: 'Lecture',
    description: 'Lire 20 pages',
    difficulty: 'easy',
    frequency: 'daily',
    positive: true,
    negative: false,
    streak: 12,
    completedToday: false,
    xpReward: 15,
    goldReward: 5,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

const mockTasks: Task[] = [
  {
    id: '1',
    userId: '1',
    title: 'Finir le rapport',
    description: 'Rapport trimestriel',
    priority: 'high',
    dueDate: new Date(Date.now() + 86400000).toISOString(),
    completed: false,
    xpReward: 50,
    goldReward: 20,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    userId: '1',
    title: 'Rendez-vous dentiste',
    priority: 'medium',
    completed: false,
    xpReward: 20,
    goldReward: 10,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export default function DashboardPage() {
  const { user } = useAuthStore();

  const completedHabits = mockHabits.filter((h) => h.completedToday).length;
  const totalHabits = mockHabits.length;
  const habitProgress = (completedHabits / totalHabits) * 100;

  const pendingTasks = mockTasks.filter((t) => !t.completed).length;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Welcome Header */}
      <motion.div variants={itemVariants}>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Bonjour, {user?.username} ! 👋
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Prêt à conquérir une nouvelle journée ?
        </p>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Level Card */}
        <Card variant="elevated" className="bg-gradient-to-br from-primary-500 to-primary-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-primary-100 text-sm">Niveau</p>
              <p className="text-3xl font-bold">{user?.level}</p>
            </div>
            <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
              <Trophy className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-1">
              <span>XP</span>
              <span>{user?.xp}/{user?.xpToNextLevel}</span>
            </div>
            <ProgressBar value={user?.xp || 0} max={user?.xpToNextLevel || 100} variant="default" size="sm" />
          </div>
        </Card>

        {/* Streak Card */}
        <Card variant="elevated" className="bg-gradient-to-br from-orange-500 to-red-500 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">Série en cours</p>
              <p className="text-3xl font-bold">{user?.streak} jours</p>
            </div>
            <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
              <Flame className="w-6 h-6" />
            </div>
          </div>
          <p className="mt-4 text-sm text-orange-100">Continue comme ça ! 🔥</p>
        </Card>

        {/* Gold Card */}
        <Card variant="elevated" className="bg-gradient-to-br from-yellow-500 to-amber-500 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100 text-sm">Or</p>
              <p className="text-3xl font-bold">{user?.gold}</p>
            </div>
            <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
              <Coins className="w-6 h-6" />
            </div>
          </div>
          <p className="mt-4 text-sm text-yellow-100">Économise pour des récompenses !</p>
        </Card>

        {/* HP Card */}
        <Card variant="elevated" className="bg-gradient-to-br from-green-500 to-emerald-500 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm">Points de vie</p>
              <p className="text-3xl font-bold">{user?.hp}/{user?.maxHp}</p>
            </div>
            <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
              <TrendingUp className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4">
            <ProgressBar value={user?.hp || 0} max={user?.maxHp || 100} variant="hp" size="sm" />
          </div>
        </Card>
      </motion.div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Habits */}
        <motion.div variants={itemVariants} className="lg:col-span-2">
          <Card variant="bordered" padding="lg">
            <CardHeader className="flex flex-row items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center">
                  <Target className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                </div>
                <div>
                  <CardTitle>Habitudes du jour</CardTitle>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {completedHabits}/{totalHabits} complétées
                  </p>
                </div>
              </div>
              <Badge variant={habitProgress === 100 ? 'success' : 'default'}>
                {Math.round(habitProgress)}%
              </Badge>
            </CardHeader>
            
            <div className="mb-4">
              <ProgressBar value={habitProgress} variant="xp" />
            </div>

            <div className="space-y-3">
              {mockHabits.map((habit) => (
                <div
                  key={habit.id}
                  className={`flex items-center justify-between p-3 rounded-lg border transition-all ${
                    habit.completedToday
                      ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                      : 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                        habit.completedToday
                          ? 'bg-green-500 text-white'
                          : 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
                      }`}
                    >
                      {habit.completedToday ? (
                        <Sparkles className="w-4 h-4" />
                      ) : (
                        <Target className="w-4 h-4" />
                      )}
                    </div>
                    <div>
                      <p className={`font-medium ${habit.completedToday ? 'line-through text-gray-500' : 'text-gray-900 dark:text-white'}`}>
                        {habit.title}
                      </p>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <span className="text-game-xp">+{habit.xpReward} XP</span>
                        <span className="text-game-gold">+{habit.goldReward} 🪙</span>
                        {habit.streak > 0 && (
                          <span className="text-orange-500">🔥 {habit.streak}</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>

        {/* Tasks & Calendar */}
        <motion.div variants={itemVariants} className="space-y-6">
          {/* Pending Tasks */}
          <Card variant="bordered" padding="lg">
            <CardHeader className="flex flex-row items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-accent-100 dark:bg-accent-900/50 flex items-center justify-center">
                <CheckSquare className="w-5 h-5 text-accent-600 dark:text-accent-400" />
              </div>
              <div>
                <CardTitle>Tâches en attente</CardTitle>
                <p className="text-sm text-gray-500 dark:text-gray-400">{pendingTasks} tâches</p>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {mockTasks.filter((t) => !t.completed).map((task) => (
                  <div
                    key={task.id}
                    className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700"
                  >
                    <input
                      type="checkbox"
                      className="mt-1 rounded border-gray-300 dark:border-gray-600 text-primary-500 focus:ring-primary-500"
                    />
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 dark:text-white">{task.title}</p>
                      {task.dueDate && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          📅 {new Date(task.dueDate).toLocaleDateString('fr-FR')}
                        </p>
                      )}
                    </div>
                    <Badge
                      variant={
                        task.priority === 'urgent'
                          ? 'danger'
                          : task.priority === 'high'
                          ? 'warning'
                          : 'default'
                      }
                      size="sm"
                    >
                      {task.priority}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card variant="bordered" padding="lg">
            <CardHeader className="flex flex-row items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center">
                <Calendar className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <CardTitle>Cette semaine</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">23</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Habitudes</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">8</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Tâches</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <p className="text-2xl font-bold text-game-xp">+450</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">XP gagnés</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <p className="text-2xl font-bold text-game-gold">+125</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Or gagné</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}
