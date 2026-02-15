'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, X, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { HabitCard } from '@/components/habits/HabitCard';
import { Button, Input, Card } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import type { Habit, HabitDifficulty, HabitFrequency } from '@/types';

// API response types
interface HabitResponse {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  difficulty: HabitDifficulty;
  frequency: HabitFrequency;
  positive: boolean;
  negative: boolean;
  is_archived: boolean;
  target_value: number | null;
  current_streak: number;
  best_streak: number;
  xp_reward: number;
  coin_reward: number;
  completed_today: boolean;
  created_at: string;
  updated_at: string;
}

// Transform API response to frontend type
function transformHabit(h: HabitResponse): Habit {
  return {
    id: h.id,
    userId: h.user_id,
    title: h.title,
    description: h.description || '',
    difficulty: h.difficulty,
    frequency: h.frequency,
    positive: h.positive,
    negative: h.negative,
    streak: h.current_streak,
    completedToday: h.completed_today,
    xpReward: h.xp_reward,
    goldReward: h.coin_reward,
    createdAt: h.created_at,
    updatedAt: h.updated_at,
  };
}

export default function HabitsPage() {
  const { accessToken, fetchCharacter } = useAuthStore();
  const [habits, setHabits] = useState<Habit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [completing, setCompleting] = useState<string | null>(null);
  
  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [difficulty, setDifficulty] = useState<HabitDifficulty>('easy');
  const [frequency, setFrequency] = useState<HabitFrequency>('daily');
  const [isPositive, setIsPositive] = useState(true);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://habit.apps.ilanewep.cloud/api';

  // Fetch habits from API
  const fetchHabits = useCallback(async () => {
    if (!accessToken) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/habits/`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement des habitudes');
      }

      const data: HabitResponse[] = await response.json();
      setHabits(data.filter(h => !h.is_archived).map(transformHabit));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  }, [accessToken, API_URL]);

  useEffect(() => {
    fetchHabits();
  }, [fetchHabits]);

  // Create habit
  const handleCreateHabit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken || !title.trim()) return;

    setCreating(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/habits/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim() || null,
          difficulty,
          frequency,
          positive: isPositive,
          negative: !isPositive,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de la création');
      }

      // Reset form and refresh list
      setTitle('');
      setDescription('');
      setDifficulty('easy');
      setFrequency('daily');
      setIsPositive(true);
      setShowForm(false);
      await fetchHabits();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la création');
    } finally {
      setCreating(false);
    }
  };

  // Complete habit
  const handleComplete = async (habitId: string, positive: boolean) => {
    if (!accessToken || completing) return;

    setCompleting(habitId);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/completions/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          habit_id: habitId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de la complétion');
      }

      // Refresh habits and character (XP/coins updated)
      await Promise.all([fetchHabits(), fetchCharacter()]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la complétion');
    } finally {
      setCompleting(null);
    }
  };

  // Delete habit
  const handleDelete = async (habitId: string) => {
    if (!accessToken) return;
    
    if (!confirm('Supprimer cette habitude ?')) return;

    try {
      const response = await fetch(`${API_URL}/habits/${habitId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la suppression');
      }

      await fetchHabits();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de la suppression');
    }
  };

  const activeHabits = habits.filter(h => !h.completedToday);
  const completedHabits = habits.filter(h => h.completedToday);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Mes Habitudes
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            {habits.length} habitude{habits.length > 1 ? 's' : ''} • {completedHabits.length} complétée{completedHabits.length > 1 ? 's' : ''} aujourd'hui
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" onClick={fetchHabits} disabled={loading}>
            <RefreshCw className={loading ? 'animate-spin' : ''} />
          </Button>
          <Button onClick={() => setShowForm(!showForm)} className="gap-2">
            {showForm ? <X /> : <Plus />}
            {showForm ? 'Annuler' : 'Nouvelle habitude'}
          </Button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <p>{error}</p>
          <button onClick={() => setError(null)} className="ml-auto">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Create Form */}
      <AnimatePresence>
        {showForm && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <Card>
              <form onSubmit={handleCreateHabit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Titre *
                  </label>
                  <Input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Ex: Méditation matinale"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Description
                  </label>
                  <Input
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Ex: 10 minutes de méditation guidée"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Difficulté
                    </label>
                    <select
                      value={difficulty}
                      onChange={(e) => setDifficulty(e.target.value as HabitDifficulty)}
                      className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    >
                      <option value="trivial">Trivial (+5 XP)</option>
                      <option value="easy">Facile (+10 XP)</option>
                      <option value="medium">Moyen (+20 XP)</option>
                      <option value="hard">Difficile (+30 XP)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Fréquence
                    </label>
                    <select
                      value={frequency}
                      onChange={(e) => setFrequency(e.target.value as HabitFrequency)}
                      className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    >
                      <option value="daily">Quotidienne</option>
                      <option value="weekly">Hebdomadaire</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Type
                  </label>
                  <div className="flex gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        checked={isPositive}
                        onChange={() => setIsPositive(true)}
                        className="text-primary-500"
                      />
                      <span className="text-green-500">Positive (à faire)</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        checked={!isPositive}
                        onChange={() => setIsPositive(false)}
                        className="text-primary-500"
                      />
                      <span className="text-red-500">Négative (à éviter)</span>
                    </label>
                  </div>
                </div>

                <div className="flex justify-end gap-3">
                  <Button type="button" variant="ghost" onClick={() => setShowForm(false)}>
                    Annuler
                  </Button>
                  <Button type="submit" disabled={creating || !title.trim()}>
                    {creating ? <Loader2 className="animate-spin" /> : 'Créer'}
                  </Button>
                </div>
              </form>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading */}
      {loading && habits.length === 0 ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        </div>
      ) : (
        <>
          {/* Active Habits */}
          {activeHabits.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                À faire aujourd'hui ({activeHabits.length})
              </h2>
              <div className="space-y-3">
                {activeHabits.map((habit) => (
                  <HabitCard
                    key={habit.id}
                    habit={habit}
                    onComplete={handleComplete}
                    isLoading={completing === habit.id}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Completed Habits */}
          {completedHabits.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-500 dark:text-gray-400">
                Complétées ({completedHabits.length})
              </h2>
              <div className="space-y-3 opacity-60">
                {completedHabits.map((habit) => (
                  <HabitCard
                    key={habit.id}
                    habit={habit}
                    onComplete={handleComplete}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Empty State */}
          {habits.length === 0 && !loading && (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                Aucune habitude pour le moment.
              </p>
              <Button onClick={() => setShowForm(true)} className="gap-2">
                <Plus className="w-5 h-5" />
                Créer ma première habitude
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
