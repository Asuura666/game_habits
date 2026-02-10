'use client'

import { motion } from 'framer-motion'
import { Flame } from 'lucide-react'

interface StreakCounterProps {
  streak: number
  isNewRecord?: boolean
}

/**
 * Animated streak counter with fire effect
 * Intensity increases with streak length
 */
export function StreakCounter({ streak, isNewRecord = false }: StreakCounterProps) {
  // More flames for longer streaks
  const flameIntensity = Math.min(streak, 10) / 10

  return (
    <motion.div
      initial={{ scale: 0.9 }}
      animate={{ scale: 1 }}
      className="relative flex items-center gap-2"
    >
      {/* Fire icon with pulse animation */}
      <motion.div
        animate={{
          scale: [1, 1.1, 1],
          rotate: [0, -5, 5, 0],
        }}
        transition={{
          duration: 0.8,
          repeat: Infinity,
          repeatType: 'reverse',
        }}
        className="relative"
      >
        <Flame
          className={`w-8 h-8 ${
            streak >= 7
              ? 'text-red-500'
              : streak >= 3
              ? 'text-orange-500'
              : 'text-yellow-500'
          }`}
          fill={streak > 0 ? 'currentColor' : 'none'}
          style={{ opacity: 0.3 + flameIntensity * 0.7 }}
        />
        
        {/* Glow effect for high streaks */}
        {streak >= 7 && (
          <motion.div
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="absolute inset-0 blur-md bg-red-500/50 rounded-full"
          />
        )}
      </motion.div>

      {/* Streak number */}
      <motion.span
        key={streak}
        initial={{ scale: 1.5, color: '#FFD700' }}
        animate={{ scale: 1, color: '#FFFFFF' }}
        transition={{ duration: 0.3 }}
        className="text-2xl font-bold"
      >
        {streak}
      </motion.span>

      {/* New record badge */}
      {isNewRecord && (
        <motion.span
          initial={{ scale: 0, rotate: -20 }}
          animate={{ scale: 1, rotate: 0 }}
          className="absolute -top-2 -right-4 text-xs bg-gradient-to-r from-yellow-400 to-amber-500 text-black px-2 py-0.5 rounded-full font-bold"
        >
          NEW!
        </motion.span>
      )}
    </motion.div>
  )
}
