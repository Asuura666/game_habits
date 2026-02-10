'use client';

import { Bell, Search, Settings, Moon, Sun, Menu, Flame } from 'lucide-react';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore } from '@/stores/authStore';
import Link from 'next/link';

interface HeaderProps {
  onMenuClick?: () => void;
}

export function Header({ onMenuClick }: HeaderProps) {
  const { user } = useAuthStore();
  const [isDark, setIsDark] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);

  const notifications = [
    { id: 1, title: 'Nouvelle récompense !', message: 'Tu as gagné 50 XP', time: 'Il y a 5 min' },
    { id: 2, title: 'Streak maintenu !', message: '7 jours consécutifs', time: 'Il y a 1h' },
    { id: 3, title: 'Nouveau niveau !', message: 'Tu es maintenant niveau 5', time: 'Il y a 2h' },
  ];

  return (
    <header className="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-4 lg:px-6">
      {/* Mobile Menu Button + Logo */}
      <div className="flex items-center gap-3 lg:hidden">
        <button
          onClick={onMenuClick}
          className="p-2 -ml-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          aria-label="Open menu"
        >
          <Menu className="w-6 h-6 text-gray-600 dark:text-gray-300" />
        </button>
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
            <Flame className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-gray-900 dark:text-white">HabitQuest</span>
        </Link>
      </div>

      {/* Search - Hidden on mobile, shown on larger screens */}
      <div className="hidden md:block flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Rechercher..."
            className="w-full pl-10 pr-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 border-none focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900 dark:text-white placeholder-gray-400"
          />
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 lg:gap-4">
        {/* Theme Toggle - Hidden on very small screens */}
        <button
          onClick={() => setIsDark(!isDark)}
          className="hidden sm:flex p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          {isDark ? (
            <Sun className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          ) : (
            <Moon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          )}
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors relative"
          >
            <Bell className="w-5 h-5 text-gray-600 dark:text-gray-300" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
          </button>

          <AnimatePresence>
            {showNotifications && (
              <>
                {/* Backdrop for mobile */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onClick={() => setShowNotifications(false)}
                  className="fixed inset-0 z-40 lg:hidden"
                />
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="absolute right-0 top-12 w-[calc(100vw-2rem)] sm:w-80 max-w-sm bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden z-50"
                >
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="font-semibold text-gray-900 dark:text-white">Notifications</h3>
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {notifications.map((notif) => (
                      <div
                        key={notif.id}
                        className="p-4 border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
                      >
                        <p className="font-medium text-gray-900 dark:text-white text-sm">{notif.title}</p>
                        <p className="text-gray-500 dark:text-gray-400 text-sm">{notif.message}</p>
                        <p className="text-gray-400 dark:text-gray-500 text-xs mt-1">{notif.time}</p>
                      </div>
                    ))}
                  </div>
                  <div className="p-3 text-center border-t border-gray-200 dark:border-gray-700">
                    <button className="text-primary-600 dark:text-primary-400 text-sm font-medium hover:underline">
                      Voir tout
                    </button>
                  </div>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>

        {/* Settings - Hidden on mobile */}
        <button className="hidden sm:flex p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
          <Settings className="w-5 h-5 text-gray-600 dark:text-gray-300" />
        </button>

        {/* User Avatar */}
        {user && (
          <div className="w-9 h-9 lg:w-10 lg:h-10 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center text-white font-bold cursor-pointer text-sm lg:text-base">
            {user.username.charAt(0).toUpperCase()}
          </div>
        )}
      </div>
    </header>
  );
}
