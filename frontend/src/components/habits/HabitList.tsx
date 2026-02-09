'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Filter, SortAsc } from 'lucide-react';
import { HabitCard } from './HabitCard';
import { Button } from '@/components/ui';
import type { Habit } from '@/types';

interface HabitListProps {
  habits: Habit[];
  onComplete?: (habitId: string, positive: boolean) => void;
  onAddHabit?: () => void;
}

export function HabitList({ habits, onComplete, onAddHabit }: HabitListProps) {
  const [filter, setFilter] = useState<'all' | 'completed' | 'pending'>('all');
  const [sortBy, setSortBy] = useState<'name' | 'difficulty' | 'streak'>('name');

  const filteredHabits = habits.filter((habit) => {
    if (filter === 'completed') return habit.completedToday;
    if (filter === 'pending') return !habit.completedToday;
    return true;
  });

  const sortedHabits = [...filteredHabits].sort((a, b) => {
    if (sortBy === 'name') return a.title.localeCompare(b.title);
    if (sortBy === 'difficulty') {
      const order = { trivial: 0, easy: 1, medium: 2, hard: 3 };
      return order[a.difficulty] - order[b.difficulty];
    }
    if (sortBy === 'streak') return b.streak - a.streak;
    return 0;
  });

  const completedCount = habits.filter((h) => h.completedToday).length;
  const progress = habits.length > 0 ? (completedCount / habits.length) * 100 : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Mes Habitudes</h2>
          <p className="text-gray-500 dark:text-gray-400">
            {completedCount} / {habits.length} complétées aujourd'hui
          </p>
        </div>
        <Button onClick={onAddHabit}>
          <Plus className="w-5 h-5 mr-2" />
          Nouvelle habitude
        </Button>
      </div>

      {/* Progress */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Progression du jour
          </span>
          <span className="text-sm font-bold text-primary-600 dark:text-primary-400">
            {Math.round(progress)}%
          </span>
        </div>
        <div className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
            className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full"
          />
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value as typeof filter)}
            className="px-3 py-1.5 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">Toutes</option>
            <option value="pending">En attente</option>
            <option value="completed">Complétées</option>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <SortAsc className="w-4 h-4 text-gray-400" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            className="px-3 py-1.5 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="name">Nom</option>
            <option value="difficulty">Difficulté</option>
            <option value="streak">Série</option>
          </select>
        </div>
      </div>

      {/* Habit List */}
      <div className="space-y-3">
        <AnimatePresence mode="popLayout">
          {sortedHabits.map((habit) => (
            <HabitCard key={habit.id} habit={habit} onComplete={onComplete} />
          ))}
        </AnimatePresence>

        {sortedHabits.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              {filter === 'all' 
                ? "Aucune habitude pour l'instant"
                : filter === 'completed'
                ? "Aucune habitude complétée"
                : "Toutes les habitudes sont complétées !"}
            </p>
            {filter === 'all' && (
              <Button onClick={onAddHabit} variant="secondary">
                <Plus className="w-5 h-5 mr-2" />
                Créer ma première habitude
              </Button>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}
