'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, X, Loader2, AlertCircle, RefreshCw, CheckCircle2, Circle, Calendar, Sparkles, Coins, Wand2 } from 'lucide-react';
import { Button, Input, Card, Badge } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import { cn, getPriorityColor } from '@/lib/utils';

type Priority = 'low' | 'medium' | 'high' | 'urgent';

interface TaskResponse {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  priority: Priority;
  due_date: string | null;
  completed: boolean;
  completed_at: string | null;
  xp_reward: number;
  coin_reward: number;
  difficulty: string | null;
  use_ai_evaluation: boolean;
  created_at: string;
  updated_at: string;
}

interface Task {
  id: string;
  title: string;
  description: string;
  priority: Priority;
  dueDate: string | null;
  completed: boolean;
  xpReward: number;
  goldReward: number;
  useAI: boolean;
}

function transformTask(t: TaskResponse): Task {
  return {
    id: t.id,
    title: t.title,
    description: t.description || '',
    priority: t.priority,
    dueDate: t.due_date,
    completed: t.completed,
    xpReward: t.xp_reward,
    goldReward: t.coin_reward,
    useAI: t.use_ai_evaluation,
  };
}

export default function TasksPage() {
  const { accessToken, fetchCharacter } = useAuthStore();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [completing, setCompleting] = useState<string | null>(null);
  
  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<Priority>('medium');
  const [dueDate, setDueDate] = useState('');
  const [useAI, setUseAI] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://habit.apps.ilanewep.cloud/api';

  const fetchTasks = useCallback(async () => {
    if (!accessToken) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/tasks/`, {
        headers: { 'Authorization': `Bearer ${accessToken}` },
      });

      if (!response.ok) throw new Error('Erreur lors du chargement');

      const data: TaskResponse[] = await response.json();
      setTasks(data.map(transformTask));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  }, [accessToken, API_URL]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accessToken || !title.trim()) return;

    setCreating(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/tasks/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim() || null,
          priority,
          due_date: dueDate || null,
          use_ai_evaluation: useAI,
        }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Erreur lors de la création');
      }

      setTitle('');
      setDescription('');
      setPriority('medium');
      setDueDate('');
      setUseAI(false);
      setShowForm(false);
      await fetchTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur');
    } finally {
      setCreating(false);
    }
  };

  const handleComplete = async (taskId: string) => {
    if (!accessToken || completing) return;

    setCompleting(taskId);
    try {
      const response = await fetch(`${API_URL}/tasks/${taskId}/complete`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${accessToken}` },
      });

      if (!response.ok) throw new Error('Erreur');
      await Promise.all([fetchTasks(), fetchCharacter()]);
    } catch (err) {
      setError('Erreur lors de la complétion');
    } finally {
      setCompleting(null);
    }
  };

  const handleDelete = async (taskId: string) => {
    if (!accessToken || !confirm('Supprimer cette tâche ?')) return;

    try {
      await fetch(`${API_URL}/tasks/${taskId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${accessToken}` },
      });
      await fetchTasks();
    } catch (err) {
      setError('Erreur lors de la suppression');
    }
  };

  const pendingTasks = tasks.filter(t => !t.completed);
  const completedTasks = tasks.filter(t => t.completed);

  const priorityLabels: Record<Priority, string> = {
    low: 'Basse',
    medium: 'Moyenne',
    high: 'Haute',
    urgent: 'Urgente',
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Mes Tâches</h1>
          <p className="text-gray-500 mt-1">{pendingTasks.length} en attente • {completedTasks.length} terminée{completedTasks.length > 1 ? 's' : ''}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" onClick={fetchTasks} disabled={loading}>
            <RefreshCw className={loading ? 'animate-spin' : ''} />
          </Button>
          <Button onClick={() => setShowForm(!showForm)} className="gap-2">
            {showForm ? <X /> : <Plus />}
            {showForm ? 'Annuler' : 'Nouvelle tâche'}
          </Button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-3 p-4 rounded-lg bg-red-100 dark:bg-red-900/30 text-red-600">
          <AlertCircle className="w-5 h-5" />
          <p>{error}</p>
          <button onClick={() => setError(null)} className="ml-auto"><X className="w-4 h-4" /></button>
        </div>
      )}

      {/* Create Form */}
      <AnimatePresence>
        {showForm && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
            <Card>
              <form onSubmit={handleCreate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Titre *</label>
                  <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Ex: Finir le rapport" required />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
                  <Input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Détails..." />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Priorité</label>
                    <select
                      value={priority}
                      onChange={(e) => setPriority(e.target.value as Priority)}
                      className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800"
                    >
                      <option value="low">Basse</option>
                      <option value="medium">Moyenne</option>
                      <option value="high">Haute</option>
                      <option value="urgent">Urgente</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Échéance</label>
                    <input
                      type="date"
                      value={dueDate}
                      onChange={(e) => setDueDate(e.target.value)}
                      className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    />
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="useAI"
                    checked={useAI}
                    onChange={(e) => setUseAI(e.target.checked)}
                    className="rounded border-gray-300 text-primary-500"
                  />
                  <label htmlFor="useAI" className="text-sm text-gray-700 dark:text-gray-300 flex items-center gap-2">
                    <Wand2 className="w-4 h-4 text-purple-500" />
                    Évaluation IA (détermine XP/Or automatiquement)
                  </label>
                </div>

                <div className="flex justify-end gap-3">
                  <Button type="button" variant="ghost" onClick={() => setShowForm(false)}>Annuler</Button>
                  <Button type="submit" disabled={creating || !title.trim()}>
                    {creating ? <Loader2 className="animate-spin" /> : 'Créer'}
                  </Button>
                </div>
              </form>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading */}
      {loading && tasks.length === 0 ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-8 h-8 animate-spin text-primary-500" />
        </div>
      ) : (
        <>
          {/* Pending */}
          {pendingTasks.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">En attente ({pendingTasks.length})</h2>
              <div className="space-y-3">
                {pendingTasks.map((task) => (
                  <Card key={task.id} className="flex items-start gap-4">
                    <button
                      onClick={() => handleComplete(task.id)}
                      disabled={completing === task.id}
                      className="mt-1 shrink-0"
                    >
                      {completing === task.id ? (
                        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
                      ) : (
                        <Circle className="w-6 h-6 text-gray-400 hover:text-green-500 transition-colors" />
                      )}
                    </button>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-gray-900 dark:text-white truncate">{task.title}</h3>
                        <Badge variant={task.priority === 'urgent' ? 'danger' : task.priority === 'high' ? 'warning' : 'default'} size="sm">
                          {priorityLabels[task.priority]}
                        </Badge>
                        {task.useAI && <Wand2 className="w-4 h-4 text-purple-500" />}
                      </div>
                      {task.description && <p className="text-sm text-gray-500 truncate">{task.description}</p>}
                      <div className="flex items-center gap-4 mt-2 text-sm">
                        <span className="text-game-xp flex items-center gap-1"><Sparkles className="w-4 h-4" />+{task.xpReward} XP</span>
                        <span className="text-game-gold flex items-center gap-1"><Coins className="w-4 h-4" />+{task.goldReward}</span>
                        {task.dueDate && (
                          <span className="text-gray-500 flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {new Date(task.dueDate).toLocaleDateString('fr-FR')}
                          </span>
                        )}
                      </div>
                    </div>
                    <button onClick={() => handleDelete(task.id)} className="text-gray-400 hover:text-red-500">
                      <X className="w-5 h-5" />
                    </button>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Completed */}
          {completedTasks.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-500">Terminées ({completedTasks.length})</h2>
              <div className="space-y-3 opacity-60">
                {completedTasks.slice(0, 5).map((task) => (
                  <Card key={task.id} className="flex items-center gap-4">
                    <CheckCircle2 className="w-6 h-6 text-green-500 shrink-0" />
                    <h3 className="font-medium text-gray-500 line-through truncate">{task.title}</h3>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Empty */}
          {tasks.length === 0 && !loading && (
            <div className="text-center py-12">
              <p className="text-gray-500 mb-4">Aucune tâche pour le moment.</p>
              <Button onClick={() => setShowForm(true)} className="gap-2">
                <Plus className="w-5 h-5" /> Créer ma première tâche
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
