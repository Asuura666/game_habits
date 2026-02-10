'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Flame, Target, Trophy, Sword, ArrowRight, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import Link from 'next/link';

const features = [
  {
    icon: Target,
    title: 'Suivez vos habitudes',
    description: 'Créez et suivez vos habitudes quotidiennes avec un système de récompenses motivant.',
  },
  {
    icon: Trophy,
    title: 'Montez de niveau',
    description: 'Gagnez de l\'XP en complétant vos habitudes et débloquez de nouveaux contenus.',
  },
  {
    icon: Sword,
    title: 'Combattez des monstres',
    description: 'Utilisez votre productivité pour vaincre des ennemis et gagner des récompenses.',
  },
];

export default function LandingPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Background effects */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(14,165,233,0.15),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(217,70,239,0.15),transparent_50%)]" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 sm:pt-12 lg:pt-20 pb-16 lg:pb-24">
          {/* Nav */}
          <nav className="flex items-center justify-between mb-10 lg:mb-16">
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                <Flame className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
              <span className="text-xl sm:text-2xl font-bold text-white">HabitQuest</span>
            </div>
            
            {/* Desktop Nav */}
            <div className="hidden sm:flex items-center gap-4">
              <Link href="/login">
                <Button variant="ghost" className="text-white">Connexion</Button>
              </Link>
              <Link href="/register">
                <Button>Commencer</Button>
              </Link>
            </div>
            
            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="sm:hidden p-2 rounded-lg text-white hover:bg-white/10 transition-colors"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </nav>

          {/* Mobile Menu */}
          <AnimatePresence>
            {isMobileMenuOpen && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="sm:hidden overflow-hidden mb-8"
              >
                <div className="flex flex-col gap-3 py-4 border-t border-white/10">
                  <Link href="/login" className="w-full">
                    <Button variant="ghost" className="w-full text-white justify-center">
                      Connexion
                    </Button>
                  </Link>
                  <Link href="/register" className="w-full">
                    <Button className="w-full justify-center">Commencer</Button>
                  </Link>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Hero Content */}
          <div className="text-center max-w-4xl mx-auto">
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              className="text-3xl sm:text-5xl lg:text-7xl font-bold mb-4 sm:mb-6"
            >
              <span className="text-white">Transformez vos habitudes en </span>
              <span className="gradient-text">quêtes épiques</span>
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-base sm:text-lg lg:text-xl text-gray-400 mb-8 sm:mb-10 max-w-2xl mx-auto px-4"
            >
              Gagnez de l'XP, montez de niveau, combattez des monstres et devenez la meilleure version de vous-même grâce à la gamification.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 px-4"
            >
              <Link href="/register" className="w-full sm:w-auto">
                <Button size="lg" className="gap-2 w-full sm:w-auto justify-center">
                  Commencer gratuitement
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </Link>
              <Button size="lg" variant="secondary" className="w-full sm:w-auto justify-center">
                Voir la démo
              </Button>
            </motion.div>
          </div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="grid grid-cols-3 gap-4 sm:gap-8 max-w-3xl mx-auto mt-12 sm:mt-20"
          >
            {[
              { value: '10K+', label: 'Utilisateurs' },
              { value: '1M+', label: 'Habitudes' },
              { value: '99%', label: 'Satisfaction' },
            ].map((stat, index) => (
              <div key={index} className="text-center">
                <p className="text-2xl sm:text-4xl font-bold text-white mb-1 sm:mb-2">{stat.value}</p>
                <p className="text-xs sm:text-base text-gray-500">{stat.label}</p>
              </div>
            ))}
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 lg:py-24 bg-gray-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-10 lg:mb-16">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-3 sm:mb-4">
              Pourquoi HabitQuest ?
            </h2>
            <p className="text-sm sm:text-base text-gray-400 max-w-2xl mx-auto">
              Découvrez comment la gamification peut transformer votre quotidien
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  className="bg-gray-800 rounded-2xl p-6 lg:p-8 border border-gray-700 hover:border-primary-500/50 transition-colors"
                >
                  <div className="w-12 h-12 lg:w-14 lg:h-14 rounded-xl bg-gradient-to-br from-primary-500/20 to-accent-500/20 flex items-center justify-center mb-4 lg:mb-6">
                    <Icon className="w-6 h-6 lg:w-7 lg:h-7 text-primary-400" />
                  </div>
                  <h3 className="text-lg lg:text-xl font-semibold text-white mb-2 lg:mb-3">{feature.title}</h3>
                  <p className="text-sm lg:text-base text-gray-400">{feature.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-16 lg:py-24">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-4 lg:mb-6">
            Prêt à commencer votre quête ?
          </h2>
          <p className="text-sm sm:text-base text-gray-400 mb-8 lg:mb-10">
            Rejoignez des milliers d'aventuriers qui transforment leur vie, une habitude à la fois.
          </p>
          <Link href="/register">
            <Button size="lg" className="gap-2">
              Créer mon compte
              <ArrowRight className="w-5 h-5" />
            </Button>
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-6 lg:py-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-xs sm:text-sm">
          <p>© 2026 HabitQuest. Tous droits réservés.</p>
        </div>
      </footer>
    </div>
  );
}
