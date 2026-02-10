'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Mail, Lock, Flame, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { Button, Input, Card } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import type { User } from '@/types';

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [debugInfo, setDebugInfo] = useState('');

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Clear previous errors
    setError('');
    setDebugInfo('');
    
    // Basic validation
    if (!email || !email.includes('@')) {
      setError('Veuillez entrer une adresse email valide');
      return;
    }
    
    if (!password || password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    setIsLoading(true);
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
    console.log('[Login] API URL:', apiUrl);
    console.log('[Login] Attempting login for:', email);

    try {
      // Login API call
      const loginUrl = `${apiUrl}/auth/login`;
      console.log('[Login] Fetching:', loginUrl);
      
      const response = await fetch(loginUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password: password,
        }),
      });

      console.log('[Login] Response status:', response.status);
      
      let data;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
        console.log('[Login] Response data:', JSON.stringify(data).substring(0, 200));
      } else {
        const text = await response.text();
        console.log('[Login] Non-JSON response:', text.substring(0, 200));
        throw new Error('Réponse invalide du serveur');
      }

      if (!response.ok) {
        const errorMsg = data?.detail || data?.message || `Erreur ${response.status}`;
        console.log('[Login] Error from API:', errorMsg);
        throw new Error(errorMsg);
      }

      if (!data.access_token || !data.user) {
        console.log('[Login] Invalid response structure:', data);
        throw new Error('Réponse invalide: token ou utilisateur manquant');
      }

      // Map API response to User type
      const user: User = {
        id: data.user.id,
        email: data.user.email,
        username: data.user.username,
        level: data.user.level || 1,
        xp: data.user.total_xp || 0,
        xpToNextLevel: 100,
        gold: data.user.coins || 0,
        hp: 100,
        maxHp: 100,
        mana: 50,
        maxMana: 50,
        streak: 0,
        avatarUrl: data.user.avatar_url,
        createdAt: data.user.created_at,
      };

      console.log('[Login] User mapped:', user.username);
      login(user, data.access_token, data.access_token);
      
      // Check if user has a character
      console.log('[Login] Checking character...');
      const characterResponse = await fetch(`${apiUrl}/characters/me`, {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      });

      console.log('[Login] Character check status:', characterResponse.status);

      if (characterResponse.ok) {
        console.log('[Login] Has character, redirecting to dashboard');
        router.push('/dashboard');
      } else {
        console.log('[Login] No character, redirecting to onboarding');
        router.push('/onboarding');
      }
    } catch (err) {
      console.error('[Login] Error:', err);
      
      let errorMessage = 'Une erreur est survenue';
      
      if (err instanceof TypeError && err.message.includes('fetch')) {
        errorMessage = 'Impossible de contacter le serveur. Vérifiez votre connexion.';
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      setDebugInfo(`API: ${apiUrl || 'non défini'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
      {/* Background effects */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(14,165,233,0.1),transparent_50%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(217,70,239,0.1),transparent_50%)]" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative w-full max-w-md"
      >
        <Card variant="bordered" padding="lg" className="bg-gray-800/80 backdrop-blur-sm border-gray-700">
          {/* Logo */}
          <div className="text-center mb-8">
            <Link href="/" className="inline-flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                <Flame className="w-7 h-7 text-white" />
              </div>
              <span className="text-2xl font-bold text-white">HabitQuest</span>
            </Link>
            <h1 className="text-2xl font-bold text-white mb-2">Bon retour !</h1>
            <p className="text-gray-400">Connectez-vous pour continuer votre quête</p>
          </div>

          {/* Form - noValidate to disable browser validation */}
          <form onSubmit={handleSubmit} className="space-y-5" noValidate autoComplete="off">
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-start gap-2"
              >
                <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                <div>
                  <p>{error}</p>
                  {debugInfo && (
                    <p className="text-xs text-red-400/60 mt-1">{debugInfo}</p>
                  )}
                </div>
              </motion.div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <Mail className="w-5 h-5" />
                </div>
                <input
                  type="text"
                  inputMode="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setError(''); }}
                  placeholder="votre@email.com"
                  className="w-full pl-10 pr-4 py-2.5 rounded-lg border bg-gray-800 text-white placeholder-gray-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent border-gray-600"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1.5">
                Mot de passe
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                  <Lock className="w-5 h-5" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setError(''); }}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-12 py-2.5 rounded-lg border bg-gray-800 text-white placeholder-gray-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent border-gray-600"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-300"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 text-gray-400">
                <input type="checkbox" className="rounded border-gray-600 bg-gray-700 text-primary-500 focus:ring-primary-500" />
                Se souvenir de moi
              </label>
              <Link href="/forgot-password" className="text-primary-400 hover:text-primary-300">
                Mot de passe oublié ?
              </Link>
            </div>

            <Button type="submit" className="w-full" size="lg" isLoading={isLoading}>
              Se connecter
            </Button>
          </form>

          {/* Divider */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-700" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-gray-800 text-gray-500">ou</span>
            </div>
          </div>

          {/* Social Login */}
          <div className="space-y-3">
            <Button variant="secondary" className="w-full" type="button">
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
              </svg>
              Continuer avec Google
            </Button>
          </div>

          {/* Register Link */}
          <p className="text-center text-gray-400 mt-8">
            Pas encore de compte ?{' '}
            <Link href="/register" className="text-primary-400 hover:text-primary-300 font-medium">
              Créer un compte
            </Link>
          </p>
        </Card>
      </motion.div>
    </div>
  );
}
