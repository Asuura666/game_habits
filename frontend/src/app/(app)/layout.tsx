'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Sidebar } from '@/components/layout/Sidebar';
import { Header } from '@/components/layout/Header';
import { useAuthStore } from '@/stores/authStore';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, isLoading, setLoading, checkCharacter, hasCharacter } = useAuthStore();
  const [isCheckingCharacter, setIsCheckingCharacter] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    // Check if user data exists in localStorage
    const hasStoredData = localStorage.getItem('auth-storage');
    if (!hasStoredData) {
      setLoading(false);
    }
  }, [setLoading]);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  // Check for character after authentication
  useEffect(() => {
    const verifyCharacter = async () => {
      if (isAuthenticated && !isLoading) {
        setIsCheckingCharacter(true);
        const hasChar = await checkCharacter();
        setIsCheckingCharacter(false);
        
        if (!hasChar) {
          router.push('/onboarding');
        }
      }
    };

    verifyCharacter();
  }, [isAuthenticated, isLoading, checkCharacter, router]);

  // Close sidebar on route change (mobile)
  useEffect(() => {
    setIsSidebarOpen(false);
  }, []);

  if (isLoading || isCheckingCharacter) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Chargement...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !hasCharacter) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      <div className="lg:ml-64">
        <Header onMenuClick={() => setIsSidebarOpen(true)} />
        <main className="p-4 lg:p-6">{children}</main>
      </div>
    </div>
  );
}
