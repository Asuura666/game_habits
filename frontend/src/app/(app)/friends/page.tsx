'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, UserPlus, Search, X, Check, Clock, Flame, Copy, Loader2 } from 'lucide-react';
import { Card, Button, Input, Badge } from '@/components/ui';
import { SpriteAvatar } from '@/components/character';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';

interface Friend {
  friendship_id: string;
  user_id: string;
  username: string;
  avatar_url: string | null;
  character_name: string | null;
  character_class: string | null;
  level: number;
  total_xp: number;
  current_streak: number;
  is_online: boolean;
  last_active: string | null;
  friends_since: string;
}

interface FriendRequest {
  id: string;
  from_user_id: string;
  from_username: string;
  from_avatar: string | null;
  from_level: number;
  to_user_id: string;
  status: string;
  created_at: string;
}

export default function FriendsPage() {
  const { accessToken } = useAuthStore();
  const [friends, setFriends] = useState<Friend[]>([]);
  const [incomingRequests, setIncomingRequests] = useState<FriendRequest[]>([]);
  const [outgoingRequests, setOutgoingRequests] = useState<FriendRequest[]>([]);
  const [friendCode, setFriendCode] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newFriendCode, setNewFriendCode] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  // Fetch all data on mount
  useEffect(() => {
    const fetchData = async () => {
      if (!accessToken) return;
      setIsLoading(true);

      try {
        // Fetch friends list
        const friendsRes = await fetch(`${API_URL}/friends/`, {
          headers: { Authorization: `Bearer ${accessToken}` }
        });
        if (friendsRes.ok) {
          const data = await friendsRes.json();
          setFriends(data.friends || []);
        }

        // Fetch pending requests
        const pendingRes = await fetch(`${API_URL}/friends/pending`, {
          headers: { Authorization: `Bearer ${accessToken}` }
        });
        if (pendingRes.ok) {
          const data = await pendingRes.json();
          setIncomingRequests(data.incoming || []);
          setOutgoingRequests(data.outgoing || []);
        }

        // Fetch friend code
        const codeRes = await fetch(`${API_URL}/friends/code`, {
          headers: { Authorization: `Bearer ${accessToken}` }
        });
        if (codeRes.ok) {
          const data = await codeRes.json();
          setFriendCode(data.friend_code || '');
        }
      } catch (err) {
        console.error('Failed to fetch friends data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [accessToken, API_URL]);

  const filteredFriends = friends.filter((f) =>
    f.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (f.character_name && f.character_name.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const onlineFriends = friends.filter((f) => f.is_online).length;

  const handleAcceptRequest = async (requestId: string) => {
    try {
      const res = await fetch(`${API_URL}/friends/accept/${requestId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      if (res.ok) {
        const newFriend = await res.json();
        setFriends(prev => [...prev, newFriend]);
        setIncomingRequests(prev => prev.filter(r => r.id !== requestId));
        setSuccessMessage('Demande acceptée !');
        setTimeout(() => setSuccessMessage(''), 3000);
      }
    } catch (err) {
      setError('Erreur lors de l\'acceptation');
    }
  };

  const handleRejectRequest = async (requestId: string) => {
    try {
      await fetch(`${API_URL}/friends/reject/${requestId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      setIncomingRequests(prev => prev.filter(r => r.id !== requestId));
    } catch (err) {
      setError('Erreur lors du refus');
    }
  };

  const handleRemoveFriend = async (userId: string) => {
    if (!confirm('Êtes-vous sûr de vouloir retirer cet ami ?')) return;
    
    try {
      await fetch(`${API_URL}/friends/${userId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      setFriends(prev => prev.filter(f => f.user_id !== userId));
    } catch (err) {
      setError('Erreur lors de la suppression');
    }
  };

  const handleSendRequest = async () => {
    if (!newFriendCode.trim()) return;
    setIsSubmitting(true);
    setError('');

    try {
      const res = await fetch(`${API_URL}/friends/code/${newFriendCode.toUpperCase()}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${accessToken}` }
      });

      if (res.ok) {
        setNewFriendCode('');
        setShowAddModal(false);
        setSuccessMessage('Demande envoyée !');
        setTimeout(() => setSuccessMessage(''), 3000);
        
        // Refresh pending requests
        const pendingRes = await fetch(`${API_URL}/friends/pending`, {
          headers: { Authorization: `Bearer ${accessToken}` }
        });
        if (pendingRes.ok) {
          const data = await pendingRes.json();
          setOutgoingRequests(data.outgoing || []);
        }
      } else {
        const data = await res.json();
        setError(data.detail || 'Erreur lors de l\'envoi');
      }
    } catch (err) {
      setError('Erreur lors de l\'envoi de la demande');
    } finally {
      setIsSubmitting(false);
    }
  };

  const copyFriendCode = () => {
    navigator.clipboard.writeText(friendCode);
    setSuccessMessage('Code copié !');
    setTimeout(() => setSuccessMessage(''), 2000);
  };

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

      {/* Success/Error Messages */}
      {successMessage && (
        <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400">
          {successMessage}
        </div>
      )}
      {error && (
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400">
          {error}
        </div>
      )}

      {/* Friend Code */}
      <Card variant="bordered" padding="md" className="bg-primary-500/10 border-primary-500/30">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Ton code ami</p>
            <p className="text-2xl font-bold text-primary-500 tracking-wider">{friendCode}</p>
          </div>
          <Button variant="secondary" onClick={copyFriendCode}>
            <Copy className="w-4 h-4 mr-2" />
            Copier
          </Button>
        </div>
      </Card>

      {/* Pending Requests */}
      {incomingRequests.length > 0 && (
        <Card variant="bordered" padding="lg" className="border-primary-500/50">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-primary-500" />
            Demandes reçues ({incomingRequests.length})
          </h3>
          <div className="space-y-3">
            {incomingRequests.map((request) => (
              <motion.div
                key={request.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-white font-bold">
                    {request.from_username.charAt(0)}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{request.from_username}</p>
                    <p className="text-sm text-gray-500">Niveau {request.from_level}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => handleAcceptRequest(request.id)}>
                    <Check className="w-4 h-4" />
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => handleRejectRequest(request.id)}>
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </motion.div>
            ))}
          </div>
        </Card>
      )}

      {/* Outgoing Requests */}
      {outgoingRequests.length > 0 && (
        <Card variant="bordered" padding="lg">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-gray-400" />
            Demandes envoyées ({outgoingRequests.length})
          </h3>
          <div className="space-y-2">
            {outgoingRequests.map((request) => (
              <div key={request.id} className="flex items-center gap-3 p-2 text-gray-500">
                <span>En attente de réponse de {request.to_user_id}</span>
              </div>
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
              key={friend.friendship_id}
              layout
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -100 }}
            >
              <Card variant="bordered" className="flex items-center gap-4">
                <div className="relative">
                  {friend.character_class ? (
                    <SpriteAvatar
                      characterClass={friend.character_class}
                      size="md"
                    />
                  ) : (
                    <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-xl font-bold text-white">
                      {friend.username.charAt(0)}
                    </div>
                  )}
                  <div
                    className={cn(
                      'absolute bottom-0 right-0 w-4 h-4 rounded-full border-2 border-white dark:border-gray-800',
                      friend.is_online ? 'bg-green-500' : 'bg-gray-500'
                    )}
                  />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                      {friend.character_name || friend.username}
                    </h3>
                    <Badge size="sm">{friend.is_online ? 'En ligne' : 'Hors ligne'}</Badge>
                  </div>
                  <div className="flex items-center gap-4 mt-1 text-sm text-gray-500 dark:text-gray-400">
                    <span>Niveau {friend.level}</span>
                    {friend.current_streak > 0 && (
                      <span className="flex items-center gap-1 text-orange-500">
                        <Flame className="w-4 h-4" />
                        {friend.current_streak} jours
                      </span>
                    )}
                  </div>
                </div>

                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleRemoveFriend(friend.user_id)}
                  className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                >
                  <X className="w-4 h-4" />
                </Button>
              </Card>
            </motion.div>
          ))}
        </AnimatePresence>

        {filteredFriends.length === 0 && (
          <div className="text-center py-12">
            <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">
              {searchQuery ? 'Aucun ami trouvé' : "Tu n'as pas encore d'amis"}
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
                    label="Code ami"
                    value={newFriendCode}
                    onChange={(e) => setNewFriendCode(e.target.value.toUpperCase())}
                    placeholder="Ex: ABC123"
                    icon={<UserPlus className="w-5 h-5" />}
                    maxLength={10}
                  />

                  {error && (
                    <p className="text-red-400 text-sm">{error}</p>
                  )}

                  <div className="flex gap-3">
                    <Button variant="secondary" onClick={() => setShowAddModal(false)} className="flex-1">
                      Annuler
                    </Button>
                    <Button onClick={handleSendRequest} className="flex-1" disabled={isSubmitting}>
                      {isSubmitting ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        'Envoyer'
                      )}
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
