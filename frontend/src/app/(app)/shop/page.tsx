'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShoppingBag, 
  Coins, 
  Sword, 
  Shield, 
  Sparkles, 
  Shirt, 
  Gem, 
  Check,
  ChevronLeft,
  ChevronRight,
  Package,
  Loader2
} from 'lucide-react';
import { Card, Button, Badge } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import { cn, getRarityColor } from '@/lib/utils';
import Link from 'next/link';

interface ShopItemAPI {
  id: string;
  name: string;
  description: string;
  category: 'weapon' | 'armor' | 'accessory' | 'consumable' | 'cosmetic';
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  price: number;
  strength_bonus?: number;
  endurance_bonus?: number;
  intelligence_bonus?: number;
  charisma_bonus?: number;
  is_owned: boolean;
  can_afford: boolean;
}

interface ShopResponse {
  items: ShopItemAPI[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
}

const categoryIcons: Record<string, React.ElementType> = {
  weapon: Sword,
  armor: Shield,
  accessory: Sparkles,
  consumable: Sparkles,
  cosmetic: Shirt,
};

const categoryLabels: Record<string, string> = {
  weapon: 'Armes',
  armor: 'Armures',
  accessory: 'Accessoires',
  consumable: 'Consommables',
  cosmetic: 'Cosmétiques',
};

export default function ShopPage() {
  const { character, accessToken, fetchCharacter } = useAuthStore();
  const [items, setItems] = useState<ShopItemAPI[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'weapon' | 'armor' | 'accessory' | 'consumable' | 'cosmetic'>('all');
  const [purchasing, setPurchasing] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [hasNext, setHasNext] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://habit.apps.ilanewep.cloud/api';

  const fetchItems = useCallback(async () => {
    if (!accessToken) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const categoryParam = filter !== 'all' ? `&category=${filter}` : '';
      const response = await fetch(
        `${API_URL}/shop/items?page=${page}&per_page=20${categoryParam}`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Erreur lors du chargement de la boutique');
      }

      const data: ShopResponse = await response.json();
      setItems(data.items);
      setTotalPages(Math.ceil(data.total / data.per_page));
      setHasNext(data.has_next);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  }, [accessToken, filter, page, API_URL]);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  useEffect(() => {
    setPage(1);
  }, [filter]);

  const handlePurchase = async (item: ShopItemAPI) => {
    if (!accessToken || item.is_owned || !item.can_afford) return;

    setPurchasing(item.id);
    
    try {
      const response = await fetch(`${API_URL}/shop/buy/${item.id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de l\'achat');
      }

      // Refresh character to get updated coins
      await fetchCharacter();
      // Refresh items to update owned/can_afford status
      await fetchItems();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de l\'achat');
    } finally {
      setPurchasing(null);
    }
  };

  const getStatBonuses = (item: ShopItemAPI): string[] => {
    const bonuses: string[] = [];
    if (item.strength_bonus) bonuses.push(`+${item.strength_bonus} Force`);
    if (item.endurance_bonus) bonuses.push(`+${item.endurance_bonus} Endurance`);
    if (item.intelligence_bonus) bonuses.push(`+${item.intelligence_bonus} Intelligence`);
    if (item.charisma_bonus) bonuses.push(`+${item.charisma_bonus} Charisme`);
    return bonuses;
  };

  const userCoins = character?.coins ?? 0;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <ShoppingBag className="w-8 h-8 text-primary-500" />
            Boutique
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            Dépensez votre or durement gagné
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/inventory">
            <Button variant="secondary" className="gap-2">
              <Package className="w-5 h-5" />
              Mon Inventaire
            </Button>
          </Link>
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-yellow-100 dark:bg-yellow-900/30">
            <Coins className="w-6 h-6 text-game-gold" />
            <span className="text-xl font-bold text-game-gold">{userCoins}</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {(['all', 'weapon', 'armor', 'accessory', 'consumable', 'cosmetic'] as const).map((f) => {
          const Icon = f === 'all' ? ShoppingBag : categoryIcons[f];
          return (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
                filter === f
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              )}
            >
              <Icon className="w-4 h-4" />
              {f === 'all' ? 'Tout' : categoryLabels[f]}
            </button>
          );
        })}
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 p-4 rounded-lg">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        </div>
      ) : (
        <>
          {/* Items Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <AnimatePresence mode="popLayout">
              {items.map((item) => {
                const Icon = categoryIcons[item.category] || Gem;
                const isPurchasing = purchasing === item.id;
                const bonuses = getStatBonuses(item);

                return (
                  <motion.div
                    key={item.id}
                    layout
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                  >
                    <Card
                      variant="bordered"
                      padding="none"
                      className={cn(
                        'overflow-hidden transition-all',
                        item.is_owned && 'opacity-60',
                        !item.can_afford && !item.is_owned && 'opacity-75'
                      )}
                    >
                      {/* Item Header */}
                      <div className={cn(
                        'p-4 bg-gradient-to-r',
                        item.rarity === 'legendary' && 'from-yellow-500/20 to-orange-500/20',
                        item.rarity === 'epic' && 'from-purple-500/20 to-pink-500/20',
                        item.rarity === 'rare' && 'from-blue-500/20 to-cyan-500/20',
                        item.rarity === 'uncommon' && 'from-green-500/20 to-emerald-500/20',
                        item.rarity === 'common' && 'from-gray-500/20 to-gray-400/20'
                      )}>
                        <div className="flex items-center justify-between mb-2">
                          <Badge size="sm" variant={item.rarity === 'legendary' ? 'warning' : 'default'}>
                            {item.rarity}
                          </Badge>
                          <Icon className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                        </div>
                        <div className="w-16 h-16 rounded-xl bg-gray-800/50 flex items-center justify-center mx-auto">
                          <Gem className={cn('w-8 h-8', getRarityColor(item.rarity))} />
                        </div>
                      </div>

                      {/* Item Info */}
                      <div className="p-4">
                        <h3 className={cn('font-semibold mb-1', getRarityColor(item.rarity))}>
                          {item.name}
                        </h3>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                          {item.description}
                        </p>
                        
                        {/* Stat Bonuses */}
                        {bonuses.length > 0 && (
                          <div className="flex flex-wrap gap-1 mb-3">
                            {bonuses.map((bonus, i) => (
                              <span 
                                key={i}
                                className="text-xs bg-primary-500/20 text-primary-400 px-2 py-0.5 rounded"
                              >
                                {bonus}
                              </span>
                            ))}
                          </div>
                        )}

                        {/* Price & Buy */}
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-1">
                            <Coins className="w-5 h-5 text-game-gold" />
                            <span className={cn(
                              'font-bold',
                              item.can_afford ? 'text-game-gold' : 'text-red-500'
                            )}>
                              {item.price}
                            </span>
                          </div>
                          
                          {item.is_owned ? (
                            <Button size="sm" disabled className="gap-1">
                              <Check className="w-4 h-4" />
                              Possédé
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              onClick={() => handlePurchase(item)}
                              disabled={!item.can_afford || isPurchasing}
                              isLoading={isPurchasing}
                            >
                              Acheter
                            </Button>
                          )}
                        </div>
                      </div>
                    </Card>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>

          {items.length === 0 && !loading && (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">
                Aucun article dans cette catégorie
              </p>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-4">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                <ChevronLeft className="w-4 h-4" />
                Précédent
              </Button>
              <span className="text-gray-500 dark:text-gray-400">
                Page {page} / {totalPages}
              </span>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage(p => p + 1)}
                disabled={!hasNext}
              >
                Suivant
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
