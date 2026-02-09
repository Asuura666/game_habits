'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, UserPlus, Search, MessageCircle, X, Check, Clock, Flame } from 'lucide-react';
import { Card, Button, Input, Badge } from '@/components/ui';
import { cn } from '@/lib/utils';
import type { Friend } from '@/types';

const mockFriends: Friend[] = [
  { id: '1', username: 'HeroMaster42', level: 12, streak: 15, status: 'online' },
  { id: '2', username: 'QuestHunter', level: 8, streak: 7, status: 'online' },
  { id: '3', username: 'DragonSlayer', level: 20, streak: 30, status: 'away' },
  { id: '4', username: 'MageSupreme', level: 15, streak: 0, status: 'offline' },
  { id: '5', username: 'NightOwl99', level: 6, streak: 3, status: 'offline' },
];

const pendingRequests = [
  { id: '6', username: 'NewAdventurer', level: 2 },
  { id: '7', username: 'QuestSeeker', level: 5 },
];

const statusColors = {
  online: 'bg-green-500',
  away: 'bg-yellow-500',
  offline: 'bg-gray-500',
};

const statusLabels = {
  online: 'En ligne',
  away: 'Absent',
  offline: 'Hors ligne',
};

export default function FriendsPage() {
  const [friends, setFriends] = useState<Friend[]>(mockFriends);
  const [requests, setRequests] = useState(pendingRequests);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newFriendUsername, setNewFriendUsername] = useState('');

  const filteredFriends = friends.filter((f) =>
    f.username.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const onlineFriends = friends.filter((f) => f.status === 'online').length;

  const handleAcceptRequest = (id: string) => {
    const request = requests.find((r) => r.id === id);
    if (request) {
      setFriends((prev) => [
        ...prev,
        { ...request, streak: 0, status: 'online' as const },
      ]);
      setRequests((prev) => prev.filter((r) => r.id !== id));
    }
  };

  const handleRejectRequest = (id: string) => {
    setRequests((prev) => prev.filter((r) => r.id !== id));
  };

  const handleRemoveFriend = (id: string) => {
    setFriends((prev) => prev.filter((f) => f.id !== id));
  };

  const handleSendRequest = () => {
    if (!newFriendUsername.trim()) return;
    // In real app, this would make an API call
    setNewFriendUsername('');
    setShowAddModal(false);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <Users className="w-8 h-8 text-primary-500" />
            Mes Amis
          </h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            {onlineFriends} amis en ligne sur {friends.length}
          </p>
        </div>
        <Button onClick={() => setShowAddModal(true)}>
          <UserPlus className="w-5 h-5 mr-2" />
          Ajouter
        </Button>
      </div>

      {/* Pending Requests */}
      {requests.length > 0 && (
        <Card variant="bordered" padding="lg" className="border-primary-500/50">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-primary-500" />
            Demandes en attente ({requests.length})
          </h3>
          <div className="space-y-3">
            {requests.map((request) => (
              <motion.div
                key={request.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-white font-bold">
                    {request.username.charAt(0)}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{request.username}</p>
                    <p className="text-sm text-gray-500">Niveau {request.level}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => handleAcceptRequest(request.id)}>
                    <Check className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleRejectRequest(request.id)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </motion.div>
            ))}
          </div>
        </Card>
      )}

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Rechercher un ami..."
          className="w-full pl-10 pr-4 py-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {/* Friends List */}
      <div className="space-y-3">
        <AnimatePresence mode="popLayout">
          {filteredFriends.map((friend) => (
            <motion.div
              key={friend.id}
              layout
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -100 }}
            >
              <Card variant="bordered" className="flex items-center gap-4">
                <div className="relative">
                  <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-xl font-bold text-white">
                    {friend.username.charAt(0)}
                  </div>
                  <div
                    className={cn(
                      'absolute bottom-0 right-0 w-4 h-4 rounded-full border-2 border-white dark:border-gray-800',
                      statusColors[friend.status]
                    )}
                  />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                      {friend.username}
                    </h3>
                    <Badge size="sm">{statusLabels[friend.status]}</Badge>
                  </div>
                  <div className="flex items-center gap-4 mt-1 text-sm text-gray-500 dark:text-gray-400">
                    <span>Niveau {friend.level}</span>
                    {friend.streak > 0 && (
                      <span className="flex items-center gap-1 text-orange-500">
                        <Flame className="w-4 h-4" />
                        {friend.streak} jours
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button size="sm" variant="secondary">
                    <MessageCircle className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleRemoveFriend(friend.id)}
                    className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            </motion.div>
          ))}
        </AnimatePresence>

        {filteredFriends.length === 0 && (
          <div className="text-center py-12">
            <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">
              {searchQuery ? 'Aucun ami trouvé' : "Vous n'avez pas encore d'amis"}
            </p>
            {!searchQuery && (
              <Button onClick={() => setShowAddModal(true)} className="mt-4">
                <UserPlus className="w-5 h-5 mr-2" />
                Ajouter des amis
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Add Friend Modal */}
      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
            onClick={() => setShowAddModal(false)}
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
                  <button
                    onClick={() => setShowAddModal(false)}
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <X className="w-5 h-5 text-gray-500" />
                  </button>
                </div>

                <div className="space-y-4">
                  <Input
                    label="Nom d'utilisateur"
                    value={newFriendUsername}
                    onChange={(e) => setNewFriendUsername(e.target.value)}
                    placeholder="Entrez un nom d'utilisateur"
                    icon={<UserPlus className="w-5 h-5" />}
                  />

                  <div className="flex gap-3">
                    <Button variant="secondary" onClick={() => setShowAddModal(false)} className="flex-1">
                      Annuler
                    </Button>
                    <Button onClick={handleSendRequest} className="flex-1">
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
