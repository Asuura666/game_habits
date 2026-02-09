'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, UserPlus, Search, MessageCircle, X, Flame, Trophy } from 'lucide-react';
import { Card, CardHeader, CardTitle, Button, Input, Badge } from '@/components/ui';

const mockFriends = [
  { id: '1', username: 'Dragon_Slayer', level: 12, streak: 25, status: 'online', avatarEmoji: '🐉' },
  { id: '2', username: 'MeditationMaster', level: 8, streak: 45, status: 'online', avatarEmoji: '🧘' },
  { id: '3', username: 'FitnessQueen', level: 15, streak: 30, status: 'away', avatarEmoji: '💪' },
  { id: '4', username: 'BookWorm42', level: 6, streak: 12, status: 'offline', avatarEmoji: '📚' },
  { id: '5', username: 'NightOwl', level: 9, streak: 18, status: 'offline', avatarEmoji: '🦉' },
];

const friendRequests = [
  { id: 'r1', username: 'NewHero2024', level: 3, avatarEmoji: '⚔️' },
  { id: 'r2', username: 'HealthyLife', level: 5, avatarEmoji: '🥗' },
];

const statusColors: Record<string, string> = {
  online: 'bg-green-500',
  away: 'bg-yellow-500',
  offline: 'bg-gray-400',
};

export default function FriendsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddFriend, setShowAddFriend] = useState(false);
  const [newFriendUsername, setNewFriendUsername] = useState('');

  const filteredFriends = mockFriends.filter((friend) =>
    friend.username.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const onlineFriends = mockFriends.filter((f) => f.status === 'online').length;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <Users className="w-8 h-8 text-primary-500" />
            Mes Amis
          </h1>
          <p className="text-gray-500 dark:text-gray-400">
            {mockFriends.length} amis · {onlineFriends} en ligne
          </p>
        </div>
        <Button onClick={() => setShowAddFriend(true)}>
          <UserPlus className="w-5 h-5 mr-2" />
          Ajouter un ami
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Friends List */}
        <div className="lg:col-span-2 space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher un ami..."
              className="w-full pl-10 pr-4 py-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {/* Friends Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <AnimatePresence mode="popLayout">
              {filteredFriends.map((friend, index) => (
                <motion.div
                  key={friend.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Card variant="bordered" hover className="cursor-pointer">
                    <div className="p-4">
                      <div className="flex items-center gap-4">
                        {/* Avatar */}
                        <div className="relative">
                          <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-2xl">
                            {friend.avatarEmoji}
                          </div>
                          <div className={`absolute bottom-0 right-0 w-4 h-4 rounded-full border-2 border-white dark:border-gray-800 ${statusColors[friend.status]}`} />
                        </div>

                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <p className="font-bold text-gray-900 dark:text-white truncate">
                            {friend.username}
                          </p>
                          <div className="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
                            <span className="flex items-center gap-1">
                              <Trophy className="w-4 h-4 text-yellow-500" />
                              Niv. {friend.level}
                            </span>
                            <span className="flex items-center gap-1">
                              <Flame className="w-4 h-4 text-orange-500" />
                              {friend.streak}
                            </span>
                          </div>
                        </div>

                        {/* Actions */}
                        <button className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                          <MessageCircle className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                        </button>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {filteredFriends.length === 0 && (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              Aucun ami trouvé
            </div>
          )}
        </div>

        {/* Friend Requests */}
        <div className="lg:col-span-1">
          <Card variant="bordered" padding="lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserPlus className="w-5 h-5 text-primary-500" />
                Demandes ({friendRequests.length})
              </CardTitle>
            </CardHeader>
            
            {friendRequests.length > 0 ? (
              <div className="space-y-3">
                {friendRequests.map((request) => (
                  <div
                    key={request.id}
                    className="flex items-center gap-3 p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50"
                  >
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-lg">
                      {request.avatarEmoji}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 dark:text-white truncate">
                        {request.username}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Niveau {request.level}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button className="p-2 rounded-lg bg-green-100 text-green-600 hover:bg-green-200 dark:bg-green-900/50 dark:text-green-400 dark:hover:bg-green-900">
                        ✓
                      </button>
                      <button className="p-2 rounded-lg bg-red-100 text-red-600 hover:bg-red-200 dark:bg-red-900/50 dark:text-red-400 dark:hover:bg-red-900">
                        ✕
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                Aucune demande en attente
              </p>
            )}
          </Card>

          {/* Suggested Friends */}
          <Card variant="bordered" padding="lg" className="mt-4">
            <CardHeader>
              <CardTitle>Suggestions</CardTitle>
            </CardHeader>
            <div className="space-y-3">
              {[
                { username: 'EarlyBird', level: 7, avatarEmoji: '🐦' },
                { username: 'ZenMaster', level: 10, avatarEmoji: '🎋' },
              ].map((suggestion) => (
                <div
                  key={suggestion.username}
                  className="flex items-center gap-3 p-3 rounded-xl bg-gray-50 dark:bg-gray-800/50"
                >
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-lg">
                    {suggestion.avatarEmoji}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900 dark:text-white">{suggestion.username}</p>
                    <p className="text-sm text-gray-500">Niv. {suggestion.level}</p>
                  </div>
                  <Button size="sm" variant="secondary">
                    <UserPlus className="w-4 h-4" />
                  </Button>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {/* Add Friend Modal */}
      <AnimatePresence>
        {showAddFriend && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
            onClick={() => setShowAddFriend(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <Card variant="elevated" padding="lg" className="w-full max-w-md bg-white dark:bg-gray-800">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">Ajouter un ami</h2>
                  <button onClick={() => setShowAddFriend(false)} className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
                    <X className="w-5 h-5 text-gray-500" />
                  </button>
                </div>

                <div className="space-y-4">
                  <Input
                    label="Nom d'utilisateur"
                    value={newFriendUsername}
                    onChange={(e) => setNewFriendUsername(e.target.value)}
                    placeholder="Entrez un nom d'utilisateur"
                    icon={<Search className="w-5 h-5" />}
                  />

                  <div className="flex gap-3 pt-4">
                    <Button variant="secondary" onClick={() => setShowAddFriend(false)} className="flex-1">
                      Annuler
                    </Button>
                    <Button className="flex-1">
                      <UserPlus className="w-5 h-5 mr-2" />
                      Envoyer
                    </Button>
                  </div>
                </div>
              </Card>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
