'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { Button } from '@/components/ui';
import { Input } from '@/components/ui';
import { Badge } from '@/components/ui';
import { 
  Shield, Package, Palette, Users, Plus, Pencil, Trash2, 
  RefreshCw, Save, X, Search, Filter, Image as ImageIcon,
  ChevronDown, ChevronUp, Eye
} from 'lucide-react';
import { SpriteExplorer } from './components/SpriteExplorer';
import { LPCCharacter } from '@/components/character/LPCCharacter';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://habit.apps.ilanewep.cloud/api';
const ADMIN_PASSWORD = 'HabitAdmin2026!';

interface Item {
  id: string;
  name: string;
  description: string;
  category: string;
  rarity: string;
  price: number;
  strength_bonus: number;
  endurance_bonus: number;
  agility_bonus: number;
  intelligence_bonus: number;
  charisma_bonus: number;
  sprite_url: string;
  is_available: boolean;
  required_level: number;
}

const CATEGORIES = ['weapon', 'armor', 'helmet', 'shield', 'accessory', 'cape', 'hair', 'body'];
const RARITIES = ['common', 'uncommon', 'rare', 'epic', 'legendary'];
const RARITY_COLORS: Record<string, string> = {
  common: 'bg-gray-500',
  uncommon: 'bg-green-500',
  rare: 'bg-blue-500',
  epic: 'bg-purple-500',
  legendary: 'bg-yellow-500',
};

export default function AdminPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'items' | 'sprites' | 'classes' | 'appearances'>('items');
  const [showItemForm, setShowItemForm] = useState(false);
  const [editingItem, setEditingItem] = useState<Item | null>(null);
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterRarity, setFilterRarity] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSpriteForItem, setSelectedSpriteForItem] = useState<{name: string; url: string; localPath: string} | null>(null);

  useEffect(() => {
    const auth = localStorage.getItem('admin_auth');
    if (auth === 'true') {
      setIsAuthenticated(true);
      fetchItems();
    }
  }, []);

  const handleLogin = () => {
    if (password === ADMIN_PASSWORD) {
      localStorage.setItem('admin_auth', 'true');
      setIsAuthenticated(true);
      fetchItems();
    } else {
      alert('Mot de passe incorrect');
    }
  };

  const fetchItems = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/shop/items`);
      const data = await res.json();
      setItems(Array.isArray(data) ? data : data.items || []);
    } catch (err) {
      console.error('Error:', err);
    }
    setLoading(false);
  };

  const saveItem = async (item: Partial<Item>) => {
    try {
      const method = item.id ? 'PUT' : 'POST';
      const url = item.id ? `${API_URL}/admin/items/${item.id}` : `${API_URL}/admin/items`;
      
      await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item),
      });
      
      fetchItems();
      setShowItemForm(false);
      setEditingItem(null);
      setSelectedSpriteForItem(null);
    } catch (err) {
      console.error('Error:', err);
    }
  };

  const deleteItem = async (id: string) => {
    if (!confirm('Supprimer cet item ?')) return;
    try {
      await fetch(`${API_URL}/admin/items/${id}`, { method: 'DELETE' });
      fetchItems();
    } catch (err) {
      console.error('Error:', err);
    }
  };

  // Filtrer les items
  const filteredItems = items.filter(item => {
    if (filterCategory !== 'all' && item.category !== filterCategory) return false;
    if (filterRarity !== 'all' && item.rarity !== filterRarity) return false;
    if (searchQuery && !item.name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  // Handler quand on sélectionne un sprite dans l'explorateur
  const handleSpriteSelect = (sprite: {name: string; url: string; localPath: string}) => {
    setSelectedSpriteForItem(sprite);
    setShowItemForm(true);
    setEditingItem(null);
  };

  // LOGIN SCREEN
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
        <Card className="w-full max-w-md bg-gray-800/50 border-gray-700 backdrop-blur">
          <CardHeader className="text-center">
            <Shield className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
            <CardTitle className="text-2xl text-white">Admin HabitQuest</CardTitle>
            <p className="text-gray-400 mt-2">Gestion des personnages et de la boutique</p>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              type="password"
              placeholder="Mot de passe admin"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
              className="bg-gray-700 border-gray-600 text-center text-lg"
            />
            <Button onClick={handleLogin} className="w-full h-12 text-lg">
              <Shield className="w-5 h-5 mr-2" />
              Connexion
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Header */}
      <header className="bg-gray-800/50 border-b border-gray-700 sticky top-0 z-50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-yellow-500" />
            <h1 className="text-xl font-bold text-white">Admin HabitQuest</h1>
          </div>
          <div className="flex items-center gap-3">
            <Badge className="bg-green-600">{items.length} items</Badge>
            <Button variant="ghost" size="sm" onClick={fetchItems} disabled={loading}>
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => { localStorage.removeItem('admin_auth'); setIsAuthenticated(false); }}>
              Déconnexion
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-gray-700 pb-4">
          {[
            { id: 'items', label: 'Items Boutique', icon: Package },
            { id: 'sprites', label: 'Explorateur Sprites', icon: ImageIcon },
            { id: 'classes', label: 'Classes', icon: Users },
            { id: 'appearances', label: 'Apparences', icon: Palette },
          ].map((tab) => (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? 'primary' : 'ghost'}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 ${activeTab === tab.id ? '' : 'text-gray-400'}`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </Button>
          ))}
        </div>

        {/* TAB: ITEMS */}
        {activeTab === 'items' && (
          <div className="space-y-6">
            {/* Toolbar */}
            <div className="flex flex-wrap gap-4 items-center justify-between bg-gray-800/50 rounded-lg p-4">
              <div className="flex gap-3 items-center flex-wrap">
                {/* Search */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input
                    placeholder="Rechercher..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 w-48 bg-gray-700 border-gray-600"
                  />
                </div>
                
                {/* Filter Category */}
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                >
                  <option value="all">Toutes catégories</option>
                  {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
                
                {/* Filter Rarity */}
                <select
                  value={filterRarity}
                  onChange={(e) => setFilterRarity(e.target.value)}
                  className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                >
                  <option value="all">Toutes raretés</option>
                  {RARITIES.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
              
              <Button onClick={() => { setEditingItem(null); setSelectedSpriteForItem(null); setShowItemForm(true); }}>
                <Plus className="w-4 h-4 mr-2" />
                Nouvel Item
              </Button>
            </div>

            {/* Item Form */}
            {showItemForm && (
              <ItemForm
                item={editingItem}
                initialSprite={selectedSpriteForItem}
                onSave={saveItem}
                onCancel={() => { setShowItemForm(false); setEditingItem(null); setSelectedSpriteForItem(null); }}
                onBrowseSprites={() => setActiveTab('sprites')}
              />
            )}

            {/* Items Table */}
            <div className="bg-gray-800/50 rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-700/50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Sprite</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Nom</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Catégorie</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Rareté</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Prix</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Stats</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {filteredItems.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-700/30">
                      <td className="px-4 py-3">
                        {item.sprite_url && (
                          <div className="w-12 h-12 bg-gray-900 rounded overflow-hidden">
                            <img
                              src={item.sprite_url}
                              alt={item.name}
                              className="w-full h-full object-contain"
                              style={{ imageRendering: 'pixelated' }}
                            />
                          </div>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <p className="text-white font-medium">{item.name}</p>
                        <p className="text-xs text-gray-400 truncate max-w-xs">{item.description}</p>
                      </td>
                      <td className="px-4 py-3">
                        <Badge className="bg-gray-600">{item.category}</Badge>
                      </td>
                      <td className="px-4 py-3">
                        <Badge className={RARITY_COLORS[item.rarity]}>{item.rarity}</Badge>
                      </td>
                      <td className="px-4 py-3 text-yellow-500 font-bold">{item.price}g</td>
                      <td className="px-4 py-3 text-xs text-gray-400">
                        {item.strength_bonus > 0 && <span className="mr-2">STR+{item.strength_bonus}</span>}
                        {item.endurance_bonus > 0 && <span className="mr-2">END+{item.endurance_bonus}</span>}
                        {item.agility_bonus > 0 && <span className="mr-2">AGI+{item.agility_bonus}</span>}
                        {item.intelligence_bonus > 0 && <span className="mr-2">INT+{item.intelligence_bonus}</span>}
                        {item.charisma_bonus > 0 && <span>CHA+{item.charisma_bonus}</span>}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <Button size="sm" variant="ghost" onClick={() => { setEditingItem(item); setShowItemForm(true); }}>
                          <Pencil className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="ghost" className="text-red-500" onClick={() => deleteItem(item.id)}>
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {filteredItems.length === 0 && (
                <div className="text-center py-12 text-gray-400">
                  Aucun item trouvé
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB: SPRITES EXPLORER */}
        {activeTab === 'sprites' && (
          <SpriteExplorer onSelectSprite={handleSpriteSelect} />
        )}

        {/* TAB: CLASSES */}
        {activeTab === 'classes' && <ClassesTab />}

        {/* TAB: APPEARANCES */}
        {activeTab === 'appearances' && <AppearancesTab />}
      </div>
    </div>
  );
}

// ============ ITEM FORM ============
function ItemForm({ 
  item, 
  initialSprite,
  onSave, 
  onCancel,
  onBrowseSprites 
}: { 
  item: Item | null; 
  initialSprite: {name: string; url: string; localPath: string} | null;
  onSave: (item: Partial<Item>) => void;
  onCancel: () => void;
  onBrowseSprites: () => void;
}) {
  const [form, setForm] = useState<Partial<Item>>(() => {
    if (item) return item;
    return {
      name: initialSprite?.name || '',
      description: '',
      category: 'weapon',
      rarity: 'common',
      price: 100,
      strength_bonus: 0,
      endurance_bonus: 0,
      agility_bonus: 0,
      intelligence_bonus: 0,
      charisma_bonus: 0,
      sprite_url: initialSprite?.url || initialSprite?.localPath || '',
      required_level: 1,
    };
  });

  return (
    <Card className="bg-gray-800 border-gray-700">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-white">{item ? 'Modifier Item' : 'Nouvel Item'}</CardTitle>
        <Button variant="ghost" size="sm" onClick={onCancel}><X className="w-4 h-4" /></Button>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Left: Sprite preview */}
          <div className="space-y-4">
            <div className="bg-gray-900 rounded-lg p-6 flex flex-col items-center">
              {form.sprite_url ? (
                <img
                  src={form.sprite_url}
                  alt="Preview"
                  className="w-32 h-32 object-contain mb-4"
                  style={{ imageRendering: 'pixelated' }}
                />
              ) : (
                <div className="w-32 h-32 bg-gray-800 rounded-lg flex items-center justify-center mb-4">
                  <ImageIcon className="w-12 h-12 text-gray-600" />
                </div>
              )}
              <Button variant="secondary" onClick={onBrowseSprites}>
                <ImageIcon className="w-4 h-4 mr-2" />
                Choisir un sprite
              </Button>
            </div>
            
            <div>
              <label className="text-sm text-gray-400">URL Sprite (ou chemin local)</label>
              <Input
                value={form.sprite_url}
                onChange={(e) => setForm({ ...form, sprite_url: e.target.value })}
                placeholder="/sprites/... ou https://..."
                className="bg-gray-700 border-gray-600 mt-1"
              />
            </div>
          </div>

          {/* Right: Form fields */}
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-gray-400">Nom</label>
                <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="bg-gray-700 border-gray-600 mt-1" />
              </div>
              <div>
                <label className="text-sm text-gray-400">Prix (gold)</label>
                <Input type="number" value={form.price} onChange={(e) => setForm({ ...form, price: +e.target.value })} className="bg-gray-700 border-gray-600 mt-1" />
              </div>
            </div>

            <div>
              <label className="text-sm text-gray-400">Description</label>
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                className="w-full mt-1 p-2 bg-gray-700 border border-gray-600 rounded-md text-white"
                rows={2}
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="text-sm text-gray-400">Catégorie</label>
                <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="w-full mt-1 p-2 bg-gray-700 border border-gray-600 rounded-md text-white">
                  {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label className="text-sm text-gray-400">Rareté</label>
                <select value={form.rarity} onChange={(e) => setForm({ ...form, rarity: e.target.value })} className="w-full mt-1 p-2 bg-gray-700 border border-gray-600 rounded-md text-white">
                  {RARITIES.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
              <div>
                <label className="text-sm text-gray-400">Niveau requis</label>
                <Input type="number" value={form.required_level} onChange={(e) => setForm({ ...form, required_level: +e.target.value })} className="bg-gray-700 border-gray-600 mt-1" />
              </div>
            </div>

            <div>
              <label className="text-sm text-gray-400 mb-2 block">Bonus de stats</label>
              <div className="grid grid-cols-5 gap-2">
                {[
                  { key: 'strength_bonus', label: 'STR', color: 'text-red-400' },
                  { key: 'endurance_bonus', label: 'END', color: 'text-green-400' },
                  { key: 'agility_bonus', label: 'AGI', color: 'text-blue-400' },
                  { key: 'intelligence_bonus', label: 'INT', color: 'text-purple-400' },
                  { key: 'charisma_bonus', label: 'CHA', color: 'text-yellow-400' },
                ].map(stat => (
                  <div key={stat.key} className="text-center">
                    <label className={`text-xs ${stat.color}`}>{stat.label}</label>
                    <Input
                      type="number"
                      value={(form as any)[stat.key]}
                      onChange={(e) => setForm({ ...form, [stat.key]: +e.target.value })}
                      className="bg-gray-700 border-gray-600 mt-1 text-center"
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-gray-700">
          <Button variant="ghost" onClick={onCancel}>Annuler</Button>
          <Button onClick={() => onSave(form)}>
            <Save className="w-4 h-4 mr-2" />
            Sauvegarder
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// ============ CLASSES TAB ============
function ClassesTab() {
  const classes = [
    { id: 'warrior', name: 'Guerrier', gender: 'male', bonus: '+20% XP tâches', color: 'red' },
    { id: 'mage', name: 'Mage', gender: 'female', bonus: '+20% pièces', color: 'purple' },
    { id: 'ranger', name: 'Rôdeur', gender: 'male', bonus: '+20% XP habitudes', color: 'green' },
    { id: 'paladin', name: 'Paladin', gender: 'male', bonus: '+10% tout XP', color: 'yellow' },
    { id: 'assassin', name: 'Assassin', gender: 'female', bonus: '+30% streak', color: 'pink' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Classes de personnage</h2>
        <Button><Plus className="w-4 h-4 mr-2" />Nouvelle classe</Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {classes.map((cls) => (
          <Card key={cls.id} className="bg-gray-800/50 border-gray-700">
            <CardContent className="p-6 flex items-center gap-4">
              <LPCCharacter characterClass={cls.id} gender={cls.gender as any} level={10} size="xl" />
              <div className="flex-1">
                <h3 className="font-bold text-white text-lg">{cls.name}</h3>
                <p className="text-sm text-gray-400">ID: {cls.id}</p>
                <Badge className="mt-2 bg-gray-600">{cls.bonus}</Badge>
              </div>
              <Button size="sm" variant="ghost"><Pencil className="w-4 h-4" /></Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// ============ APPEARANCES TAB ============
function AppearancesTab() {
  return (
    <div className="space-y-8">
      <div className="text-center py-12 text-gray-400">
        <Palette className="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>Gestion des apparences à venir</p>
        <p className="text-sm mt-2">Utilise l'explorateur de sprites pour voir toutes les options disponibles</p>
      </div>
    </div>
  );
}
