'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Target, CheckSquare, Flame, Trophy, TrendingUp, Calendar, Sparkles, Coins, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, ProgressBar, Badge, Button } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import Link from 'next/link';

interface HabitResponse {
  id: string;
  title: string;
  description: string | null;
  difficulty: string;
  positive: boolean;
  negative: boolean;
  current_streak: number;
  xp_reward: number;
  coin_reward: number;
  completed_today: boolean;
}

interface TaskResponse {
  id: string;
  title: string;
  description: string | null;
  priority: string;
  due_date: string | null;
  completed: boolean;
  xp_reward: number;
  coin_reward: number;
}

interface StatsOverview {
  total_habits: number;
  completed_today: number;
  current_streak: number;
  best_streak: number;
  total_xp_earned: number;
  total_coins_earned: number;
  habits_this_week: number;
  tasks_this_week: number;
  xp_this_week: number;
  coins_this_week: number;
}

export default function DashboardPage() {
  const { user, character, accessToken, fetchCharacter } = useAuthStore();
  const [habits, setHabits] = useState<HabitResponse[]>([]);
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [stats, setStats] = useState<StatsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://habit.apps.ilanewep.cloud/api';

  const fetchDashboardData = useCallback(async () => {
    if (!accessToken) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const [habitsRes, tasksRes, statsRes] = await Promise.all([
        fetch(`${API_URL}/habits/today`, {
          headers: { 'Authorization': `Bearer ${accessToken}` },
        }),
        fetch(`${API_URL}/tasks/`, {
          headers: { 'Authorization': `Bearer ${accessToken}` },
        }),
        fetch(`${API_URL}/stats/overview`, {
          headers: { 'Authorization': `Bearer ${accessToken}` },
        }),
      ]);

      if (!habitsRes.ok || !tasksRes.ok || !statsRes.ok) {
        throw new Error('Erreur lors du chargement des données');
      }

      const [habitsData, tasksData, statsData] = await Promise.all([
        habitsRes.json(),
        tasksRes.json(),
        statsRes.json(),
      ]);

      setHabits(habitsData);
      setTasks(tasksData);
      setStats(statsData);
      await fetchCharacter();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  }, [accessToken, API_URL, fetchCharacter]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Handle habit completion
  const handleCompleteHabit = async (habitId: string) => {
    if (!accessToken) return;

    try {
      const response = await fetch(`${API_URL}/completions/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ habit_id: habitId }),
      });

      if (!response.ok) throw new Error('Erreur');
      await fetchDashboardData();
    } catch (err) {
      setError('Erreur lors de la complétion');
    }
  };

  const completedHabits = habits.filter(h => h.completed_today).length;
  const totalHabits = habits.length;
  const habitProgress = totalHabits > 0 ? (completedHabits / totalHabits) * 100 : 0;
  const pendingTasks = tasks.filter(t => !t.completed).length;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-6xl mx-auto space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Bonjour, {user?.username} 👋
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Niveau {character?.level ?? user?.level} • {character?.xp ?? user?.xp} XP
          </p>
        </div>
        <Button variant="ghost" onClick={fetchDashboardData}>
          <RefreshCw className={loading ? 'animate-spin' : ''} />
        </Button>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400">
          <AlertCircle className="w-5 h-5" />
          <p>{error}</p>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900/50 mx-auto mb-2">
            <Flame className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{character?.streak ?? stats?.current_streak ?? 0}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">Jours de streak</p>
        </Card>

        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-game-xp/20 mx-auto mb-2">
            <Sparkles className="w-6 h-6 text-game-xp" />
          </div>
          <p className="text-2xl font-bold text-game-xp">{character?.xp ?? user?.xp ?? 0}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">XP Total</p>
        </Card>

        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-game-gold/20 mx-auto mb-2">
            <Coins className="w-6 h-6 text-game-gold" />
          </div>
          <p className="text-2xl font-bold text-game-gold">{character?.coins ?? user?.gold ?? 0}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">Pièces</p>
        </Card>

        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/50 mx-auto mb-2">
            <Trophy className="w-6 h-6 text-green-600 dark:text-green-400" />
          </div>
          <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.best_streak ?? 0}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">Meilleur streak</p>
        </Card>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Habits */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center">
                  <Target className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                </div>
                <div>
                  <CardTitle>Habitudes du jour</CardTitle>
                  <p className="text-sm text-gray-500">{completedHabits}/{totalHabits} complétées</p>
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
              {habits.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  Aucune habitude. <Link href="/habits" className="text-primary-500 hover:underline">Créer une habitude</Link>
                </p>
              ) : (
                habits.slice(0, 5).map((habit) => (
                  <div
                    key={habit.id}
                    className={`flex items-center justify-between p-3 rounded-lg border transition-all ${
                      habit.completed_today
                        ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                        : 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700 hover:border-primary-300'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => !habit.completed_today && handleCompleteHabit(habit.id)}
                        disabled={habit.completed_today}
                        className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all ${
                          habit.completed_today
                            ? 'bg-green-500 text-white cursor-not-allowed'
                            : 'bg-gray-200 dark:bg-gray-700 text-gray-500 hover:bg-green-500 hover:text-white'
                        }`}
                      >
                        {habit.completed_today ? <Sparkles className="w-4 h-4" /> : <Target className="w-4 h-4" />}
                      </button>
                      <div>
                        <p className={`font-medium ${habit.completed_today ? 'line-through text-gray-500' : 'text-gray-900 dark:text-white'}`}>
                          {habit.title}
                        </p>
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <span className="text-game-xp">+{habit.xp_reward} XP</span>
                          <span className="text-game-gold">+{habit.coin_reward} 🪙</span>
                          {habit.current_streak > 0 && <span className="text-orange-500">🔥 {habit.current_streak}</span>}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
              {habits.length > 5 && (
                <Link href="/habits" className="block text-center text-primary-500 hover:underline text-sm">
                  Voir toutes les habitudes →
                </Link>
              )}
            </div>
          </Card>
        </div>

        {/* Tasks & Stats */}
        <div className="space-y-6">
          {/* Tasks */}
          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-accent-100 dark:bg-accent-900/50 flex items-center justify-center">
                <CheckSquare className="w-5 h-5 text-accent-600 dark:text-accent-400" />
              </div>
              <div>
                <CardTitle>Tâches en attente</CardTitle>
                <p className="text-sm text-gray-500">{pendingTasks} tâche{pendingTasks > 1 ? 's' : ''}</p>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {tasks.filter(t => !t.completed).length === 0 ? (
                  <p className="text-gray-500 text-center py-2">Aucune tâche en attente</p>
                ) : (
                  tasks.filter(t => !t.completed).slice(0, 3).map((task) => (
                    <div key={task.id} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 dark:text-white">{task.title}</p>
                        {task.due_date && (
                          <p className="text-xs text-gray-500 mt-1">
                            📅 {new Date(task.due_date).toLocaleDateString('fr-FR')}
                          </p>
                        )}
                      </div>
                      <Badge variant={task.priority === 'urgent' ? 'danger' : task.priority === 'high' ? 'warning' : 'default'} size="sm">
                        {task.priority}
                      </Badge>
                    </div>
                  ))
                )}
                <Link href="/tasks" className="block text-center text-primary-500 hover:underline text-sm">
                  Voir les tâches →
                </Link>
              </div>
            </CardContent>
          </Card>

          {/* Week Stats */}
          <Card>
            <CardHeader className="flex flex-row items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900/50 flex items-center justify-center">
                <Calendar className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <CardTitle>Cette semaine</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.habits_this_week ?? 0}</p>
                  <p className="text-xs text-gray-500">Habitudes</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats?.tasks_this_week ?? 0}</p>
                  <p className="text-xs text-gray-500">Tâches</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <p className="text-2xl font-bold text-game-xp">+{stats?.xp_this_week ?? 0}</p>
                  <p className="text-xs text-gray-500">XP gagnés</p>
                </div>
                <div className="text-center p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                  <p className="text-2xl font-bold text-game-gold">+{stats?.coins_this_week ?? 0}</p>
                  <p className="text-xs text-gray-500">Or gagné</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </motion.div>
  );
}
