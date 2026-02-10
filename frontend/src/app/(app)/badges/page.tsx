'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Award, Lock, Star, Gem, Crown, Loader2, CheckCircle, X, Sparkles } from 'lucide-react';
import { Card, Button, Badge as UiBadge } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';

interface BadgeData {
  id: string;
  code: string;
  name: string;
  description: string;
  icon: string;
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  xp_reward: number;
  condition_type: string;
  condition_value: Record<string, unknown>;
  is_secret: boolean;
  is_seasonal: boolean;
}

interface UserBadge {
  badge: BadgeData;
  is_unlocked: boolean;
  unlocked_at: string | null;
  is_displayed: boolean;
  display_position: number | null;
}

interface BadgeCollection {
  total_badges: number;
  unlocked_count: number;
  locked_count: number;
  displayed_badges: UserBadge[];
  recent_unlocks: UserBadge[];
  rarest_badge: UserBadge | null;
}

const RARITY_CONFIG = {
  common: { color: 'text-gray-400 border-gray-400/50 bg-gray-400/10', label: 'Commun', icon: Star },
  uncommon: { color: 'text-green-400 border-green-400/50 bg-green-400/10', label: 'Peu commun', icon: Star },
  rare: { color: 'text-blue-400 border-blue-400/50 bg-blue-400/10', label: 'Rare', icon: Gem },
  epic: { color: 'text-purple-400 border-purple-400/50 bg-purple-400/10', label: 'Épique', icon: Crown },
  legendary: { color: 'text-yellow-400 border-yellow-400/50 bg-yellow-400/10', label: 'Légendaire', icon: Crown },
};

const CATEGORY_LABELS: Record<string, string> = {
  streak: 'Séries',
  completion: 'Complétion',
  level: 'Niveaux',
  social: 'Social',
  combat: 'Combat',
  achievement: 'Accomplissements',
};

export default function BadgesPage() {
  const { accessToken } = useAuthStore();
  const [badges, setBadges] = useState<UserBadge[]>([]);
  const [collection, setCollection] = useState<BadgeCollection | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedBadge, setSelectedBadge] = useState<UserBadge | null>(null);
  const [filter, setFilter] = useState<'all' | 'unlocked' | 'locked'>('all');
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const [displayedBadgeIds, setDisplayedBadgeIds] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  // Fetch badges and collection
  useEffect(() => {
    const fetchData = async () => {
      if (!accessToken) return;
      setIsLoading(true);

      try {
        // Fetch all badges with unlock status
        const badgesRes = await fetch(`${API_URL}/badges/?include_secret=true`, {
          headers: { Authorization: `Bearer ${accessToken}` }
        });
        if (badgesRes.ok) {
          const data = await badgesRes.json();
          setBadges(data);
        }

        // Fetch collection summary
        const collectionRes = await fetch(`${API_URL}/badges/collection`, {
          headers: { Authorization: `Bearer ${accessToken}` }
        });
        if (collectionRes.ok) {
          const data = await collectionRes.json();
          setCollection(data);
          setDisplayedBadgeIds(data.displayed_badges.map((b: UserBadge) => b.badge.id));
        }
      } catch (err) {
        console.error('Failed to fetch badges:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [accessToken, API_URL]);

  // Filter badges
  const filteredBadges = badges.filter(b => {
    if (filter === 'unlocked' && !b.is_unlocked) return false;
    if (filter === 'locked' && b.is_unlocked) return false;
    if (categoryFilter && b.badge.condition_type !== categoryFilter) return false;
    return true;
  });

  // Group by category
  const categories = [...new Set(badges.map(b => b.badge.condition_type))];

  // Toggle badge display
  const toggleDisplay = (badgeId: string) => {
    if (displayedBadgeIds.includes(badgeId)) {
      setDisplayedBadgeIds(prev => prev.filter(id => id !== badgeId));
    } else if (displayedBadgeIds.length < 3) {
      setDisplayedBadgeIds(prev => [...prev, badgeId]);
    }
  };

  // Save displayed badges
  const saveDisplayedBadges = async () => {
    setIsSaving(true);
    try {
      const res = await fetch(`${API_URL}/badges/display`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ badge_ids: displayedBadgeIds })
      });
      if (res.ok) {
        setSelectedBadge(null);
      }
    } catch (err) {
      console.error('Failed to save displayed badges:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const unlockedCount = badges.filter(b => b.is_unlocked).length;
  const progressPercentage = badges.length > 0 ? (unlockedCount / badges.length) * 100 : 0;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
          <Award className="w-8 h-8 text-yellow-500" />
          Badges & Succès
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Débloque des badges en accomplissant des défis
        </p>
      </div>

      {/* Progress Card */}
      <Card variant="bordered" padding="lg" className="bg-gradient-to-r from-primary-500/10 to-accent-500/10">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Progression</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {unlockedCount} / {badges.length} badges
            </p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-primary-500">{Math.round(progressPercentage)}%</p>
          </div>
        </div>
        <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${progressPercentage}%` }}
            transition={{ duration: 1, ease: 'easeOut' }}
            className="h-full bg-gradient-to-r from-primary-500 to-accent-500"
          />
        </div>

        {/* Displayed Badges */}
        {collection?.displayed_badges && collection.displayed_badges.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Badges affichés sur ton profil</p>
            <div className="flex gap-3">
              {collection.displayed_badges.map((ub) => (
                <div
                  key={ub.badge.id}
                  className={cn(
                    'w-14 h-14 rounded-xl border-2 flex items-center justify-center text-2xl',
                    RARITY_CONFIG[ub.badge.rarity].color
                  )}
                >
                  {ub.badge.icon}
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>

      {/* Rarest Badge */}
      {collection?.rarest_badge && (
        <Card variant="bordered" padding="md" className="border-yellow-500/50 bg-yellow-500/5">
          <div className="flex items-center gap-4">
            <div className={cn(
              'w-16 h-16 rounded-xl border-2 flex items-center justify-center text-3xl',
              RARITY_CONFIG[collection.rarest_badge.badge.rarity].color
            )}>
              {collection.rarest_badge.badge.icon}
            </div>
            <div>
              <p className="text-sm text-yellow-500 flex items-center gap-1">
                <Sparkles className="w-4 h-4" />
                Badge le plus rare
              </p>
              <p className="font-bold text-gray-900 dark:text-white">{collection.rarest_badge.badge.name}</p>
              <UiBadge size="sm" className={RARITY_CONFIG[collection.rarest_badge.badge.rarity].color}>
                {RARITY_CONFIG[collection.rarest_badge.badge.rarity].label}
              </UiBadge>
            </div>
          </div>
        </Card>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setFilter('all')}
          className={cn(
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            filter === 'all'
              ? 'bg-primary-500 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
          )}
        >
          Tous ({badges.length})
        </button>
        <button
          onClick={() => setFilter('unlocked')}
          className={cn(
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            filter === 'unlocked'
              ? 'bg-green-500 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
          )}
        >
          <CheckCircle className="w-4 h-4 inline mr-1" />
          Débloqués ({unlockedCount})
        </button>
        <button
          onClick={() => setFilter('locked')}
          className={cn(
            'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            filter === 'locked'
              ? 'bg-gray-500 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
          )}
        >
          <Lock className="w-4 h-4 inline mr-1" />
          Verrouillés ({badges.length - unlockedCount})
        </button>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setCategoryFilter(null)}
          className={cn(
            'px-3 py-1.5 rounded-lg text-xs font-medium transition-colors',
            !categoryFilter
              ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
          )}
        >
          Toutes catégories
        </button>
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setCategoryFilter(cat)}
            className={cn(
              'px-3 py-1.5 rounded-lg text-xs font-medium transition-colors',
              categoryFilter === cat
                ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'
            )}
          >
            {CATEGORY_LABELS[cat] || cat}
          </button>
        ))}
      </div>

      {/* Badges Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
        {filteredBadges.map((userBadge, index) => {
          const { badge, is_unlocked } = userBadge;
          const rarityConfig = RARITY_CONFIG[badge.rarity];

          return (
            <motion.div
              key={badge.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.02 }}
              onClick={() => setSelectedBadge(userBadge)}
              className="cursor-pointer"
            >
              <Card
                variant="bordered"
                padding="md"
                className={cn(
                  'text-center relative transition-all hover:scale-105',
                  is_unlocked ? rarityConfig.color : 'opacity-50 grayscale'
                )}
              >
                {/* Lock overlay */}
                {!is_unlocked && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/20 rounded-xl">
                    <Lock className="w-6 h-6 text-gray-400" />
                  </div>
                )}

                {/* Badge icon */}
                <div className="text-4xl mb-2">{badge.icon}</div>

                {/* Name */}
                <p className="font-semibold text-sm text-gray-900 dark:text-white truncate">
                  {badge.is_secret && !is_unlocked ? '???' : badge.name}
                </p>

                {/* Rarity */}
                <p className={cn('text-xs mt-1', rarityConfig.color.split(' ')[0])}>
                  {rarityConfig.label}
                </p>

                {/* Display indicator */}
                {displayedBadgeIds.includes(badge.id) && (
                  <div className="absolute top-1 right-1 w-5 h-5 bg-primary-500 rounded-full flex items-center justify-center">
                    <CheckCircle className="w-3 h-3 text-white" />
                  </div>
                )}
              </Card>
            </motion.div>
          );
        })}
      </div>

      {filteredBadges.length === 0 && (
        <div className="text-center py-12">
          <Award className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">Aucun badge trouvé</p>
        </div>
      )}

      {/* Badge Detail Modal */}
      <AnimatePresence>
        {selectedBadge && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedBadge(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <Card variant="elevated" padding="lg" className="w-full max-w-md bg-white dark:bg-gray-800">
                <div className="flex justify-between items-start mb-4">
                  <div className={cn(
                    'w-20 h-20 rounded-xl border-2 flex items-center justify-center text-4xl',
                    RARITY_CONFIG[selectedBadge.badge.rarity].color
                  )}>
                    {selectedBadge.badge.icon}
                  </div>
                  <button
                    onClick={() => setSelectedBadge(null)}
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <X className="w-5 h-5 text-gray-500" />
                  </button>
                </div>

                <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                  {selectedBadge.badge.is_secret && !selectedBadge.is_unlocked
                    ? 'Badge Secret'
                    : selectedBadge.badge.name}
                </h2>

                <UiBadge size="sm" className={cn('mt-2', RARITY_CONFIG[selectedBadge.badge.rarity].color)}>
                  {RARITY_CONFIG[selectedBadge.badge.rarity].label}
                </UiBadge>

                <p className="text-gray-500 dark:text-gray-400 mt-4">
                  {selectedBadge.badge.is_secret && !selectedBadge.is_unlocked
                    ? 'Débloque ce badge pour découvrir sa description !'
                    : selectedBadge.badge.description}
                </p>

                {selectedBadge.is_unlocked && (
                  <>
                    <div className="flex items-center gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                      <CheckCircle className="w-5 h-5 text-green-500" />
                      <span className="text-sm text-green-500">
                        Débloqué le {new Date(selectedBadge.unlocked_at!).toLocaleDateString('fr-FR')}
                      </span>
                    </div>

                    <p className="text-sm text-game-xp font-semibold mt-2">
                      +{selectedBadge.badge.xp_reward} XP gagnés
                    </p>

                    {/* Display toggle */}
                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                      <Button
                        variant={displayedBadgeIds.includes(selectedBadge.badge.id) ? 'secondary' : 'primary'}
                        onClick={() => toggleDisplay(selectedBadge.badge.id)}
                        disabled={!displayedBadgeIds.includes(selectedBadge.badge.id) && displayedBadgeIds.length >= 3}
                        className="w-full"
                      >
                        {displayedBadgeIds.includes(selectedBadge.badge.id)
                          ? 'Retirer du profil'
                          : displayedBadgeIds.length >= 3
                          ? 'Maximum 3 badges affichés'
                          : 'Afficher sur le profil'}
                      </Button>
                    </div>
                  </>
                )}

                {!selectedBadge.is_unlocked && (
                  <div className="flex items-center gap-2 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <Lock className="w-5 h-5 text-gray-400" />
                    <span className="text-sm text-gray-400">Badge verrouillé</span>
                  </div>
                )}
              </Card>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Save button if displayed badges changed */}
      {displayedBadgeIds.length > 0 && (
        <div className="fixed bottom-4 right-4">
          <Button onClick={saveDisplayedBadges} disabled={isSaving}>
            {isSaving ? (
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <CheckCircle className="w-4 h-4 mr-2" />
            )}
            Sauvegarder les badges affichés
          </Button>
        </div>
      )}
    </div>
  );
}
