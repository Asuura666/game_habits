'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Users, 
  UserPlus, 
  Search, 
  X, 
  Check, 
  Clock, 
  Flame, 
  Copy, 
  Loader2,
  UserX,
  ExternalLink,
  AlertTriangle
} from 'lucide-react';
import { Card, Button, Input, Badge } from '@/components/ui';
import { SpriteAvatar } from '@/components/character';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';

// ============================================================================
// Types
// ============================================================================

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
  to_username?: string;
  status: string;
  created_at: string;
}

// ============================================================================
// Skeleton Components
// ============================================================================

function FriendCardSkeleton() {
  return (
    <Card variant="bordered" className="flex items-center gap-4 animate-pulse">
      <div className="w-14 h-14 rounded-full bg-gray-200 dark:bg-gray-700" />
      <div className="flex-1 space-y-2">
        <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded" />
        <div className="h-3 w-24 bg-gray-200 dark:bg-gray-700 rounded" />
      </div>
      <div className="flex gap-2">
        <div className="h-9 w-24 bg-gray-200 dark:bg-gray-700 rounded-lg" />
        <div className="h-9 w-9 bg-gray-200 dark:bg-gray-700 rounded-lg" />
      </div>
    </Card>
  );
}

function RequestSkeleton() {
  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 animate-pulse">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700" />
        <div className="space-y-2">
          <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded" />
          <div className="h-3 w-16 bg-gray-200 dark:bg-gray-700 rounded" />
        </div>
      </div>
      <div className="flex gap-2">
        <div className="h-9 w-9 bg-gray-200 dark:bg-gray-700 rounded-lg" />
        <div className="h-9 w-9 bg-gray-200 dark:bg-gray-700 rounded-lg" />
      </div>
    </div>
  );
}

function FriendCodeSkeleton() {
  return (
    <Card variant="bordered" padding="md" className="bg-primary-500/10 border-primary-500/30 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <div className="h-3 w-20 bg-gray-300 dark:bg-gray-600 rounded" />
          <div className="h-8 w-32 bg-primary-400/30 rounded" />
        </div>
        <div className="h-10 w-24 bg-gray-300 dark:bg-gray-600 rounded-lg" />
      </div>
    </Card>
  );
}

// ============================================================================
// Delete Confirmation Modal
// ============================================================================

interface DeleteModalProps {
  isOpen: boolean;
  friendName: string;
  onConfirm: () => void;
  onCancel: () => void;
  isLoading: boolean;
}

function DeleteConfirmModal({ isOpen, friendName, onConfirm, onCancel, isLoading }: DeleteModalProps) {
  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      onClick={onCancel}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <Card variant="elevated" padding="lg" className="w-full max-w-sm bg-white dark:bg-gray-800">
          <div className="flex flex-col items-center text-center">
            <div className="w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mb-4">
              <AlertTriangle className="w-6 h-6 text-red-500" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              Supprimer cet ami ?
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              Tu vas retirer <span className="font-medium text-gray-700 dark:text-gray-300">{friendName}</span> de ta liste d'amis. Cette action est irréversible.
            </p>
            <div className="flex gap-3 w-full">
              <Button variant="secondary" onClick={onCancel} className="flex-1" disabled={isLoading}>
                Annuler
              </Button>
              <Button variant="danger" onClick={onConfirm} className="flex-1" disabled={isLoading}>
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Supprimer'}
              </Button>
            </div>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  );
}

// ============================================================================
// Main Component
// ============================================================================

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
  
  // Delete confirmation state
  const [deleteModal, setDeleteModal] = useState<{ isOpen: boolean; friend: Friend | null; isLoading: boolean }>({
    isOpen: false,
    friend: null,
    isLoading: false
  });

  const API_URL = process.env.NEXT_PUBLIC_API_URL;

  // ============================================================================
  // Data Fetching
  // ============================================================================

  const fetchData = useCallback(async () => {
    if (!accessToken) return;
    setIsLoading(true);

    try {
      const [friendsRes, pendingRes, codeRes] = await Promise.all([
        fetch(`${API_URL}/friends/`, {
          headers: { Authorization: `Bearer ${accessToken}` }
        }),
        fetch(`${API_URL}/friends/pending`, {
          headers: { Authorization: `Bearer ${accessToken}` }
        }),
        fetch(`${API_URL}/friends/code`, {
          headers: { Authorization: `Bearer ${accessToken}` }
        })
      ]);

      if (friendsRes.ok) {
        const data = await friendsRes.json();
        setFriends(data.friends || []);
      }

      if (pendingRes.ok) {
        const data = await pendingRes.json();
        setIncomingRequests(data.incoming || []);
        setOutgoingRequests(data.outgoing || []);
      }

      if (codeRes.ok) {
        const data = await codeRes.json();
        setFriendCode(data.friend_code || '');
      }
    } catch (err) {
      console.error('Failed to fetch friends data:', err);
      setError('Erreur de chargement des données');
    } finally {
      setIsLoading(false);
    }
  }, [accessToken, API_URL]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // ============================================================================
  // Computed Values
  // ============================================================================

  const filteredFriends = friends.filter((f) =>
    f.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (f.character_name && f.character_name.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const onlineFriends = friends.filter((f) => f.is_online).length;

  // ============================================================================
  // Handlers
  // ============================================================================

  const showSuccess = (message: string) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(''), 3000);
  };

  const showError = (message: string) => {
    setError(message);
    setTimeout(() => setError(''), 5000);
  };

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
        showSuccess('Demande acceptée ! 🎉');
      } else {
        const data = await res.json();
        showError(data.detail || 'Erreur lors de l\'acceptation');
      }
    } catch (err) {
      showError('Erreur lors de l\'acceptation');
    }
  };

  const handleRejectRequest = async (requestId: string) => {
    try {
      const res = await fetch(`${API_URL}/friends/reject/${requestId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      if (res.ok || res.status === 204) {
        setIncomingRequests(prev => prev.filter(r => r.id !== requestId));
        showSuccess('Demande refusée');
      }
    } catch (err) {
      showError('Erreur lors du refus');
    }
  };

  const handleCancelRequest = async (requestId: string) => {
    try {
      const res = await fetch(`${API_URL}/friends/reject/${requestId}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      if (res.ok || res.status === 204) {
        setOutgoingRequests(prev => prev.filter(r => r.id !== requestId));
        showSuccess('Demande annulée');
      }
    } catch (err) {
      showError('Erreur lors de l\'annulation');
    }
  };

  const openDeleteModal = (friend: Friend) => {
    setDeleteModal({ isOpen: true, friend, isLoading: false });
  };

  const closeDeleteModal = () => {
    setDeleteModal({ isOpen: false, friend: null, isLoading: false });
  };

  const handleRemoveFriend = async () => {
    if (!deleteModal.friend) return;
    
    setDeleteModal(prev => ({ ...prev, isLoading: true }));
    
    try {
      const res = await fetch(`${API_URL}/friends/${deleteModal.friend.user_id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      if (res.ok || res.status === 204) {
        setFriends(prev => prev.filter(f => f.user_id !== deleteModal.friend!.user_id));
        showSuccess('Ami supprimé');
        closeDeleteModal();
      } else {
        showError('Erreur lors de la suppression');
      }
    } catch (err) {
      showError('Erreur lors de la suppression');
    } finally {
      setDeleteModal(prev => ({ ...prev, isLoading: false }));
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
        showSuccess('Demande envoyée ! 📨');
        
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
        if (data.detail?.includes('already friends')) {
          showError('Vous êtes déjà amis !');
        } else if (data.detail?.includes('already pending')) {
          showError('Demande déjà envoyée');
        } else if (data.detail?.includes('Invalid')) {
          showError('Code ami invalide');
        } else if (data.detail?.includes('yourself')) {
          showError('Tu ne peux pas t\'ajouter toi-même ! 😄');
        } else {
          showError(data.detail || 'Erreur lors de l\'envoi');
        }
      }
    } catch (err) {
      showError('Erreur lors de l\'envoi de la demande');
    } finally {
      setIsSubmitting(false);
    }
  };

  const copyFriendCode = async () => {
    try {
      await navigator.clipboard.writeText(friendCode);
      showSuccess('Code copié ! 📋');
    } catch (err) {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = friendCode;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      showSuccess('Code copié ! 📋');
    }
  };

  // ============================================================================
  // Loading State
  // ============================================================================

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header Skeleton */}
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <div className="h-8 w-48 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div className="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>
          <div className="h-10 w-28 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse" />
        </div>

        {/* Friend Code Skeleton */}
        <FriendCodeSkeleton />

        {/* Search Skeleton */}
        <div className="h-12 w-full bg-gray-200 dark:bg-gray-700 rounded-xl animate-pulse" />

        {/* Friends List Skeleton */}
        <div className="space-y-3">
          <FriendCardSkeleton />
          <FriendCardSkeleton />
          <FriendCardSkeleton />
        </div>
      </div>
    );
  }

  // ============================================================================
  // Main Render
  // ============================================================================

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
            {friends.length === 0 
              ? "Ajoute des amis pour comparer tes progrès !"
              : `${onlineFriends} en ligne sur ${friends.length} ami${friends.length > 1 ? 's' : ''}`
            }
          </p>
        </div>
        <Button onClick={() => setShowAddModal(true)}>
          <UserPlus className="w-5 h-5 mr-2" />
          Ajouter
        </Button>
      </div>

      {/* Success/Error Messages */}
      <AnimatePresence>
        {successMessage && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-green-600 dark:text-green-400"
          >
            {successMessage}
          </motion.div>
        )}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* ================================================================== */}
      {/* SECTION 3: Ajouter un ami - Friend Code Display */}
      {/* ================================================================== */}
      <Card variant="bordered" padding="md" className="bg-gradient-to-r from-primary-500/10 to-accent-500/10 border-primary-500/30">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Ton code ami</p>
            <p className="text-2xl font-bold text-primary-500 tracking-wider font-mono">{friendCode}</p>
            <p className="text-xs text-gray-400 mt-1">Partage ce code pour recevoir des demandes d'ami</p>
          </div>
          <Button variant="secondary" onClick={copyFriendCode} className="shrink-0">
            <Copy className="w-4 h-4 mr-2" />
            Copier
          </Button>
        </div>
      </Card>

      {/* ================================================================== */}
      {/* SECTION 2: Demandes - Incoming Requests */}
      {/* ================================================================== */}
      {incomingRequests.length > 0 && (
        <Card variant="bordered" padding="lg" className="border-primary-500/50">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <div className="relative">
              <Clock className="w-5 h-5 text-primary-500" />
              <span className="absolute -top-1 -right-1 w-2 h-2 bg-primary-500 rounded-full animate-pulse" />
            </div>
            Demandes reçues ({incomingRequests.length})
          </h3>
          <div className="space-y-3">
            {incomingRequests.map((request) => (
              <motion.div
                key={request.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-white font-bold">
                    {request.from_username.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">{request.from_username}</p>
                    <p className="text-sm text-gray-500">Niveau {request.from_level}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => handleAcceptRequest(request.id)} title="Accepter">
                    <Check className="w-4 h-4" />
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => handleRejectRequest(request.id)} title="Refuser">
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </motion.div>
            ))}
          </div>
        </Card>
      )}

      {/* ================================================================== */}
      {/* SECTION 2: Demandes - Outgoing Requests */}
      {/* ================================================================== */}
      {outgoingRequests.length > 0 && (
        <Card variant="bordered" padding="lg">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-gray-400" />
            Demandes envoyées ({outgoingRequests.length})
          </h3>
          <div className="space-y-3">
            {outgoingRequests.map((request) => (
              <motion.div
                key={request.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center text-gray-600 dark:text-gray-300 font-bold">
                    {(request.to_username || '?').charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">
                      {request.to_username || 'Utilisateur'}
                    </p>
                    <Badge size="sm" variant="warning" className="mt-1">
                      <Clock className="w-3 h-3 mr-1" />
                      En attente
                    </Badge>
                  </div>
                </div>
                <Button 
                  size="sm" 
                  variant="ghost" 
                  onClick={() => handleCancelRequest(request.id)}
                  className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                  title="Annuler la demande"
                >
                  <X className="w-4 h-4 mr-1" />
                  Annuler
                </Button>
              </motion.div>
            ))}
          </div>
        </Card>
      )}

      {/* ================================================================== */}
      {/* SECTION 1: Mes amis - Search */}
      {/* ================================================================== */}
      {friends.length > 0 && (
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Rechercher un ami..."
            className="w-full pl-10 pr-4 py-3 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900 dark:text-white placeholder-gray-400"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <X className="w-4 h-4 text-gray-400" />
            </button>
          )}
        </div>
      )}

      {/* ================================================================== */}
      {/* SECTION 1: Mes amis - Friends List */}
      {/* ================================================================== */}
      <div className="space-y-3">
        <AnimatePresence mode="popLayout">
          {filteredFriends.map((friend, index) => (
            <motion.div
              key={friend.friendship_id}
              layout
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -100 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card variant="bordered" className="flex items-center gap-4 hover:border-primary-500/50 transition-colors">
                {/* Avatar */}
                <div className="relative shrink-0">
                  {friend.character_class ? (
                    <SpriteAvatar
                      characterClass={friend.character_class}
                      size="md"
                    />
                  ) : (
                    <div className="w-14 h-14 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-xl font-bold text-white">
                      {friend.username.charAt(0).toUpperCase()}
                    </div>
                  )}
                  {/* Online indicator */}
                  <div
                    className={cn(
                      'absolute bottom-0 right-0 w-4 h-4 rounded-full border-2 border-white dark:border-gray-800',
                      friend.is_online ? 'bg-green-500' : 'bg-gray-400'
                    )}
                  />
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                      {friend.character_name || friend.username}
                    </h3>
                    <Badge size="sm" variant={friend.is_online ? 'success' : 'default'}>
                      {friend.is_online ? 'En ligne' : 'Hors ligne'}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4 mt-1 text-sm text-gray-500 dark:text-gray-400 flex-wrap">
                    <span className="flex items-center gap-1">
                      ⭐ Niveau {friend.level}
                    </span>
                    {friend.current_streak > 0 && (
                      <span className="flex items-center gap-1 text-orange-500">
                        <Flame className="w-4 h-4" />
                        {friend.current_streak} jour{friend.current_streak > 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 shrink-0">
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => window.location.href = `/profile/${friend.user_id}`}
                    title="Voir le profil"
                  >
                    <ExternalLink className="w-4 h-4 sm:mr-1" />
                    <span className="hidden sm:inline">Profil</span>
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => openDeleteModal(friend)}
                    className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                    title="Supprimer cet ami"
                  >
                    <UserX className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Empty State */}
        {friends.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-16"
          >
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
              <Users className="w-10 h-10 text-primary-500" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Invite tes amis ! 🎮
            </h3>
            <p className="text-gray-500 dark:text-gray-400 max-w-sm mx-auto mb-6">
              Ajoute des amis pour comparer vos progrès, vous challenger et rester motivés ensemble !
            </p>
            <Button onClick={() => setShowAddModal(true)} size="lg">
              <UserPlus className="w-5 h-5 mr-2" />
              Ajouter mon premier ami
            </Button>
          </motion.div>
        )}

        {/* No Search Results */}
        {friends.length > 0 && filteredFriends.length === 0 && searchQuery && (
          <div className="text-center py-12">
            <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">
              Aucun ami trouvé pour "{searchQuery}"
            </p>
            <Button variant="ghost" onClick={() => setSearchQuery('')} className="mt-2">
              Effacer la recherche
            </Button>
          </div>
        )}
      </div>

      {/* ================================================================== */}
      {/* Add Friend Modal */}
      {/* ================================================================== */}
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
              className="w-full max-w-md"
            >
              <Card variant="elevated" padding="lg" className="bg-white dark:bg-gray-800">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                    Ajouter un ami
                  </h2>
                  <button
                    onClick={() => setShowAddModal(false)}
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
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

                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Demande le code ami de ton pote et entre-le ci-dessus pour lui envoyer une demande.
                  </p>

                  <div className="flex gap-3 pt-2">
                    <Button 
                      variant="secondary" 
                      onClick={() => setShowAddModal(false)} 
                      className="flex-1"
                      disabled={isSubmitting}
                    >
                      Annuler
                    </Button>
                    <Button 
                      onClick={handleSendRequest} 
                      className="flex-1" 
                      disabled={isSubmitting || !newFriendCode.trim()}
                    >
                      {isSubmitting ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <>
                          <UserPlus className="w-4 h-4 mr-2" />
                          Envoyer
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </Card>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Delete Confirmation Modal */}
      <AnimatePresence>
        <DeleteConfirmModal
          isOpen={deleteModal.isOpen}
          friendName={deleteModal.friend?.character_name || deleteModal.friend?.username || ''}
          onConfirm={handleRemoveFriend}
          onCancel={closeDeleteModal}
          isLoading={deleteModal.isLoading}
        />
      </AnimatePresence>
    </div>
  );
}
