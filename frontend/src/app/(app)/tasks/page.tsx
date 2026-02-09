'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, X, Calendar, Flag, CheckCircle2, Circle, Trash2, Edit2 } from 'lucide-react';
import { Button, Input, Card, Badge } from '@/components/ui';
import { cn, getPriorityColor } from '@/lib/utils';
import type { Task, TaskPriority } from '@/types';

const initialTasks: Task[] = [
  {
    id: '1',
    userId: '1',
    title: 'Finir le rapport trimestriel',
    description: 'Compiler les données Q4 et rédiger le résumé',
    priority: 'high',
    dueDate: new Date(Date.now() + 86400000).toISOString(),
    completed: false,
    xpReward: 50,
    goldReward: 20,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    userId: '1',
    title: 'Rendez-vous dentiste',
    description: 'Contrôle annuel',
    priority: 'medium',
    dueDate: new Date(Date.now() + 172800000).toISOString(),
    completed: false,
    xpReward: 20,
    goldReward: 10,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '3',
    userId: '1',
    title: 'Répondre aux emails',
    priority: 'low',
    completed: true,
    xpReward: 15,
    goldReward: 5,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '4',
    userId: '1',
    title: 'Préparer la présentation',
    description: 'Slides pour la réunion de vendredi',
    priority: 'urgent',
    dueDate: new Date(Date.now() + 43200000).toISOString(),
    completed: false,
    xpReward: 75,
    goldReward: 30,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

const priorityLabels: Record<TaskPriority, string> = {
  low: 'Basse',
  medium: 'Moyenne',
  high: 'Haute',
  urgent: 'Urgente',
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [showModal, setShowModal] = useState(false);
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all');
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'medium' as TaskPriority,
    dueDate: '',
  });

  const handleComplete = (taskId: string) => {
    setTasks((prev) =>
      prev.map((t) =>
        t.id === taskId ? { ...t, completed: !t.completed, updatedAt: new Date().toISOString() } : t
      )
    );
  };

  const handleDelete = (taskId: string) => {
    setTasks((prev) => prev.filter((t) => t.id !== taskId));
  };

  const handleAddTask = () => {
    if (!newTask.title.trim()) return;

    const task: Task = {
      id: Date.now().toString(),
      userId: '1',
      title: newTask.title,
      description: newTask.description || undefined,
      priority: newTask.priority,
      dueDate: newTask.dueDate || undefined,
      completed: false,
      xpReward: { low: 15, medium: 25, high: 50, urgent: 75 }[newTask.priority],
      goldReward: { low: 5, medium: 10, high: 20, urgent: 30 }[newTask.priority],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    setTasks((prev) => [task, ...prev]);
    setNewTask({ title: '', description: '', priority: 'medium', dueDate: '' });
    setShowModal(false);
  };

  const filteredTasks = tasks.filter((task) => {
    if (filter === 'completed') return task.completed;
    if (filter === 'pending') return !task.completed;
    return true;
  });

  const pendingCount = tasks.filter((t) => !t.completed).length;
  const completedCount = tasks.filter((t) => t.completed).length;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Mes Tâches</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">
            {pendingCount} en attente • {completedCount} terminées
          </p>
        </div>
        <Button onClick={() => setShowModal(true)}>
          <Plus className="w-5 h-5 mr-2" />
          Nouvelle tâche
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        {(['all', 'pending', 'completed'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={cn(
              'px-4 py-2 rounded-lg text-sm font-medium transition-all',
              filter === f
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
            )}
          >
            {f === 'all' ? 'Toutes' : f === 'pending' ? 'En attente' : 'Terminées'}
          </button>
        ))}
      </div>

      {/* Tasks List */}
      <div className="space-y-3">
        <AnimatePresence mode="popLayout">
          {filteredTasks.map((task) => (
            <motion.div
              key={task.id}
              layout
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, x: -100 }}
            >
              <Card
                variant="bordered"
                className={cn(
                  'flex items-start gap-4',
                  task.completed && 'bg-green-50 dark:bg-green-900/20'
                )}
              >
                <button
                  onClick={() => handleComplete(task.id)}
                  className={cn(
                    'mt-1 flex-shrink-0 transition-colors',
                    task.completed ? 'text-green-500' : 'text-gray-400 hover:text-primary-500'
                  )}
                >
                  {task.completed ? (
                    <CheckCircle2 className="w-6 h-6" />
                  ) : (
                    <Circle className="w-6 h-6" />
                  )}
                </button>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3
                      className={cn(
                        'font-semibold text-gray-900 dark:text-white',
                        task.completed && 'line-through text-gray-500'
                      )}
                    >
                      {task.title}
                    </h3>
                    <Badge
                      variant={
                        task.priority === 'urgent'
                          ? 'danger'
                          : task.priority === 'high'
                          ? 'warning'
                          : 'default'
                      }
                      size="sm"
                    >
                      {priorityLabels[task.priority]}
                    </Badge>
                  </div>

                  {task.description && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">{task.description}</p>
                  )}

                  <div className="flex items-center gap-4 text-sm">
                    {task.dueDate && (
                      <div className="flex items-center gap-1 text-gray-500 dark:text-gray-400">
                        <Calendar className="w-4 h-4" />
                        <span>{new Date(task.dueDate).toLocaleDateString('fr-FR')}</span>
                      </div>
                    )}
                    <span className="text-game-xp">+{task.xpReward} XP</span>
                    <span className="text-game-gold">+{task.goldReward} 🪙</span>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(task.id)}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </Card>
            </motion.div>
          ))}
        </AnimatePresence>

        {filteredTasks.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              {filter === 'all' ? 'Aucune tâche' : filter === 'pending' ? 'Aucune tâche en attente' : 'Aucune tâche terminée'}
            </p>
          </div>
        )}
      </div>

      {/* Add Task Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
            onClick={() => setShowModal(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <Card variant="elevated" padding="lg" className="w-full max-w-md bg-white dark:bg-gray-800">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-gray-900 dark:text-white">Nouvelle tâche</h2>
                  <button
                    onClick={() => setShowModal(false)}
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    <X className="w-5 h-5 text-gray-500" />
                  </button>
                </div>

                <div className="space-y-4">
                  <Input
                    label="Titre"
                    value={newTask.title}
                    onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                    placeholder="Ex: Finir le projet"
                  />

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                      Description (optionnel)
                    </label>
                    <textarea
                      value={newTask.description}
                      onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                      placeholder="Détails de la tâche..."
                      className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      rows={3}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                        Priorité
                      </label>
                      <select
                        value={newTask.priority}
                        onChange={(e) => setNewTask({ ...newTask, priority: e.target.value as TaskPriority })}
                        className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="low">Basse</option>
                        <option value="medium">Moyenne</option>
                        <option value="high">Haute</option>
                        <option value="urgent">Urgente</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                        Échéance
                      </label>
                      <input
                        type="date"
                        value={newTask.dueDate}
                        onChange={(e) => setNewTask({ ...newTask, dueDate: e.target.value })}
                        className="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      />
                    </div>
                  </div>

                  <div className="flex gap-3 pt-4">
                    <Button variant="secondary" onClick={() => setShowModal(false)} className="flex-1">
                      Annuler
                    </Button>
                    <Button onClick={handleAddTask} className="flex-1">
                      <Plus className="w-5 h-5 mr-2" />
                      Créer
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
