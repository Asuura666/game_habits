'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Star, Sparkles, Gift, X } from 'lucide-react';
import { LPCCharacter } from './LPCCharacter';
import { getTierByLevel, type CharacterClass } from '@/types/character';
import { cn } from '@/lib/utils';

interface LevelUpNotificationProps {
  show: boolean;
  newLevel: number;
  characterClass?: CharacterClass;
  gender?: 'male' | 'female';
  spriteSheetUrl?: string;
  unlockedItems?: string[];
  onClose: () => void;
  autoCloseMs?: number;
}

export function LevelUpNotification({
  show,
  newLevel,
  characterClass = 'warrior',
  gender,
  spriteSheetUrl,
  unlockedItems = [],
  onClose,
  autoCloseMs = 5000,
}: LevelUpNotificationProps) {
  const [isVisible, setIsVisible] = useState(false);
  const tier = getTierByLevel(newLevel);

  useEffect(() => {
    if (show) {
      setIsVisible(true);
      if (autoCloseMs > 0) {
        const timer = setTimeout(() => {
          setIsVisible(false);
          setTimeout(onClose, 300);
        }, autoCloseMs);
        return () => clearTimeout(timer);
      }
    }
  }, [show, autoCloseMs, onClose]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 300);
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50"
            onClick={handleClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ type: 'spring', damping: 20, stiffness: 300 }}
            className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none"
          >
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 max-w-md w-full mx-4 shadow-2xl pointer-events-auto border border-gray-700">
              {/* Close button */}
              <button
                onClick={handleClose}
                className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-6 h-6" />
              </button>

              {/* Sparkles background */}
              <div className="absolute inset-0 overflow-hidden rounded-2xl pointer-events-none">
                {[...Array(20)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute"
                    initial={{ 
                      x: Math.random() * 100 + '%', 
                      y: '100%',
                      opacity: 0 
                    }}
                    animate={{ 
                      y: '-20%',
                      opacity: [0, 1, 0],
                    }}
                    transition={{ 
                      duration: 2 + Math.random() * 2,
                      repeat: Infinity,
                      delay: Math.random() * 2,
                    }}
                  >
                    <Sparkles className={cn(
                      'w-4 h-4',
                      tier.tier === 'legendary' && 'text-yellow-400',
                      tier.tier === 'epic' && 'text-purple-400',
                      tier.tier === 'rare' && 'text-blue-400',
                      tier.tier === 'uncommon' && 'text-green-400',
                      tier.tier === 'common' && 'text-gray-400',
                    )} />
                  </motion.div>
                ))}
              </div>

              {/* Content */}
              <div className="relative text-center">
                {/* Title */}
                <motion.div
                  initial={{ y: -20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="mb-6"
                >
                  <Star className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
                  <h2 className="text-3xl font-bold text-white">Level Up!</h2>
                </motion.div>

                {/* Character with animation */}
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.3, type: 'spring', damping: 10 }}
                  className="mb-6"
                >
                  <LPCCharacter
                    characterClass={characterClass}
                    gender={gender}
                    level={newLevel}
                    size="2xl"
                    showLevel={true}
                    spriteSheetUrl={spriteSheetUrl}
                    animation="spellcast"
                    animated={true}
                    className="mx-auto"
                  />
                </motion.div>

                {/* Level display */}
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.5, type: 'spring' }}
                  className={cn(
                    'text-6xl font-black mb-2',
                    tier.tier === 'legendary' && 'text-yellow-400',
                    tier.tier === 'epic' && 'text-purple-400',
                    tier.tier === 'rare' && 'text-blue-400',
                    tier.tier === 'uncommon' && 'text-green-400',
                    tier.tier === 'common' && 'text-gray-300',
                  )}
                >
                  {newLevel}
                </motion.div>
                <p className="text-gray-400 mb-6 capitalize">{tier.tier}</p>

                {/* Unlocked items */}
                {unlockedItems.length > 0 && (
                  <motion.div
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.7 }}
                    className="bg-gray-800/50 rounded-xl p-4 border border-gray-700"
                  >
                    <div className="flex items-center justify-center gap-2 text-yellow-400 mb-3">
                      <Gift className="w-5 h-5" />
                      <span className="font-semibold">Débloqué !</span>
                    </div>
                    <div className="flex flex-wrap justify-center gap-2">
                      {unlockedItems.map((item, i) => (
                        <span
                          key={i}
                          className="bg-gray-700 px-3 py-1 rounded-full text-sm text-gray-200"
                        >
                          {item}
                        </span>
                      ))}
                    </div>
                  </motion.div>
                )}

                {/* Close button */}
                <motion.button
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1 }}
                  onClick={handleClose}
                  className={cn(
                    'mt-6 px-8 py-3 rounded-xl font-semibold text-white',
                    'bg-gradient-to-r transition-all hover:scale-105',
                    tier.tier === 'legendary' && 'from-yellow-500 to-orange-500',
                    tier.tier === 'epic' && 'from-purple-500 to-pink-500',
                    tier.tier === 'rare' && 'from-blue-500 to-cyan-500',
                    tier.tier === 'uncommon' && 'from-green-500 to-emerald-500',
                    tier.tier === 'common' && 'from-gray-500 to-gray-600',
                  )}
                >
                  Continuer
                </motion.button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
