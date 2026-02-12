'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui';
import { Button } from '@/components/ui';
import { Input } from '@/components/ui';
import { Badge } from '@/components/ui';
import { ChevronRight, Plus, Search, Loader2, FolderOpen, ArrowLeft, Swords, User, Shirt, CircleUser } from 'lucide-react';

const GITHUB_REPO = 'LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator';
const GITHUB_API = `https://api.github.com/repos/${GITHUB_REPO}/contents`;
const GITHUB_RAW = `https://raw.githubusercontent.com/${GITHUB_REPO}/master`;

// Catégories principales comme dans le générateur
const CATEGORIES = [
  { id: 'body', name: 'Corps', icon: User, color: 'bg-orange-500' },
  { id: 'hair', name: 'Cheveux', icon: CircleUser, color: 'bg-yellow-500' },
  { id: 'torso', name: 'Torse', icon: Shirt, color: 'bg-blue-500' },
  { id: 'legs', name: 'Jambes', icon: User, color: 'bg-green-500' },
  { id: 'feet', name: 'Pieds', icon: User, color: 'bg-purple-500' },
  { id: 'head', name: 'Tête', icon: CircleUser, color: 'bg-pink-500' },
  { id: 'weapons', name: 'Armes', icon: Swords, color: 'bg-red-500' },
  { id: 'arms', name: 'Bras', icon: User, color: 'bg-cyan-500' },
];

interface ItemDefinition {
  name: string;
  fileName: string;
  category: string;
  subcategory?: string;
  spritePath: string;
  previewUrl: string;
  variants?: string[];
}

interface SpriteExplorerProps {
  onSelectSprite: (sprite: { name: string; url: string; localPath: string }) => void;
}

export function SpriteExplorer({ onSelectSprite }: SpriteExplorerProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [subcategories, setSubcategories] = useState<string[]>([]);
  const [selectedSubcategory, setSelectedSubcategory] = useState<string | null>(null);
  const [items, setItems] = useState<ItemDefinition[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedItem, setSelectedItem] = useState<ItemDefinition | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [allItems, setAllItems] = useState<ItemDefinition[]>([]);

  // Charger les sous-catégories d'une catégorie
  const loadCategory = async (categoryId: string) => {
    setLoading(true);
    setError(null);
    setSelectedCategory(categoryId);
    setSelectedSubcategory(null);
    setItems([]);
    setSelectedItem(null);
    
    try {
      const url = `${GITHUB_API}/sheet_definitions/${categoryId}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Erreur ${res.status}`);
      const data = await res.json();
      
      // Filtrer pour avoir les dossiers (sous-catégories) et fichiers JSON
      const folders = data.filter((f: any) => f.type === 'dir').map((f: any) => f.name);
      const jsonFiles = data.filter((f: any) => f.name.endsWith('.json') && !f.name.startsWith('meta_'));
      
      setSubcategories(folders);
      
      // Si pas de sous-dossiers, charger directement les items JSON
      if (folders.length === 0 && jsonFiles.length > 0) {
        await loadItemsFromJsonList(categoryId, '', jsonFiles);
      }
    } catch (err: any) {
      setError(err.message);
    }
    setLoading(false);
  };

  // Charger les items d'une sous-catégorie
  const loadSubcategory = async (subcategory: string) => {
    setLoading(true);
    setError(null);
    setSelectedSubcategory(subcategory);
    setItems([]);
    setSelectedItem(null);
    
    try {
      const url = `${GITHUB_API}/sheet_definitions/${selectedCategory}/${subcategory}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Erreur ${res.status}`);
      const data = await res.json();
      
      const jsonFiles = data.filter((f: any) => f.name.endsWith('.json') && !f.name.startsWith('meta_'));
      await loadItemsFromJsonList(selectedCategory!, subcategory, jsonFiles);
    } catch (err: any) {
      setError(err.message);
    }
    setLoading(false);
  };

  // Charger et parser les fichiers JSON des items
  const loadItemsFromJsonList = async (category: string, subcategory: string, jsonFiles: any[]) => {
    const loadedItems: ItemDefinition[] = [];
    
    // Limiter à 30 items pour éviter trop de requêtes
    const filesToLoad = jsonFiles.slice(0, 30);
    
    for (const file of filesToLoad) {
      try {
        const jsonUrl = `${GITHUB_RAW}/sheet_definitions/${category}${subcategory ? '/' + subcategory : ''}/${file.name}`;
        const res = await fetch(jsonUrl);
        if (!res.ok) continue;
        const def = await res.json();
        
        // Trouver le chemin du sprite (layer_1 généralement)
        let spritePath = '';
        if (def.layer_1?.male) {
          spritePath = def.layer_1.male;
        } else if (def.layer_1) {
          spritePath = Object.values(def.layer_1).find((v: any) => typeof v === 'string' && v.includes('/')) as string || '';
        }
        
        // Construire l'URL de preview (animation walk ou idle)
        const variant = def.variants?.[0] || file.name.replace('.json', '').split('_').pop();
        const previewUrl = spritePath 
          ? `${GITHUB_RAW}/spritesheets/${spritePath}walk/${variant}.png`
          : '';
        
        loadedItems.push({
          name: def.name || file.name.replace('.json', ''),
          fileName: file.name,
          category,
          subcategory,
          spritePath,
          previewUrl,
          variants: def.variants,
        });
      } catch (e) {
        console.error('Error loading', file.name, e);
      }
    }
    
    setItems(loadedItems);
    setAllItems(prev => [...prev.filter(i => i.category !== category || i.subcategory !== subcategory), ...loadedItems]);
  };

  // Retour
  const goBack = () => {
    if (selectedSubcategory) {
      setSelectedSubcategory(null);
      setItems([]);
      setSelectedItem(null);
    } else if (selectedCategory) {
      setSelectedCategory(null);
      setSubcategories([]);
      setItems([]);
      setSelectedItem(null);
    }
  };

  // Filtrer
  const filteredItems = searchQuery && !selectedCategory
    ? allItems.filter(i => i.name.toLowerCase().includes(searchQuery.toLowerCase()))
    : items;

  // Recherche globale
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (query && !selectedCategory) {
      // Recherche dans tous les items chargés
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3">
          <FolderOpen className="w-6 h-6 text-yellow-500" />
          <h2 className="text-xl font-bold text-white">Explorateur LPC</h2>
          {selectedCategory && (
            <Badge className="bg-gray-600 text-sm">
              {CATEGORIES.find(c => c.id === selectedCategory)?.name}
              {selectedSubcategory && ` / ${selectedSubcategory}`}
            </Badge>
          )}
        </div>
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Rechercher..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="pl-10 w-64 bg-gray-700 border-gray-600"
          />
        </div>
      </div>

      {/* Back button */}
      {(selectedCategory || selectedSubcategory) && (
        <Button variant="ghost" size="sm" onClick={goBack}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Retour
        </Button>
      )}

      {/* Contenu */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-16">
          <Loader2 className="w-10 h-10 animate-spin text-yellow-500 mb-4" />
          <p className="text-gray-400">Chargement...</p>
        </div>
      ) : error ? (
        <div className="text-center py-16">
          <p className="text-red-400 mb-4">{error}</p>
          <Button onClick={() => selectedCategory && loadCategory(selectedCategory)}>Réessayer</Button>
        </div>
      ) : !selectedCategory ? (
        /* Grille des catégories principales */
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => loadCategory(cat.id)}
              className="p-6 rounded-xl bg-gray-800 border border-gray-700 hover:border-yellow-500 hover:bg-gray-700 transition-all group"
            >
              <div className={`w-14 h-14 rounded-xl ${cat.color} flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform`}>
                <cat.icon className="w-7 h-7 text-white" />
              </div>
              <p className="text-white font-semibold text-lg">{cat.name}</p>
              <p className="text-gray-400 text-sm mt-1">{cat.id}</p>
            </button>
          ))}
        </div>
      ) : subcategories.length > 0 && !selectedSubcategory ? (
        /* Grille des sous-catégories */
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {subcategories.map((sub) => (
            <button
              key={sub}
              onClick={() => loadSubcategory(sub)}
              className="p-4 rounded-lg bg-gray-800 border border-gray-700 hover:border-blue-500 hover:bg-gray-700 transition-all"
            >
              <FolderOpen className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
              <p className="text-white font-medium text-sm truncate">{sub}</p>
            </button>
          ))}
        </div>
      ) : (
        /* Grille des items */
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {filteredItems.map((item, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedItem(item)}
              className={`p-4 rounded-lg border transition-all text-left ${
                selectedItem?.fileName === item.fileName
                  ? 'bg-yellow-500/20 border-yellow-500'
                  : 'bg-gray-800 border-gray-700 hover:border-blue-500 hover:bg-gray-700'
              }`}
            >
              <div className="w-16 h-16 mx-auto mb-3 bg-gray-900 rounded-lg flex items-center justify-center overflow-hidden">
                {item.previewUrl ? (
                  <img
                    src={item.previewUrl}
                    alt={item.name}
                    className="w-16 h-16 object-none object-[0_-128px]"
                    style={{ imageRendering: 'pixelated' }}
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                ) : (
                  <Swords className="w-8 h-8 text-gray-600" />
                )}
              </div>
              <p className="text-white font-medium text-sm truncate text-center" title={item.name}>
                {item.name}
              </p>
            </button>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && selectedCategory && items.length === 0 && subcategories.length === 0 && (
        <div className="text-center py-16 text-gray-400">
          <p>Aucun item trouvé dans cette catégorie</p>
        </div>
      )}

      {/* Panel item sélectionné */}
      {selectedItem && (
        <Card className="bg-gray-800 border-yellow-500/50 mt-6">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row items-start gap-6">
              {/* Preview */}
              <div className="bg-gray-900 rounded-xl p-6 flex-shrink-0">
                {selectedItem.previewUrl ? (
                  <img
                    src={selectedItem.previewUrl}
                    alt={selectedItem.name}
                    className="w-32 h-32 object-none object-[0_-128px]"
                    style={{ imageRendering: 'pixelated' }}
                  />
                ) : (
                  <div className="w-32 h-32 flex items-center justify-center">
                    <Swords className="w-16 h-16 text-gray-600" />
                  </div>
                )}
              </div>

              {/* Infos */}
              <div className="flex-1 space-y-4">
                <div>
                  <h3 className="text-xl font-bold text-white mb-1">{selectedItem.name}</h3>
                  <p className="text-sm text-gray-400">
                    {selectedItem.category}{selectedItem.subcategory && ` / ${selectedItem.subcategory}`}
                  </p>
                  <p className="text-xs text-gray-500 mt-2 font-mono">
                    {selectedItem.spritePath}
                  </p>
                  {selectedItem.variants && selectedItem.variants.length > 0 && (
                    <div className="mt-3 flex gap-2 flex-wrap">
                      {selectedItem.variants.map(v => (
                        <Badge key={v} className="bg-gray-700">{v}</Badge>
                      ))}
                    </div>
                  )}
                </div>
                
                <div className="flex gap-3 flex-wrap">
                  <Button
                    onClick={() => {
                      const variant = selectedItem.variants?.[0] || 'default';
                      const spriteUrl = selectedItem.previewUrl || `${GITHUB_RAW}/spritesheets/${selectedItem.spritePath}walk/${variant}.png`;
                      onSelectSprite({
                        name: selectedItem.name,
                        url: spriteUrl,
                        localPath: `/sprites/lpc/${selectedItem.spritePath}`,
                      });
                    }}
                    className="bg-yellow-600 hover:bg-yellow-500"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Créer un item
                  </Button>
                  
                  <Button 
                    variant="secondary"
                    onClick={() => {
                      navigator.clipboard.writeText(selectedItem.previewUrl || '');
                      alert('URL copiée !');
                    }}
                  >
                    Copier l'URL
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Info */}
      <p className="text-xs text-gray-500 text-center mt-8">
        Source : Universal LPC Spritesheet Character Generator • Organisation identique au générateur web
      </p>
    </div>
  );
}
