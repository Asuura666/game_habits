'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Settings,
  User,
  Bell,
  Shield,
  Palette,
  Globe,
  LogOut,
  Moon,
  Sun,
  Smartphone,
  Mail,
  Lock,
  Trash2,
  Save,
} from 'lucide-react';
import { Card, Button, Input, Badge } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';

type SettingsSection = 'profile' | 'notifications' | 'appearance' | 'security' | 'danger';

const sections = [
  { id: 'profile', label: 'Profil', icon: User },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'appearance', label: 'Apparence', icon: Palette },
  { id: 'security', label: 'Sécurité', icon: Shield },
  { id: 'danger', label: 'Zone de danger', icon: Trash2 },
] as const;

export default function SettingsPage() {
  const { user, logout, updateUser } = useAuthStore();
  const [activeSection, setActiveSection] = useState<SettingsSection>('profile');
  const [isSaving, setIsSaving] = useState(false);
  
  // Profile state
  const [username, setUsername] = useState(user?.username || '');
  const [email, setEmail] = useState(user?.email || '');
  
  // Notification state
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    streak: true,
    friends: true,
    achievements: true,
  });
  
  // Appearance state
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('dark');
  const [language, setLanguage] = useState('fr');

  const handleSaveProfile = async () => {
    setIsSaving(true);
    await new Promise((r) => setTimeout(r, 1000));
    updateUser({ username, email });
    setIsSaving(false);
  };

  const renderSection = () => {
    switch (activeSection) {
      case 'profile':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Informations du profil
              </h3>
              
              <div className="flex items-center gap-6 mb-6">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-3xl font-bold text-white">
                  {username.charAt(0).toUpperCase()}
                </div>
                <Button variant="secondary">Changer l'avatar</Button>
              </div>

              <div className="space-y-4 max-w-md">
                <Input
                  label="Nom d'utilisateur"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  icon={<User className="w-5 h-5" />}
                />
                <Input
                  label="Adresse email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  icon={<Mail className="w-5 h-5" />}
                />
              </div>
            </div>

            <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
              <Button onClick={handleSaveProfile} isLoading={isSaving}>
                <Save className="w-5 h-5 mr-2" />
                Enregistrer les modifications
              </Button>
            </div>
          </div>
        );

      case 'notifications':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Préférences de notification
            </h3>
            
            <div className="space-y-4">
              {[
                { key: 'email', label: 'Notifications par email', description: 'Recevoir des résumés quotidiens', icon: Mail },
                { key: 'push', label: 'Notifications push', description: 'Recevoir des alertes sur votre appareil', icon: Smartphone },
                { key: 'streak', label: 'Rappels de série', description: 'Être notifié pour maintenir votre série', icon: Bell },
                { key: 'friends', label: 'Activité des amis', description: 'Voir quand vos amis progressent', icon: User },
                { key: 'achievements', label: 'Succès débloqués', description: 'Être notifié des nouveaux succès', icon: Shield },
              ].map(({ key, label, description, icon: Icon }) => (
                <div
                  key={key}
                  className="flex items-center justify-between p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                      <Icon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{label}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{description}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setNotifications((prev) => ({ ...prev, [key]: !prev[key as keyof typeof notifications] }))}
                    className={cn(
                      'relative w-12 h-6 rounded-full transition-colors',
                      notifications[key as keyof typeof notifications] ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'
                    )}
                  >
                    <span
                      className={cn(
                        'absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white transition-transform',
                        notifications[key as keyof typeof notifications] && 'translate-x-6'
                      )}
                    />
                  </button>
                </div>
              ))}
            </div>
          </div>
        );

      case 'appearance':
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Thème</h3>
              <div className="flex gap-3">
                {(['light', 'dark', 'system'] as const).map((t) => (
                  <button
                    key={t}
                    onClick={() => setTheme(t)}
                    className={cn(
                      'flex items-center gap-2 px-4 py-3 rounded-xl border-2 transition-all',
                      theme === t
                        ? 'border-primary-500 bg-primary-500/10'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    )}
                  >
                    {t === 'light' && <Sun className="w-5 h-5" />}
                    {t === 'dark' && <Moon className="w-5 h-5" />}
                    {t === 'system' && <Settings className="w-5 h-5" />}
                    <span className="capitalize">{t === 'system' ? 'Système' : t === 'light' ? 'Clair' : 'Sombre'}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Langue</h3>
              <div className="flex items-center gap-3 max-w-xs">
                <Globe className="w-5 h-5 text-gray-400" />
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="flex-1 px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                >
                  <option value="fr">Français</option>
                  <option value="en">English</option>
                  <option value="es">Español</option>
                  <option value="de">Deutsch</option>
                </select>
              </div>
            </div>
          </div>
        );

      case 'security':
        return (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Sécurité du compte
            </h3>

            <Card variant="bordered" padding="md">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                    <Lock className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Mot de passe</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Dernière modification il y a 30 jours</p>
                  </div>
                </div>
                <Button variant="secondary">Modifier</Button>
              </div>
            </Card>

            <Card variant="bordered" padding="md">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                    <Shield className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Authentification à deux facteurs</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Sécurisez votre compte avec la 2FA</p>
                  </div>
                </div>
                <Badge variant="warning">Désactivé</Badge>
              </div>
            </Card>

            <Card variant="bordered" padding="md">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
                    <Smartphone className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Sessions actives</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">2 appareils connectés</p>
                  </div>
                </div>
                <Button variant="ghost" className="text-red-500">Déconnecter tout</Button>
              </div>
            </Card>
          </div>
        );

      case 'danger':
        return (
          <div className="space-y-6">
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30">
              <h3 className="text-lg font-semibold text-red-500 mb-2">Zone de danger</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Ces actions sont irréversibles. Procédez avec prudence.
              </p>
            </div>

            <Card variant="bordered" padding="md" className="border-red-500/30">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">Supprimer le compte</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Supprimer définitivement votre compte et toutes vos données
                  </p>
                </div>
                <Button variant="danger">Supprimer</Button>
              </div>
            </Card>

            <Card variant="bordered" padding="md">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">Exporter les données</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Télécharger une copie de vos données
                  </p>
                </div>
                <Button variant="secondary">Exporter</Button>
              </div>
            </Card>
          </div>
        );
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
          <Settings className="w-8 h-8 text-primary-500" />
          Paramètres
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Gérez votre compte et vos préférences
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Sidebar */}
        <Card variant="bordered" padding="sm" className="md:col-span-1 h-fit">
          <nav className="space-y-1">
            {sections.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveSection(id)}
                className={cn(
                  'flex items-center gap-3 w-full px-4 py-3 rounded-lg text-left transition-all',
                  activeSection === id
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800',
                  id === 'danger' && activeSection !== id && 'text-red-500'
                )}
              >
                <Icon className="w-5 h-5" />
                {label}
              </button>
            ))}
            
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={() => logout()}
                className="flex items-center gap-3 w-full px-4 py-3 rounded-lg text-left text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all"
              >
                <LogOut className="w-5 h-5" />
                Déconnexion
              </button>
            </div>
          </nav>
        </Card>

        {/* Content */}
        <Card variant="bordered" padding="lg" className="md:col-span-3">
          <motion.div
            key={activeSection}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.2 }}
          >
            {renderSection()}
          </motion.div>
        </Card>
      </div>
    </div>
  );
}
