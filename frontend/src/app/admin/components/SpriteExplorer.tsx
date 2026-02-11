'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { Button } from '@/components/ui';
import { Input } from '@/components/ui';
import { Badge } from '@/components/ui';
import { ChevronRight, ChevronDown, Image, Download, Plus, Search, Loader2, FolderOpen, ArrowLeft } from 'lucide-react';

const GITHUB_API = 'https://api.github.com/repos/sanderfrenken/Universal-LPC-Spritesheet-Character-Generator/contents/spritesheets';
const GITHUB_RAW = 'https://raw.githubusercontent.com/sanderfrenken/Universal-LPC-Spritesheet-Character-Generator/master/spritesheets';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'dir';
  download_url?: string;
}

interface SpriteExplorerProps {
  onSelectSprite: (sprite: { name: string; url: string; localPath: string }) => void;
}

export function SpriteExplorer({ onSelectSprite }: SpriteExplorerProps) {
  const [currentPath, setCurrentPath] = useState('');
  const [contents, setContents] = useState<FileNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSprite, setSelectedSprite] = useState<FileNode | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [downloading, setDownloading] = useState(false);

  // Charger le contenu d'un dossier
  const loadDirectory = async (path: string) => {
    setLoading(true);
    setError(null);
    try {
      const url = path ? `${GITHUB_API}/${path}` : GITHUB_API;
      const res = await fetch(url);
      if (!res.ok) throw new Error('Erreur de chargement');
      const data = await res.json();
      
      // Trier : dossiers d'abord, puis fichiers
      const sorted = data.sort((a: FileNode, b: FileNode) => {
        if (a.type === b.type) return a.name.localeCompare(b.name);
        return a.type === 'dir' ? -1 : 1;
      });
      
      setContents(sorted);
      setCurrentPath(path);
    } catch (err) {
      setError('Erreur de chargement. Réessayez.');
      console.error(err);
    }
    setLoading(false);
  };

  // Charger le dossier racine au démarrage
  useEffect(() => {
    loadDirectory('');
  }, []);

  // Navigation : remonter d'un niveau
  const goBack = () => {
    const parts = currentPath.split('/');
    parts.pop();
    loadDirectory(parts.join('/'));
  };

  // Générer le chemin local pour un sprite
  const getLocalPath = (githubPath: string) => {
    return `/sprites/lpc/${githubPath.replace('spritesheets/', '')}`;
  };

  // Télécharger un sprite sur le serveur
  const downloadSprite = async (node: FileNode) => {
    setDownloading(true);
    try {
      const localPath = getLocalPath(node.path);
      // Appeler l'API pour télécharger
      const res = await fetch('/api/admin/sprites/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: `${GITHUB_RAW}/${node.path.replace('spritesheets/', '')}`,
          localPath,
        }),
      });
      
      if (res.ok) {
        onSelectSprite({
          name: node.name.replace('.png', ''),
          url: `${GITHUB_RAW}/${node.path.replace('spritesheets/', '')}`,
          localPath,
        });
      }
    } catch (err) {
      console.error('Erreur téléchargement:', err);
    }
    setDownloading(false);
  };

  // Filtrer les contenus
  const filteredContents = searchQuery
    ? contents.filter(c => c.name.toLowerCase().includes(searchQuery.toLowerCase()))
    : contents;

  // Breadcrumb
  const pathParts = currentPath ? currentPath.split('/') : [];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <FolderOpen className="w-5 h-5 text-yellow-500" />
          <h2 className="text-lg font-bold text-white">Explorateur LPC</h2>
          <Badge className="bg-blue-600">{contents.filter(c => c.type === 'file').length} sprites</Badge>
        </div>
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            placeholder="Rechercher..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 w-64 bg-gray-700 border-gray-600"
          />
        </div>
      </div>

      {/* Breadcrumb */}
      <div className="flex items-center gap-1 text-sm text-gray-400 flex-wrap">
        <button onClick={() => loadDirectory('')} className="hover:text-white">
          spritesheets
        </button>
        {pathParts.map((part, i) => (
          <span key={i} className="flex items-center gap-1">
            <ChevronRight className="w-4 h-4" />
            <button
              onClick={() => loadDirectory(pathParts.slice(0, i + 1).join('/'))}
              className="hover:text-white"
            >
              {part}
            </button>
          </span>
        ))}
      </div>

      {/* Navigation */}
      {currentPath && (
        <Button variant="ghost" size="sm" onClick={goBack}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Retour
        </Button>
      )}

      {/* Contenu */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-yellow-500" />
        </div>
      ) : error ? (
        <div className="text-center py-12 text-red-400">{error}</div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3">
          {filteredContents.map((node) => (
            <div
              key={node.path}
              onClick={() => {
                if (node.type === 'dir') {
                  loadDirectory(node.path);
                } else {
                  setSelectedSprite(node);
                }
              }}
              className={`
                p-3 rounded-lg border cursor-pointer transition-all
                ${node.type === 'dir' 
                  ? 'bg-gray-800 border-gray-700 hover:border-yellow-500' 
                  : 'bg-gray-900 border-gray-700 hover:border-blue-500'}
                ${selectedSprite?.path === node.path ? 'border-blue-500 ring-2 ring-blue-500/50' : ''}
              `}
            >
              {node.type === 'dir' ? (
                <div className="text-center">
                  <FolderOpen className="w-10 h-10 mx-auto mb-2 text-yellow-500" />
                  <p className="text-xs text-white truncate">{node.name}</p>
                </div>
              ) : (
                <div className="text-center">
                  <div className="w-16 h-16 mx-auto mb-2 bg-gray-800 rounded flex items-center justify-center overflow-hidden">
                    <img
                      src={`${GITHUB_RAW}/${node.path.replace('spritesheets/', '')}`}
                      alt={node.name}
                      className="max-w-full max-h-full object-contain"
                      style={{ 
                        imageRendering: 'pixelated',
                        transform: 'scale(2)',
                        transformOrigin: 'top left',
                        clipPath: 'inset(0 0 calc(100% - 64px) calc(100% - 64px))'
                      }}
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                  </div>
                  <p className="text-xs text-gray-300 truncate" title={node.name}>
                    {node.name.replace('.png', '')}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Panel sprite sélectionné */}
      {selectedSprite && (
        <Card className="bg-gray-800 border-gray-700 mt-6">
          <CardContent className="p-4">
            <div className="flex items-start gap-6">
              {/* Preview */}
              <div className="bg-gray-900 rounded-lg p-4 flex-shrink-0">
                <div className="w-32 h-32 overflow-hidden">
                  <img
                    src={`${GITHUB_RAW}/${selectedSprite.path.replace('spritesheets/', '')}`}
                    alt={selectedSprite.name}
                    className="w-full h-full object-contain"
                    style={{ 
                      imageRendering: 'pixelated',
                      objectPosition: '0 -128px'
                    }}
                  />
                </div>
              </div>

              {/* Infos */}
              <div className="flex-1 space-y-3">
                <h3 className="text-lg font-bold text-white">{selectedSprite.name.replace('.png', '')}</h3>
                <p className="text-sm text-gray-400">
                  Chemin : <code className="text-xs bg-gray-900 px-2 py-1 rounded">{selectedSprite.path}</code>
                </p>
                
                <div className="flex gap-2 flex-wrap">
                  <Button
                    onClick={() => {
                      onSelectSprite({
                        name: selectedSprite.name.replace('.png', ''),
                        url: `${GITHUB_RAW}/${selectedSprite.path.replace('spritesheets/', '')}`,
                        localPath: getLocalPath(selectedSprite.path),
                      });
                    }}
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Utiliser ce sprite
                  </Button>
                  
                  <Button variant="secondary" onClick={() => downloadSprite(selectedSprite)} disabled={downloading}>
                    {downloading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
                    Télécharger sur serveur
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Stats */}
      <p className="text-xs text-gray-500 text-center">
        24 221 sprites disponibles depuis le repo LPC • Navigation en temps réel
      </p>
    </div>
  );
}
