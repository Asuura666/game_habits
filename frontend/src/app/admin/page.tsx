'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { Button } from '@/components/ui';
import { Input } from '@/components/ui';
import { Badge } from '@/components/ui';
import { Shield, Package, Users, Palette, Plus, Pencil, Trash2, RefreshCw, Save, X } from 'lucide-react';
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
}

const CATEGORIES = ['weapon', 'armor', 'helmet', 'accessory'];
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
  const [activeTab, setActiveTab] = useState('items');
  const [editingItem, setEditingItem] = useState<Item | null>(null);
  const [filterCategory, setFilterCategory] = useState('all');
  const [showForm, setShowForm] = useState(false);

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
      setShowForm(false);
      setEditingItem(null);
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

  const filteredItems = filterCategory === 'all' 
    ? items 
    : items.filter(i => i.category === filterCategory);

  // LOGIN SCREEN
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <Card className="w-full max-w-md bg-gray-800 border-gray-700">
          <CardHeader className="text-center">
            <Shield className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
            <CardTitle className="text-white">Admin HabitQuest</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              type="password"
              placeholder="Mot de passe"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
              className="bg-gray-700 border-gray-600"
            />
            <Button onClick={handleLogin} className="w-full">Connexion</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
          <div className="flex items-center gap-4">
            <Shield className="w-8 h-8 text-yellow-500" />
            <h1 className="text-2xl font-bold text-white">Admin HabitQuest</h1>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary" onClick={fetchItems} disabled={loading}>
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Actualiser
            </Button>
            <Button variant="ghost" onClick={() => { localStorage.removeItem('admin_auth'); setIsAuthenticated(false); }}>
              Déconnexion
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {[
            { id: 'items', label: 'Items', icon: Package, count: items.length },
            { id: 'classes', label: 'Classes', icon: Users },
            { id: 'appearances', label: 'Apparences', icon: Palette },
          ].map((tab) => (
            <Button
              key={tab.id}
              variant={activeTab === tab.id ? 'primary' : 'ghost'}
              onClick={() => setActiveTab(tab.id)}
              className="flex items-center gap-2"
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
              {tab.count && <Badge className="ml-1">{tab.count}</Badge>}
            </Button>
          ))}
        </div>

        {/* ITEMS TAB */}
        {activeTab === 'items' && (
          <div className="space-y-6">
            {/* Filters */}
            <div className="flex flex-wrap gap-4 items-center justify-between">
              <div className="flex gap-2 flex-wrap">
                <Button
                  variant={filterCategory === 'all' ? 'primary' : 'ghost'}
                  size="sm"
                  onClick={() => setFilterCategory('all')}
                >
                  Tous
                </Button>
                {CATEGORIES.map(cat => (
                  <Button
                    key={cat}
                    variant={filterCategory === cat ? 'primary' : 'ghost'}
                    size="sm"
                    onClick={() => setFilterCategory(cat)}
                  >
                    {cat}
                  </Button>
                ))}
              </div>
              
              <Button onClick={() => { setEditingItem(null); setShowForm(true); }}>
                <Plus className="w-4 h-4 mr-2" />
                Nouvel Item
              </Button>
            </div>

            {/* Item Form */}
            {showForm && (
              <ItemForm
                item={editingItem}
                onSave={saveItem}
                onCancel={() => { setShowForm(false); setEditingItem(null); }}
              />
            )}

            {/* Items Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredItems.map((item) => (
                <Card key={item.id} className="bg-gray-800 border-gray-700">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h3 className="font-semibold text-white text-sm truncate">{item.name}</h3>
                        <div className="flex gap-1 mt-1">
                          <Badge className="text-xs">{item.category}</Badge>
                          <Badge className={`${RARITY_COLORS[item.rarity]} text-xs`}>{item.rarity}</Badge>
                        </div>
                      </div>
                      <span className="text-yellow-500 font-bold text-sm">{item.price}g</span>
                    </div>
                    
                    {item.sprite_url && (
                      <div className="bg-gray-900 rounded-lg p-2 mb-2 flex justify-center h-20">
                        <img 
                          src={item.sprite_url} 
                          alt={item.name}
                          className="h-full object-contain"
                          style={{ imageRendering: 'pixelated' }}
                        />
                      </div>
                    )}
                    
                    <p className="text-gray-400 text-xs mb-2 line-clamp-2">{item.description}</p>
                    
                    <div className="flex justify-end gap-1">
                      <Button size="sm" variant="ghost" onClick={() => { setEditingItem(item); setShowForm(true); }}>
                        <Pencil className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="ghost" className="text-red-500" onClick={() => deleteItem(item.id)}>
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* CLASSES TAB */}
        {activeTab === 'classes' && <ClassesTab />}

        {/* APPEARANCES TAB */}
        {activeTab === 'appearances' && <AppearancesTab />}
      </div>
    </div>
  );
}

// Item Form Component
function ItemForm({ item, onSave, onCancel }: { 
  item: Item | null; 
  onSave: (item: Partial<Item>) => void;
  onCancel: () => void;
}) {
  const [form, setForm] = useState<Partial<Item>>(item || {
    name: '', description: '', category: 'weapon', rarity: 'common',
    price: 100, strength_bonus: 0, endurance_bonus: 0, agility_bonus: 0,
    intelligence_bonus: 0, charisma_bonus: 0, sprite_url: '',
  });

  return (
    <Card className="bg-gray-800 border-gray-700">
      <CardHeader>
        <CardTitle className="text-white flex items-center justify-between">
          {item ? 'Modifier Item' : 'Nouvel Item'}
          <Button variant="ghost" size="sm" onClick={onCancel}><X className="w-4 h-4" /></Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="text-sm text-gray-400">Nom</label>
            <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="bg-gray-700" />
          </div>
          <div>
            <label className="text-sm text-gray-400">Prix</label>
            <Input type="number" value={form.price} onChange={(e) => setForm({ ...form, price: +e.target.value })} className="bg-gray-700" />
          </div>
          <div>
            <label className="text-sm text-gray-400">Catégorie</label>
            <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="w-full p-2 bg-gray-700 border border-gray-600 rounded-md text-white">
              {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="text-sm text-gray-400">Rareté</label>
            <select value={form.rarity} onChange={(e) => setForm({ ...form, rarity: e.target.value })} className="w-full p-2 bg-gray-700 border border-gray-600 rounded-md text-white">
              {RARITIES.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>
        </div>
        
        <div>
          <label className="text-sm text-gray-400">Description</label>
          <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full p-2 bg-gray-700 border border-gray-600 rounded-md text-white" rows={2} />
        </div>
        
        <div>
          <label className="text-sm text-gray-400">URL Sprite</label>
          <Input value={form.sprite_url} onChange={(e) => setForm({ ...form, sprite_url: e.target.value })} placeholder="/sprites/shop/..." className="bg-gray-700" />
        </div>
        
        <div className="grid grid-cols-5 gap-2">
          {[
            { key: 'strength_bonus', label: 'STR' },
            { key: 'endurance_bonus', label: 'END' },
            { key: 'agility_bonus', label: 'AGI' },
            { key: 'intelligence_bonus', label: 'INT' },
            { key: 'charisma_bonus', label: 'CHA' },
          ].map(stat => (
            <div key={stat.key}>
              <label className="text-xs text-gray-400">{stat.label}</label>
              <Input type="number" value={(form as any)[stat.key]} onChange={(e) => setForm({ ...form, [stat.key]: +e.target.value })} className="bg-gray-700" />
            </div>
          ))}
        </div>
        
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onCancel}>Annuler</Button>
          <Button onClick={() => onSave(form)}><Save className="w-4 h-4 mr-2" />Sauvegarder</Button>
        </div>
      </CardContent>
    </Card>
  );
}

// Classes Tab
function ClassesTab() {
  const classes = [
    { id: 'warrior', name: 'Guerrier', gender: 'male', armor: 'plate', bonus: '+20% XP tâches' },
    { id: 'mage', name: 'Mage', gender: 'female', armor: 'robe', bonus: '+20% pièces' },
    { id: 'ranger', name: 'Rôdeur', gender: 'male', armor: 'leather', bonus: '+20% XP habitudes' },
    { id: 'paladin', name: 'Paladin', gender: 'male', armor: 'plate', bonus: '+10% tout XP' },
    { id: 'assassin', name: 'Assassin', gender: 'female', armor: 'leather', bonus: '+30% streak' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Classes de personnage</h2>
        <Button><Plus className="w-4 h-4 mr-2" /> Nouvelle classe</Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {classes.map((cls) => (
          <Card key={cls.id} className="bg-gray-800 border-gray-700">
            <CardContent className="p-6 flex items-center gap-4">
              <LPCCharacter characterClass={cls.id} gender={cls.gender as any} level={10} size="lg" />
              <div>
                <h3 className="font-bold text-white text-lg">{cls.name}</h3>
                <p className="text-sm text-gray-400">Genre: {cls.gender}</p>
                <p className="text-sm text-gray-400">Armure: {cls.armor}</p>
                <Badge className="mt-2">{cls.bonus}</Badge>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// Appearances Tab
function AppearancesTab() {
  const skins = [
    { name: 'Peau claire', sprite: '/sprites/shop/bodies/male_light.png' },
    { name: 'Peau foncée', sprite: '/sprites/shop/bodies/male_dark.png' },
    { name: 'Peau bronzée', sprite: '/sprites/shop/bodies/male_tanned.png' },
  ];

  const hairStyles = [
    { name: 'Cheveux courts', sprite: '/sprites/shop/hair/bangsshort_black_m.png' },
    { name: 'Cheveux longs', sprite: '/sprites/shop/hair/bangslong_black_m.png' },
    { name: 'Queue de cheval', sprite: '/sprites/shop/hair/ponytail_black_f.png' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white mb-4">Couleurs de peau</h2>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
          {skins.map((skin, i) => (
            <Card key={i} className="bg-gray-800 border-gray-700">
              <CardContent className="p-4 text-center">
                <div className="w-16 h-16 mx-auto bg-gray-900 rounded-lg overflow-hidden mb-2">
                  <img src={skin.sprite} alt={skin.name} className="w-full h-full object-cover" style={{ imageRendering: 'pixelated', objectPosition: '0 -128px' }} />
                </div>
                <p className="text-sm text-white">{skin.name}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-xl font-bold text-white mb-4">Coiffures</h2>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
          {hairStyles.map((hair, i) => (
            <Card key={i} className="bg-gray-800 border-gray-700">
              <CardContent className="p-4 text-center">
                <div className="w-16 h-16 mx-auto bg-gray-900 rounded-lg overflow-hidden mb-2">
                  <img src={hair.sprite} alt={hair.name} className="w-full h-full object-cover" style={{ imageRendering: 'pixelated', objectPosition: '0 -128px' }} />
                </div>
                <p className="text-sm text-white">{hair.name}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
