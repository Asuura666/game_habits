'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, X } from 'lucide-react';
import { HabitList } from '@/components/habits';
import { Button, Input, Card } from '@/components/ui';
import type { Habit, HabitDifficulty, HabitFrequency } from '@/types';

// Mock data
const initialHabits: Habit[] = [
  {
    id: '1',
    userId: '1',
    title: 'Méditation matinale',
    description: '10 minutes de méditation guidée',
    difficulty: 'easy',
    frequency: 'daily',
    positive: true,
    negative: false,
    streak: 7,
    completedToday: false,
    xpReward: 15,
    goldReward: 5,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    userId: '1',
    title: 'Sport',
    description: '30 minutes d\'exercice physique',
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
    description: 'Lire au moins 20 pages',
    difficulty: 'easy',
    frequency: 'daily',
    positive: true,
    negative: false,
    streak: 12,
    completedToday: true,
    xpReward: 15,
    goldReward: 5,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '4',
    userId: '1',
    title: 'Pas de réseaux sociaux après 21h',
    description: 'Éviter les distractions le soir',
    difficulty: 'hard',
    frequency: 'daily',
    positive: false,
    negative: true,
    streak: 2,
    completedToday: false,
    xpReward: 30,
    goldReward: 15,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '5',
    userId: '1',
    title: 'Boire 2L d\'eau',
    description: 'Hydratation quotidienne',
    difficulty: 'trivial',
    frequency: 'daily',
    positive: true,
    negative: false,
    streak: 5,
    completedToday: false,
    xpReward: 10,
    goldReward: 3,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

export default function HabitsPage() {
  const [habits, setHabits] = useState<Habit[]>(initialHabits);
  const [showModal, setShowModal] = useState(false);
  const [newHabit, setNewHabit] = useState({
    title: '',
    description: '',
    difficulty: 'easy' as HabitDifficulty,
    frequency: 'daily' as HabitFrequency,
    positive: true,
    negative: false,
  });

  const handleComplete = (habitId: string, positive: boolean) => {
    setHabits((prev) =>
      prev.map((h) =>
        h.id === habitId
          ? { ...h, completedToday: positive, streak: positive ? h.streak + 1 : Math.max(0, h.streak - 1) }
          : h
      )
    );
  };

  const handleAddHabit = () => {
    if (!newHabit.title.trim()) return;

    const habit: Habit = {
      id: Date.now().toString(),
      userId: '1',
      title: newHabit.title,
      description: newHabit.description,
      difficulty: newHabit.difficulty,
      frequency: newHabit.frequency,
      positive: newHabit.positive,
      negative: newHabit.negative,
      streak: 0,
      completedToday: false,
      xpReward: { trivial: 10, easy: 15, medium: 25, hard: 40 }[newHabit.difficulty],
      goldReward: { trivial: 3, easy: 5, medium: 10, hard: 20 }[newHabit.difficulty],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    setHabits((prev) => [habit, ...prev]);
    setNewHabit({
      title: '',
      description: '',
      difficulty: 'easy',
      frequency: 'daily',
      positive: true,
      negative: false,
    });
    setShowModal(false);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <HabitList
        habits={habits}
        onComplete={handleComplete}
        onAddHabit={() => setShowModal(true)}
      />

      {/* Add Habit Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
            onClick={() => setShowModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <Card variant="elevated" padding="lg" className="w-full max-w-md bg-white dark:bg-gray-800">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                    Nouvelle habitude
                  </h2>
                  <button
                    onClick={() => setShowModal(false)}
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <X className="w-5 h-5 text-gray-500" />
                  </button>
                </div>

                <div className="space-y-4">
                  <Input
                    label="Titre"
                    value={newHabit.title}
                    onChange={(e) => setNewHabit({ ...newHabit, title: e.target.value })}
                    placeholder="Ex: Méditation quotidienne"
                  />

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                      Description (optionnel)
                    </label>
                    <textarea
                      value={newHabit.description}
                      onChange={(e) => setNewHabit({ ...newHabit, description: e.target.value })}
                      placeholder="Décrivez votre habitude..."
                      className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      rows={3}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                        Difficulté
                      </label>
                      <select
                        value={newHabit.difficulty}
                        onChange={(e) => setNewHabit({ ...newHabit, difficulty: e.target.value as HabitDifficulty })}
                        className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="trivial">Trivial</option>
                        <option value="easy">Facile</option>
                        <option value="medium">Moyen</option>
                        <option value="hard">Difficile</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                        Fréquence
                      </label>
                      <select
                        value={newHabit.frequency}
                        onChange={(e) => setNewHabit({ ...newHabit, frequency: e.target.value as HabitFrequency })}
                        className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="daily">Quotidien</option>
                        <option value="weekly">Hebdomadaire</option>
                        <option value="monthly">Mensuel</option>
                      </select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Type d'habitude
                    </label>
                    <div className="flex gap-4">
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={newHabit.positive}
                          onChange={(e) => setNewHabit({ ...newHabit, positive: e.target.checked })}
                          className="rounded border-gray-300 text-green-500 focus:ring-green-500"
                        />
                        <span className="text-sm text-gray-600 dark:text-gray-400">Positive (+)</span>
                      </label>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={newHabit.negative}
                          onChange={(e) => setNewHabit({ ...newHabit, negative: e.target.checked })}
                          className="rounded border-gray-300 text-red-500 focus:ring-red-500"
                        />
                        <span className="text-sm text-gray-600 dark:text-gray-400">Négative (-)</span>
                      </label>
                    </div>
                  </div>

                  <div className="flex gap-3 pt-4">
                    <Button variant="secondary" onClick={() => setShowModal(false)} className="flex-1">
                      Annuler
                    </Button>
                    <Button onClick={handleAddHabit} className="flex-1">
                      <Plus className="w-5 h-5 mr-2" />
                      Créer
                    </Button>
                  </div>
                </div>
              </Card>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
