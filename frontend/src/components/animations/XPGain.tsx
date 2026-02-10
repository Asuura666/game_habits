'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useState, useEffect } from 'react'

interface XPGainProps {
  amount: number
  show: boolean
  onComplete?: () => void
}

/**
 * Animated XP gain notification
 * Floats up and fades out when XP is earned
 */
export function XPGain({ amount, show, onComplete }: XPGainProps) {
  const [visible, setVisible] = useState(show)

  useEffect(() => {
    if (show) {
      setVisible(true)
      const timer = setTimeout(() => {
        setVisible(false)
        onComplete?.()
      }, 1500)
      return () => clearTimeout(timer)
    }
  }, [show, onComplete])

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 20, scale: 0.8 }}
          animate={{ opacity: 1, y: -30, scale: 1 }}
          exit={{ opacity: 0, y: -60 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className="fixed top-20 right-8 z-50 pointer-events-none"
        >
          <div className="flex items-center gap-2 bg-gradient-to-r from-yellow-500 to-amber-500 text-white px-4 py-2 rounded-full shadow-lg">
            <span className="text-xl">⭐</span>
            <span className="font-bold text-lg">+{amount} XP</span>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
