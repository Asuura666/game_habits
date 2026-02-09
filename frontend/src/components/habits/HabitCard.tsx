'use client';

import { motion } from 'framer-motion';
import { Plus, Minus, Flame, Coins, Sparkles } from 'lucide-react';
import { cn, getDifficultyColor } from '@/lib/utils';
import { Card } from '@/components/ui';
import type { Habit } from '@/types';

interface HabitCardProps {
  habit: Habit;
  onComplete?: (habitId: string, positive: boolean) => void;
}

export function HabitCard({ habit, onComplete }: HabitCardProps) {
  const handlePositive = () => {
    if (onComplete && !habit.completedToday) {
      onComplete(habit.id, true);
    }
  };

  const handleNegative = () => {
    if (onComplete) {
      onComplete(habit.id, false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
    >
      <Card variant="bordered" className={cn(
        'flex items-center gap-4 transition-all',
        habit.completedToday && 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700'
      )}>
        {/* Positive Button */}
        {habit.positive && (
          <button
            onClick={handlePositive}
            disabled={habit.completedToday}
            className={cn(
              'w-12 h-12 rounded-lg flex items-center justify-center transition-all',
              habit.completedToday
                ? 'bg-green-500 text-white cursor-not-allowed'
                : 'bg-green-100 text-green-600 hover:bg-green-500 hover:text-white dark:bg-green-900/50 dark:text-green-400 dark:hover:bg-green-500 dark:hover:text-white'
            )}
          >
            {habit.completedToday ? (
              <Sparkles className="w-6 h-6" />
            ) : (
              <Plus className="w-6 h-6" />
            )}
          </button>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className={cn(
              'font-semibold text-gray-900 dark:text-white truncate',
              habit.completedToday && 'line-through text-gray-500 dark:text-gray-400'
            )}>
              {habit.title}
            </h3>
            <span className={cn(
              'w-2 h-2 rounded-full',
              getDifficultyColor(habit.difficulty)
            )} />
          </div>
          
          {habit.description && (
            <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
              {habit.description}
            </p>
          )}

          <div className="flex items-center gap-4 mt-2">
            {/* Rewards */}
            <div className="flex items-center gap-1 text-sm">
              <Sparkles className="w-4 h-4 text-game-xp" />
              <span className="text-game-xp">+{habit.xpReward} XP</span>
            </div>
            <div className="flex items-center gap-1 text-sm">
              <Coins className="w-4 h-4 text-game-gold" />
              <span className="text-game-gold">+{habit.goldReward}</span>
            </div>
            {/* Streak */}
            {habit.streak > 0 && (
              <div className="flex items-center gap-1 text-sm">
                <Flame className="w-4 h-4 text-orange-500" />
                <span className="text-orange-500">{habit.streak}</span>
              </div>
            )}
          </div>
        </div>

        {/* Negative Button */}
        {habit.negative && (
          <button
            onClick={handleNegative}
            className="w-12 h-12 rounded-lg bg-red-100 text-red-600 hover:bg-red-500 hover:text-white dark:bg-red-900/50 dark:text-red-400 dark:hover:bg-red-500 dark:hover:text-white flex items-center justify-center transition-all"
          >
            <Minus className="w-6 h-6" />
          </button>
        )}
      </Card>
    </motion.div>
  );
}
