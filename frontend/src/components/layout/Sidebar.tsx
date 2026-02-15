'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Target,
  CheckSquare,
  User,
  ShoppingBag,
  Package,
  Swords,
  Users,
  Trophy,
  Award,
  BarChart3,
  LogOut,
  Flame,
  X,
} from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { ProgressBar } from '@/components/ui';

// Feature flags for hiding incomplete features
const FEATURES = {
  combat: false,  // Combat not connected to backend yet
  tasks: true,    // Tasks feature enabled
};

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', enabled: true },
  { href: '/habits', icon: Target, label: 'Habitudes', enabled: true },
  { href: '/tasks', icon: CheckSquare, label: 'Tâches', enabled: FEATURES.tasks },
  { href: '/character', icon: User, label: 'Personnage', enabled: true },
  { href: '/shop', icon: ShoppingBag, label: 'Boutique', enabled: true },
  { href: '/inventory', icon: Package, label: 'Inventaire', enabled: true },
  { href: '/combat', icon: Swords, label: 'Combat', enabled: FEATURES.combat },
  { href: '/friends', icon: Users, label: 'Amis', enabled: true },
  { href: '/leaderboard', icon: Trophy, label: 'Classement', enabled: true },
  { href: '/badges', icon: Award, label: 'Badges', enabled: true },
  { href: '/stats', icon: BarChart3, label: 'Statistiques', enabled: true },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const pathname = usePathname();
  const { user, character, logout } = useAuthStore();

  // Use character coins if available, fallback to user gold
  const coins = character?.coins ?? user?.gold ?? 0;

  const handleNavClick = () => {
    // Close sidebar on mobile after navigation
    if (onClose) {
      onClose();
    }
  };

  // Filter out disabled features
  const visibleNavItems = navItems.filter(item => item.enabled);

  const sidebarContent = (
    <>
      {/* Logo */}
      <div className="p-4 lg:p-6 border-b border-gray-800 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-3" onClick={handleNavClick}>
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
            <Flame className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold">HabitQuest</span>
        </Link>
        {/* Close button for mobile - touch-friendly size (48x48) */}
        <button
          onClick={onClose}
          className="lg:hidden p-3 -mr-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors min-w-[48px] min-h-[48px] flex items-center justify-center"
          aria-label="Fermer le menu"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      {/* User Stats */}
      {user && (
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-lg font-bold shrink-0">
              {user.username.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold truncate">{user.username}</p>
              <p className="text-sm text-gray-400">Niveau {character?.level ?? user.level}</p>
            </div>
          </div>
          
          <div className="space-y-2">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-game-xp">XP</span>
                <span>{character?.xp ?? user.xp}/{character?.xp_to_next_level ?? user.xpToNextLevel}</span>
              </div>
              <ProgressBar value={character?.xp ?? user.xp} max={character?.xp_to_next_level ?? user.xpToNextLevel} variant="xp" size="sm" />
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-game-hp">HP</span>
                <span>{character?.hp ?? user.hp}/{character?.max_hp ?? user.maxHp}</span>
              </div>
              <ProgressBar value={character?.hp ?? user.hp} max={character?.max_hp ?? user.maxHp} variant="hp" size="sm" />
            </div>
          </div>

          <div className="flex items-center justify-between mt-3 text-sm">
            <div className="flex items-center gap-1">
              <span className="text-game-gold">🪙</span>
              <span>{coins}</span>
            </div>
            <div className="flex items-center gap-1">
              <Flame className="w-4 h-4 text-orange-500" />
              <span>{character?.streak ?? user.streak} jours</span>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 p-4 overflow-y-auto">
        <ul className="space-y-1">
          {visibleNavItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  onClick={handleNavClick}
                  className={cn(
                    // Touch-friendly: min 44px height with py-3
                    'flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200 relative min-h-[44px]',
                    isActive
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800 active:bg-gray-700'
                  )}
                >
                  <Icon className="w-5 h-5 shrink-0" />
                  <span>{item.label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="activeIndicator"
                      className="absolute right-0 w-1 h-8 bg-primary-400 rounded-l-full"
                    />
                  )}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Logout - touch-friendly */}
      <div className="p-4 border-t border-gray-800">
        <button
          onClick={() => {
            logout();
            handleNavClick();
          }}
          className="flex items-center gap-3 w-full px-3 py-3 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 active:bg-gray-700 transition-all duration-200 min-h-[44px]"
        >
          <LogOut className="w-5 h-5" />
          <span>Déconnexion</span>
        </button>
      </div>
    </>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex fixed left-0 top-0 z-40 h-screen w-64 bg-gray-900 text-white flex-col">
        {sidebarContent}
      </aside>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={onClose}
              className="lg:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
            />
            
            {/* Mobile Sidebar */}
            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="lg:hidden fixed left-0 top-0 z-50 h-screen w-72 bg-gray-900 text-white flex flex-col shadow-2xl overflow-hidden"
            >
              {sidebarContent}
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
