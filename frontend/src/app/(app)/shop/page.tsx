'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShoppingBag, Coins, Sword, Shield, Sparkles, Shirt, Gem, Check } from 'lucide-react';
import { Card, Button, Badge } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import { cn, getRarityColor } from '@/lib/utils';
import type { ShopItem } from '@/types';

const shopItems: (ShopItem & { rarity: string })[] = [
  {
    id: '1',
    name: 'Épée Légendaire',
    description: '+15 Force, +5% critique',
    price: 500,
    type: 'equipment',
    rarity: 'legendary',
  },
  {
    id: '2',
    name: 'Bouclier du Gardien',
    description: '+20 Défense, +50 PV max',
    price: 350,
    type: 'equipment',
    rarity: 'epic',
  },
  {
    id: '3',
    name: 'Potion de Soin',
    description: 'Restaure 50 PV',
    price: 25,
    type: 'consumable',
    rarity: 'common',
  },
  {
    id: '4',
    name: 'Élixir de Mana',
    description: 'Restaure 30 Mana',
    price: 30,
    type: 'consumable',
    rarity: 'common',
  },
  {
    id: '5',
    name: 'Cape du Voyageur',
    description: 'Look unique pour votre avatar',
    price: 200,
    type: 'cosmetic',
    rarity: 'rare',
  },
  {
    id: '6',
    name: 'Aura Dorée',
    description: 'Effet visuel spécial',
    price: 750,
    type: 'cosmetic',
    rarity: 'legendary',
  },
  {
    id: '7',
    name: 'Boost XP x2',
    description: 'Double XP pendant 24h',
    price: 100,
    type: 'consumable',
    rarity: 'rare',
  },
  {
    id: '8',
    name: 'Anneau de Sagesse',
    description: '+10 Intelligence',
    price: 250,
    type: 'equipment',
    rarity: 'uncommon',
  },
];

const typeIcons = {
  equipment: Sword,
  consumable: Sparkles,
  cosmetic: Shirt,
};

const typeLabels = {
  equipment: 'Équipement',
  consumable: 'Consommable',
  cosmetic: 'Cosmétique',
};

export default function ShopPage() {
  const { user, updateUser } = useAuthStore();
  const [filter, setFilter] = useState<'all' | 'equipment' | 'consumable' | 'cosmetic'>('all');
  const [purchasedItems, setPurchasedItems] = useState<string[]>([]);
  const [purchasing, setPurchasing] = useState<string | null>(null);

  const filteredItems = shopItems.filter((item) => filter === 'all' || item.type === filter);

  const handlePurchase = async (item: ShopItem & { rarity: string }) => {
    if (!user || user.gold < item.price) return;

    setPurchasing(item.id);
    
    // Simulate purchase
    await new Promise((resolve) => setTimeout(resolve, 800));
    
    updateUser({ gold: user.gold - item.price });
    setPurchasedItems((prev) => [...prev, item.id]);
    setPurchasing(null);
  };

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
        <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-yellow-100 dark:bg-yellow-900/30">
          <Coins className="w-6 h-6 text-game-gold" />
          <span className="text-xl font-bold text-game-gold">{user?.gold || 0}</span>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {(['all', 'equipment', 'consumable', 'cosmetic'] as const).map((f) => {
          const Icon = f === 'all' ? ShoppingBag : typeIcons[f];
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
              {f === 'all' ? 'Tout' : typeLabels[f]}
            </button>
          );
        })}
      </div>

      {/* Items Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <AnimatePresence mode="popLayout">
          {filteredItems.map((item) => {
            const Icon = typeIcons[item.type];
            const isPurchased = purchasedItems.includes(item.id);
            const canAfford = (user?.gold || 0) >= item.price;
            const isPurchasing = purchasing === item.id;

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
                    isPurchased && 'opacity-60',
                    !canAfford && !isPurchased && 'opacity-75'
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
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
                      {item.description}
                    </p>

                    {/* Price & Buy */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1">
                        <Coins className="w-5 h-5 text-game-gold" />
                        <span className={cn(
                          'font-bold',
                          canAfford ? 'text-game-gold' : 'text-red-500'
                        )}>
                          {item.price}
                        </span>
                      </div>
                      
                      {isPurchased ? (
                        <Button size="sm" disabled className="gap-1">
                          <Check className="w-4 h-4" />
                          Acheté
                        </Button>
                      ) : (
                        <Button
                          size="sm"
                          onClick={() => handlePurchase(item)}
                          disabled={!canAfford || isPurchasing}
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

      {filteredItems.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400">
            Aucun article dans cette catégorie
          </p>
        </div>
      )}
    </div>
  );
}
