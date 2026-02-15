'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, Target, Flame, Trophy, TrendingUp, Calendar, Sparkles, Coins, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, ProgressBar, Badge, Button } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';

interface StatsOverview {
  total_habits: number;
  active_habits: number;
  completed_today: number;
  current_streak: number;
  best_streak: number;
  total_xp_earned: number;
  total_coins_earned: number;
  total_completions: number;
  habits_this_week: number;
  tasks_this_week: number;
  xp_this_week: number;
  coins_this_week: number;
  completion_rate: number;
}

interface HabitStats {
  habit_id: string;
  title: string;
  total_completions: number;
  current_streak: number;
  best_streak: number;
  completion_rate: number;
  last_completed: string | null;
}

interface TrendData {
  date: string;
  completions: number;
  xp_earned: number;
  coins_earned: number;
}

export default function StatsPage() {
  const { accessToken, character, user } = useAuthStore();
  const [overview, setOverview] = useState<StatsOverview | null>(null);
  const [habitStats, setHabitStats] = useState<HabitStats[]>([]);
  const [trends, setTrends] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://habit.apps.ilanewep.cloud/api';

  const fetchStats = useCallback(async () => {
    if (!accessToken) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const [overviewRes, habitsRes, trendsRes] = await Promise.all([
        fetch(`${API_URL}/stats/overview`, { headers: { 'Authorization': `Bearer ${accessToken}` } }),
        fetch(`${API_URL}/stats/habits`, { headers: { 'Authorization': `Bearer ${accessToken}` } }),
        fetch(`${API_URL}/stats/trends?days=7`, { headers: { 'Authorization': `Bearer ${accessToken}` } }),
      ]);

      if (!overviewRes.ok || !habitsRes.ok || !trendsRes.ok) {
        throw new Error('Erreur lors du chargement des statistiques');
      }

      const [overviewData, habitsData, trendsData] = await Promise.all([
        overviewRes.json(),
        habitsRes.json(),
        trendsRes.json(),
      ]);

      setOverview(overviewData);
      setHabitStats(habitsData);
      setTrends(trendsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  }, [accessToken, API_URL]);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <BarChart3 className="w-8 h-8 text-primary-500" />
            Statistiques
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Vue d'ensemble de ta progression</p>
        </div>
        <Button variant="ghost" onClick={fetchStats}>
          <RefreshCw className={loading ? 'animate-spin' : ''} />
        </Button>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-600">
          <AlertCircle className="w-5 h-5" />
          <p>{error}</p>
        </div>
      )}

      {/* Main Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-primary-100 dark:bg-primary-900/50 mx-auto mb-2">
            <Target className="w-6 h-6 text-primary-600" />
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{overview?.total_habits ?? 0}</p>
          <p className="text-sm text-gray-500">Habitudes actives</p>
        </Card>

        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-orange-100 dark:bg-orange-900/50 mx-auto mb-2">
            <Flame className="w-6 h-6 text-orange-600" />
          </div>
          <p className="text-3xl font-bold text-orange-500">{overview?.current_streak ?? character?.streak ?? 0}</p>
          <p className="text-sm text-gray-500">Streak actuel</p>
        </Card>

        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/50 mx-auto mb-2">
            <Trophy className="w-6 h-6 text-green-600" />
          </div>
          <p className="text-3xl font-bold text-green-500">{overview?.best_streak ?? 0}</p>
          <p className="text-sm text-gray-500">Meilleur streak</p>
        </Card>

        <Card className="text-center">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/50 mx-auto mb-2">
            <TrendingUp className="w-6 h-6 text-blue-600" />
          </div>
          <p className="text-3xl font-bold text-blue-500">{Math.round(overview?.completion_rate ?? 0)}%</p>
          <p className="text-sm text-gray-500">Taux de complétion</p>
        </Card>
      </div>

      {/* XP & Coins Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-game-xp/20 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-game-xp" />
            </div>
            <div>
              <CardTitle>Expérience</CardTitle>
              <p className="text-sm text-gray-500">Niveau {character?.level ?? user?.level ?? 1}</p>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Progression vers niveau {(character?.level ?? 1) + 1}</span>
                  <span className="text-game-xp">{character?.xp ?? 0}/{character?.xp_to_next_level ?? 100} XP</span>
                </div>
                <ProgressBar value={character?.xp ?? 0} max={character?.xp_to_next_level ?? 100} variant="xp" />
              </div>
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <div className="text-center">
                  <p className="text-2xl font-bold text-game-xp">+{overview?.xp_this_week ?? 0}</p>
                  <p className="text-xs text-gray-500">Cette semaine</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{overview?.total_xp_earned ?? 0}</p>
                  <p className="text-xs text-gray-500">Total gagné</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-game-gold/20 flex items-center justify-center">
              <Coins className="w-5 h-5 text-game-gold" />
            </div>
            <div>
              <CardTitle>Pièces d'or</CardTitle>
              <p className="text-sm text-gray-500">Solde actuel: {character?.coins ?? user?.gold ?? 0}</p>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                <p className="text-2xl font-bold text-game-gold">+{overview?.coins_this_week ?? 0}</p>
                <p className="text-xs text-gray-500">Cette semaine</p>
              </div>
              <div className="text-center p-4 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{overview?.total_coins_earned ?? 0}</p>
                <p className="text-xs text-gray-500">Total gagné</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Weekly Activity */}
      <Card>
        <CardHeader className="flex flex-row items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900/50 flex items-center justify-center">
            <Calendar className="w-5 h-5 text-purple-600" />
          </div>
          <CardTitle>Activité des 7 derniers jours</CardTitle>
        </CardHeader>
        <CardContent>
          {trends.length > 0 ? (
            <div className="flex items-end justify-between gap-2 h-32">
              {trends.map((day, i) => {
                const maxCompletions = Math.max(...trends.map(t => t.completions), 1);
                const height = (day.completions / maxCompletions) * 100;
                return (
                  <div key={i} className="flex-1 flex flex-col items-center gap-2">
                    <div
                      className="w-full bg-primary-500 rounded-t transition-all hover:bg-primary-600"
                      style={{ height: `${Math.max(height, 5)}%` }}
                      title={`${day.completions} complétion(s)`}
                    />
                    <span className="text-xs text-gray-500">
                      {new Date(day.date).toLocaleDateString('fr-FR', { weekday: 'short' })}
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">Pas encore de données</p>
          )}
        </CardContent>
      </Card>

      {/* Top Habits */}
      {habitStats.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Meilleures habitudes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {habitStats.slice(0, 5).map((habit, i) => (
                <div key={habit.habit_id} className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center text-sm font-bold text-primary-600">
                    {i + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 dark:text-white truncate">{habit.title}</p>
                    <p className="text-sm text-gray-500">{habit.total_completions} complétions • Streak max: {habit.best_streak}</p>
                  </div>
                  <Badge variant={habit.completion_rate >= 80 ? 'success' : habit.completion_rate >= 50 ? 'warning' : 'default'}>
                    {Math.round(habit.completion_rate)}%
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </motion.div>
  );
}
