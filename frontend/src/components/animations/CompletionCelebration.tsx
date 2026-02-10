'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useEffect, useState } from 'react'
import confetti from 'canvas-confetti'

interface CompletionResult {
  xpEarned: number
  coinsEarned: number
  newStreak: number
  isPersonalBest: boolean
}

interface CompletionCelebrationProps {
  show: boolean
  result: CompletionResult
  onComplete?: () => void
}

/**
 * Celebration animation when completing a habit
 * Shows XP, coins, and streak with satisfying animations
 */
export function CompletionCelebration({
  show,
  result,
  onComplete,
}: CompletionCelebrationProps) {
  const [visible, setVisible] = useState(show)

  useEffect(() => {
    if (show) {
      setVisible(true)

      // Quick confetti burst
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.7 },
        colors: ['#10B981', '#34D399', '#6EE7B7'],
      })

      const timer = setTimeout(() => {
        setVisible(false)
        onComplete?.()
      }, 2500)
      return () => clearTimeout(timer)
    }
  }, [show, onComplete])

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50"
        >
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            className="bg-gradient-to-r from-emerald-500 to-green-500 text-white px-6 py-4 rounded-2xl shadow-2xl"
          >
            {/* Checkmark */}
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', delay: 0.1 }}
              className="text-center mb-3"
            >
              <span className="text-4xl">✅</span>
            </motion.div>

            {/* Rewards */}
            <div className="flex items-center justify-center gap-6 text-lg font-semibold">
              {/* XP */}
              <motion.div
                initial={{ x: -20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="flex items-center gap-1"
              >
                <span>⭐</span>
                <span>+{result.xpEarned} XP</span>
              </motion.div>

              {/* Coins */}
              <motion.div
                initial={{ x: 20, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="flex items-center gap-1"
              >
                <span>🪙</span>
                <span>+{result.coinsEarned}</span>
              </motion.div>
            </div>

            {/* Streak */}
            <motion.div
              initial={{ y: 10, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="text-center mt-2 text-sm"
            >
              <span className="opacity-90">🔥 Streak: {result.newStreak}</span>
              {result.isPersonalBest && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.5, type: 'spring' }}
                  className="ml-2 bg-yellow-400 text-black px-2 py-0.5 rounded-full text-xs font-bold"
                >
                  RECORD!
                </motion.span>
              )}
            </motion.div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
