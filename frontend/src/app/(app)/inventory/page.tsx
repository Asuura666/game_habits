'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Package, 
  Sword, 
  Shield, 
  Sparkles, 
  Shirt, 
  Gem, 
  Check,
  X,
  Star,
  Loader2,
  ShoppingBag,
  TrendingUp
} from 'lucide-react';
import { Card, Button, Badge } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import { cn, getRarityColor } from '@/lib/utils';
import Link from 'next/link';

interface InventoryItem {
  id: string;
  item_id: string;
  name: string;
  description?: string;
  category: 'weapon' | 'armor' | 'accessory' | 'consumable' | 'cosmetic';
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  strength_bonus?: number;
  endurance_bonus?: number;
  intelligence_bonus?: number;
  charisma_bonus?: number;
  is_equipped: boolean;
  equipped_slot?: string;
}

interface InventoryResponse {
  items: InventoryItem[];
  total: number;
  equipped_count: number;
  total_stats_bonus: {
    strength: number;
    endurance: number;
    intelligence: number;
    charisma: number;
  };
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

const slotLabels: Record<string, string> = {
  weapon: 'Arme',
  armor: 'Armure',
  accessory: 'Accessoire',
  head: 'Tête',
  chest: 'Torse',
  legs: 'Jambes',
  feet: 'Pieds',
  hands: 'Mains',
};

export default function InventoryPage() {
  const { accessToken, fetchCharacter } = useAuthStore();
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'equipped' | 'unequipped'>('all');
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [totalStats, setTotalStats] = useState<InventoryResponse['total_stats_bonus']>({
    strength: 0,
    endurance: 0,
    intelligence: 0,
    charisma: 0,
  });
  const [equippedCount, setEquippedCount] = useState(0);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://habit.apps.ilanewep.cloud/api';

  const fetchInventory = useCallback(async () => {
    if (!accessToken) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/inventory/`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Erreur lors du chargement de l\'inventaire');
      }

      const data: InventoryResponse = await response.json();
      setItems(data.items);
      setTotalStats(data.total_stats_bonus);
      setEquippedCount(data.equipped_count);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  }, [accessToken, API_URL]);

  useEffect(() => {
    fetchInventory();
  }, [fetchInventory]);

  const handleEquip = async (item: InventoryItem) => {
    if (!accessToken) return;

    setActionLoading(item.id);
    
    try {
      const response = await fetch(`${API_URL}/inventory/equip/${item.id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de l\'équipement');
      }

      await fetchInventory();
      await fetchCharacter();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors de l\'équipement');
    } finally {
      setActionLoading(null);
    }
  };

  const handleUnequip = async (item: InventoryItem) => {
    if (!accessToken) return;

    setActionLoading(item.id);
    
    try {
      const response = await fetch(`${API_URL}/inventory/unequip/${item.id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors du déséquipement');
      }

      await fetchInventory();
      await fetchCharacter();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur lors du déséquipement');
    } finally {
      setActionLoading(null);
    }
  };

  const getStatBonuses = (item: InventoryItem): string[] => {
    const bonuses: string[] = [];
    if (item.strength_bonus) bonuses.push(`+${item.strength_bonus} Force`);
    if (item.endurance_bonus) bonuses.push(`+${item.endurance_bonus} Endurance`);
    if (item.intelligence_bonus) bonuses.push(`+${item.intelligence_bonus} Intelligence`);
    if (item.charisma_bonus) bonuses.push(`+${item.charisma_bonus} Charisme`);
    return bonuses;
  };

  const filteredItems = items.filter(item => {
    if (filter === 'equipped') return item.is_equipped;
    if (filter === 'unequipped') return !item.is_equipped;
    return true;
  });

  const equippedItems = items.filter(item => item.is_equipped);

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <Package className="w-8 h-8 text-primary-500" />
            Inventaire
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            {items.length} objet{items.length > 1 ? 's' : ''} • {equippedCount} équipé{equippedCount > 1 ? 's' : ''}
          </p>
        </div>
        <Link href="/shop">
          <Button variant="secondary" className="gap-2">
            <ShoppingBag className="w-5 h-5" />
            Boutique
          </Button>
        </Link>
      </div>

      {/* Stats Bonus Panel */}
      <Card className="bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border-indigo-500/20">
        <div className="flex items-center gap-3 mb-4">
          <TrendingUp className="w-6 h-6 text-indigo-400" />
          <h2 className="text-lg font-semibold text-white">Bonus d&apos;équipement</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 rounded-lg bg-red-500/10">
            <p className="text-2xl font-bold text-red-400">+{totalStats.strength}</p>
            <p className="text-sm text-gray-400">Force</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-green-500/10">
            <p className="text-2xl font-bold text-green-400">+{totalStats.endurance}</p>
            <p className="text-sm text-gray-400">Endurance</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-blue-500/10">
            <p className="text-2xl font-bold text-blue-400">+{totalStats.intelligence}</p>
            <p className="text-sm text-gray-400">Intelligence</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-purple-500/10">
            <p className="text-2xl font-bold text-purple-400">+{totalStats.charisma}</p>
            <p className="text-sm text-gray-400">Charisme</p>
          </div>
        </div>
      </Card>

      {/* Equipped Items Summary */}
      {equippedItems.length > 0 && (
        <Card>
          <div className="flex items-center gap-3 mb-4">
            <Star className="w-6 h-6 text-yellow-400" />
            <h2 className="text-lg font-semibold text-white">Équipement actuel</h2>
          </div>
          <div className="flex flex-wrap gap-3">
            {equippedItems.map(item => {
              const Icon = categoryIcons[item.category] || Gem;
              return (
                <div 
                  key={item.id}
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 rounded-lg border',
                    'bg-gradient-to-r from-indigo-500/10 to-purple-500/10 border-indigo-500/30'
                  )}
                >
                  <Icon className={cn('w-5 h-5', getRarityColor(item.rarity))} />
                  <span className={cn('font-medium', getRarityColor(item.rarity))}>
                    {item.name}
                  </span>
                  <Badge size="sm" variant="default">
                    {slotLabels[item.equipped_slot || item.category] || item.category}
                  </Badge>
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {(['all', 'equipped', 'unequipped'] as const).map((f) => {
          const labels = {
            all: 'Tout',
            equipped: 'Équipés',
            unequipped: 'Non équipés',
          };
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
              {labels[f]}
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
              {filteredItems.map((item) => {
                const Icon = categoryIcons[item.category] || Gem;
                const isLoading = actionLoading === item.id;
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
                        item.is_equipped && 'ring-2 ring-indigo-500'
                      )}
                    >
                      {/* Item Header */}
                      <div className={cn(
                        'p-4 bg-gradient-to-r relative',
                        item.rarity === 'legendary' && 'from-yellow-500/20 to-orange-500/20',
                        item.rarity === 'epic' && 'from-purple-500/20 to-pink-500/20',
                        item.rarity === 'rare' && 'from-blue-500/20 to-cyan-500/20',
                        item.rarity === 'uncommon' && 'from-green-500/20 to-emerald-500/20',
                        item.rarity === 'common' && 'from-gray-500/20 to-gray-400/20'
                      )}>
                        {item.is_equipped && (
                          <div className="absolute top-2 right-2">
                            <Badge variant="success" size="sm" className="gap-1">
                              <Check className="w-3 h-3" />
                              Équipé
                            </Badge>
                          </div>
                        )}
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
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                          {categoryLabels[item.category]}
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

                        {/* Actions */}
                        <div className="flex items-center justify-end gap-2">
                          {item.is_equipped ? (
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => handleUnequip(item)}
                              disabled={isLoading}
                              isLoading={isLoading}
                              className="gap-1"
                            >
                              <X className="w-4 h-4" />
                              Retirer
                            </Button>
                          ) : (
                            <Button
                              size="sm"
                              onClick={() => handleEquip(item)}
                              disabled={isLoading}
                              isLoading={isLoading}
                              className="gap-1"
                            >
                              <Check className="w-4 h-4" />
                              Équiper
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

          {filteredItems.length === 0 && !loading && (
            <div className="text-center py-12">
              <Package className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                {filter === 'all' 
                  ? 'Votre inventaire est vide'
                  : filter === 'equipped'
                  ? 'Aucun objet équipé'
                  : 'Tous vos objets sont équipés'}
              </p>
              <Link href="/shop">
                <Button className="gap-2">
                  <ShoppingBag className="w-5 h-5" />
                  Aller à la boutique
                </Button>
              </Link>
            </div>
          )}
        </>
      )}
    </div>
  );
}
