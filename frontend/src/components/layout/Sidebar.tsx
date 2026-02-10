'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
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
} from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { ProgressBar } from '@/components/ui';

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/habits', icon: Target, label: 'Habitudes' },
  { href: '/tasks', icon: CheckSquare, label: 'Tâches' },
  { href: '/character', icon: User, label: 'Personnage' },
  { href: '/shop', icon: ShoppingBag, label: 'Boutique' },
  { href: '/inventory', icon: Package, label: 'Inventaire' },
  { href: '/combat', icon: Swords, label: 'Combat' },
  { href: '/friends', icon: Users, label: 'Amis' },
  { href: '/leaderboard', icon: Trophy, label: 'Classement' },
  { href: '/badges', icon: Award, label: 'Badges' },
  { href: '/stats', icon: BarChart3, label: 'Statistiques' },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, character, logout } = useAuthStore();

  // Use character coins if available, fallback to user gold
  const coins = character?.coins ?? user?.gold ?? 0;

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 bg-gray-900 text-white flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <Link href="/dashboard" className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
            <Flame className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-bold">HabitQuest</span>
        </Link>
      </div>

      {/* User Stats */}
      {user && (
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-lg font-bold">
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
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200',
                    isActive
                      ? 'bg-primary-600 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-gray-800'
                  )}
                >
                  <Icon className="w-5 h-5" />
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

      {/* Logout */}
      <div className="p-4 border-t border-gray-800">
        <button
          onClick={() => logout()}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-all duration-200"
        >
          <LogOut className="w-5 h-5" />
          <span>Déconnexion</span>
        </button>
      </div>
    </aside>
  );
}
