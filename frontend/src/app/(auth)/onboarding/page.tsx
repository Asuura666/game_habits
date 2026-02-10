'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sword, 
  Wand2, 
  Target, 
  Shield, 
  Zap,
  ArrowRight,
  ArrowLeft,
  Sparkles,
  Check,
  User
} from 'lucide-react';
import { Button, Card, Input } from '@/components/ui';
import { LPCCharacter } from '@/components/character';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';

const CLASSES = [
  {
    id: 'warrior',
    name: 'Guerrier',
    icon: Sword,
    color: 'from-red-500 to-orange-500',
    borderColor: 'border-red-500',
    bonus: '+20% XP des tâches',
    description: 'Force brute et détermination. Idéal pour ceux qui aiment les gros défis.',
    stats: { strength: 15, intelligence: 8, agility: 10, vitality: 14, luck: 8 },
    defaultGender: 'male' as const,
  },
  {
    id: 'mage',
    name: 'Mage',
    icon: Wand2,
    color: 'from-blue-500 to-purple-500',
    borderColor: 'border-blue-500',
    bonus: '+20% pièces d\'or',
    description: 'Sagesse et connaissance. Parfait pour les penseurs stratégiques.',
    stats: { strength: 6, intelligence: 18, agility: 8, vitality: 8, luck: 10 },
    defaultGender: 'female' as const,
  },
  {
    id: 'ranger',
    name: 'Rôdeur',
    icon: Target,
    color: 'from-green-500 to-emerald-500',
    borderColor: 'border-green-500',
    bonus: '+20% XP des habitudes',
    description: 'Agilité et constance. Pour ceux qui construisent des routines solides.',
    stats: { strength: 10, intelligence: 10, agility: 16, vitality: 10, luck: 9 },
    defaultGender: 'male' as const,
  },
  {
    id: 'paladin',
    name: 'Paladin',
    icon: Shield,
    color: 'from-yellow-500 to-amber-500',
    borderColor: 'border-yellow-500',
    bonus: '+10% tout XP',
    description: 'Équilibre et polyvalence. Le choix des joueurs expérimentés.',
    stats: { strength: 12, intelligence: 12, agility: 10, vitality: 12, luck: 9 },
    defaultGender: 'male' as const,
  },
  {
    id: 'assassin',
    name: 'Assassin',
    icon: Zap,
    color: 'from-purple-500 to-pink-500',
    borderColor: 'border-purple-500',
    bonus: '+30% bonus de streak',
    description: 'Vitesse et précision. Récompense la régularité quotidienne.',
    stats: { strength: 8, intelligence: 10, agility: 14, vitality: 8, luck: 15 },
    defaultGender: 'female' as const,
  }
] as const;

type CharacterClass = typeof CLASSES[number]['id'];
type Gender = 'male' | 'female';

export default function OnboardingPage() {
  const router = useRouter();
  const { accessToken, fetchUser } = useAuthStore();
  const [step, setStep] = useState(1);
  const [characterName, setCharacterName] = useState('');
  const [selectedClass, setSelectedClass] = useState<CharacterClass | null>(null);
  const [selectedGender, setSelectedGender] = useState<Gender>('male');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const totalSteps = 4;

  const handleNext = () => {
    if (step === 1 && !characterName.trim()) {
      setError('Entre un nom pour ton personnage');
      return;
    }
    if (step === 2 && !selectedClass) {
      setError('Choisis une classe');
      return;
    }
    setError('');
    setStep(prev => Math.min(prev + 1, totalSteps));
  };

  const handleBack = () => {
    setError('');
    setStep(prev => Math.max(prev - 1, 1));
  };

  const handleClassSelect = (classId: CharacterClass) => {
    setSelectedClass(classId);
    // Set default gender for this class
    const classData = CLASSES.find(c => c.id === classId);
    if (classData) {
      setSelectedGender(classData.defaultGender);
    }
  };

  const handleSubmit = async () => {
    if (!selectedClass || !characterName.trim()) return;

    setIsLoading(true);
    setError('');

    try {
      const selectedClassData = CLASSES.find(c => c.id === selectedClass);
      
      // Create avatar_id based on class and gender
      const avatarId = `${selectedClass}_${selectedGender === 'female' ? 'f' : 'm'}1`;
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/characters/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          name: characterName.trim(),
          character_class: selectedClass,
          stats: selectedClassData?.stats || {},
          avatar_id: avatarId
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Erreur lors de la création du personnage');
      }

      // Refresh user data
      await fetchUser();
      
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Une erreur est survenue');
    } finally {
      setIsLoading(false);
    }
  };

  const selectedClassData = CLASSES.find(c => c.id === selectedClass);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex justify-between mb-2">
            {[1, 2, 3, 4].map(s => (
              <div
                key={s}
                className={cn(
                  'flex items-center justify-center w-10 h-10 rounded-full font-bold transition-all',
                  s < step ? 'bg-primary-500 text-white' :
                  s === step ? 'bg-primary-500 text-white ring-4 ring-primary-500/30' :
                  'bg-gray-700 text-gray-400'
                )}
              >
                {s < step ? <Check className="w-5 h-5" /> : s}
              </div>
            ))}
          </div>
          <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-primary-500 to-accent-500"
              initial={{ width: 0 }}
              animate={{ width: `${((step - 1) / (totalSteps - 1)) * 100}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        </div>

        <AnimatePresence mode="wait">
          {/* Step 1: Name */}
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <Card variant="elevated" padding="xl" className="bg-gray-800/80 backdrop-blur border-gray-700">
                <div className="text-center mb-8">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.2, type: 'spring' }}
                    className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center"
                  >
                    <Sparkles className="w-10 h-10 text-white" />
                  </motion.div>
                  <h1 className="text-3xl font-bold text-white mb-2">
                    Crée ton personnage
                  </h1>
                  <p className="text-gray-400">
                    Commence par lui donner un nom légendaire
                  </p>
                </div>

                <div className="space-y-4">
                  <Input
                    label="Nom du personnage"
                    placeholder="Ex: Shadowbane, Luna, Valor..."
                    value={characterName}
                    onChange={(e) => setCharacterName(e.target.value)}
                    maxLength={30}
                    autoFocus
                  />
                  <p className="text-sm text-gray-500">
                    2-30 caractères. Lettres, chiffres, espaces et tirets autorisés.
                  </p>
                </div>

                {error && (
                  <p className="mt-4 text-red-400 text-sm text-center">{error}</p>
                )}

                <div className="mt-8 flex justify-end">
                  <Button onClick={handleNext} className="gap-2">
                    Continuer
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            </motion.div>
          )}

          {/* Step 2: Class */}
          {step === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <Card variant="elevated" padding="xl" className="bg-gray-800/80 backdrop-blur border-gray-700">
                <div className="text-center mb-8">
                  <h1 className="text-3xl font-bold text-white mb-2">
                    Choisis ta classe
                  </h1>
                  <p className="text-gray-400">
                    Chaque classe offre des bonus uniques
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {CLASSES.map(cls => {
                    const Icon = cls.icon;
                    const isSelected = selectedClass === cls.id;
                    
                    return (
                      <motion.button
                        key={cls.id}
                        onClick={() => handleClassSelect(cls.id)}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className={cn(
                          'relative p-4 rounded-xl border-2 text-left transition-all',
                          isSelected
                            ? `${cls.borderColor} bg-gray-700/50`
                            : 'border-gray-700 hover:border-gray-600 bg-gray-800/50'
                        )}
                      >
                        {isSelected && (
                          <div className="absolute top-2 right-2">
                            <Check className="w-5 h-5 text-primary-400" />
                          </div>
                        )}
                        
                        <div className={cn(
                          'w-12 h-12 rounded-lg bg-gradient-to-br flex items-center justify-center mb-3',
                          cls.color
                        )}>
                          <Icon className="w-6 h-6 text-white" />
                        </div>
                        
                        <h3 className="font-bold text-white mb-1">{cls.name}</h3>
                        <p className="text-sm text-primary-400 mb-2">{cls.bonus}</p>
                        <p className="text-xs text-gray-500">{cls.description}</p>
                      </motion.button>
                    );
                  })}
                </div>

                {error && (
                  <p className="mt-4 text-red-400 text-sm text-center">{error}</p>
                )}

                <div className="mt-8 flex justify-between">
                  <Button variant="ghost" onClick={handleBack} className="gap-2">
                    <ArrowLeft className="w-4 h-4" />
                    Retour
                  </Button>
                  <Button onClick={handleNext} className="gap-2">
                    Continuer
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            </motion.div>
          )}

          {/* Step 3: Appearance (Gender Selection) */}
          {step === 3 && selectedClass && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <Card variant="elevated" padding="xl" className="bg-gray-800/80 backdrop-blur border-gray-700">
                <div className="text-center mb-8">
                  <h1 className="text-3xl font-bold text-white mb-2">
                    Choisis ton apparence
                  </h1>
                  <p className="text-gray-400">
                    Personnalise ton {selectedClassData?.name}
                  </p>
                </div>

                {/* Gender Selection */}
                <div className="flex justify-center gap-8 mb-8">
                  {(['male', 'female'] as const).map((gender) => (
                    <motion.button
                      key={gender}
                      onClick={() => setSelectedGender(gender)}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className={cn(
                        'p-4 rounded-2xl transition-all flex flex-col items-center gap-4',
                        selectedGender === gender
                          ? 'ring-4 ring-primary-500 bg-gray-700/50'
                          : 'bg-gray-800/30 hover:bg-gray-700/30'
                      )}
                    >
                      <LPCCharacter
                        characterClass={selectedClass}
                        gender={gender}
                        level={10}
                        size="xl"
                        animated={false}
                      />
                      <span className={cn(
                        'font-medium',
                        selectedGender === gender ? 'text-primary-400' : 'text-gray-400'
                      )}>
                        {gender === 'male' ? 'Masculin' : 'Féminin'}
                      </span>
                      {selectedGender === gender && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="absolute -top-2 -right-2 w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center"
                        >
                          <Check className="w-4 h-4 text-white" />
                        </motion.div>
                      )}
                    </motion.button>
                  ))}
                </div>

                {/* Preview at different levels */}
                <div className="text-center p-6 bg-gray-900/50 rounded-xl mb-6">
                  <p className="text-sm text-gray-400 mb-4">Évolution de ton personnage selon le niveau :</p>
                  <div className="flex justify-center gap-6 items-end">
                    {[1, 5, 10, 15, 20].map((level) => (
                      <div key={level} className="flex flex-col items-center">
                        <LPCCharacter
                          characterClass={selectedClass}
                          gender={selectedGender}
                          level={level}
                          size={level === 10 ? 'lg' : 'md'}
                          animated={false}
                        />
                        <span className="text-xs text-gray-500 mt-2">Niv. {level}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {error && (
                  <p className="mt-4 text-red-400 text-sm text-center">{error}</p>
                )}

                <div className="mt-8 flex justify-between">
                  <Button variant="ghost" onClick={handleBack} className="gap-2">
                    <ArrowLeft className="w-4 h-4" />
                    Retour
                  </Button>
                  <Button onClick={handleNext} className="gap-2">
                    Continuer
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            </motion.div>
          )}

          {/* Step 4: Confirmation */}
          {step === 4 && selectedClassData && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <Card variant="elevated" padding="xl" className="bg-gray-800/80 backdrop-blur border-gray-700">
                <div className="text-center mb-8">
                  <h1 className="text-3xl font-bold text-white mb-2">
                    Prêt à commencer ?
                  </h1>
                  <p className="text-gray-400">
                    Vérifie ton personnage avant de te lancer
                  </p>
                </div>

                <div className="bg-gray-900/50 rounded-2xl p-6 mb-6">
                  <div className="flex items-center gap-6">
                    <LPCCharacter
                      characterClass={selectedClass!}
                      gender={selectedGender}
                      level={1}
                      size="2xl"
                      showLevel={true}
                      animated={true}
                    />
                    
                    <div>
                      <h2 className="text-2xl font-bold text-white">{characterName}</h2>
                      <p className="text-lg text-gray-400">{selectedClassData.name}</p>
                      <p className="text-primary-400 mt-1">{selectedClassData.bonus}</p>
                      <p className="text-sm text-gray-500 mt-1">
                        {selectedGender === 'male' ? '♂ Masculin' : '♀ Féminin'}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-5 gap-2 mt-6">
                    {Object.entries(selectedClassData.stats).map(([stat, value]) => (
                      <div key={stat} className="text-center p-2 bg-gray-800 rounded-lg">
                        <p className="text-lg font-bold text-white">{value}</p>
                        <p className="text-xs text-gray-500 capitalize">{
                          stat === 'strength' ? 'FOR' :
                          stat === 'intelligence' ? 'INT' :
                          stat === 'agility' ? 'AGI' :
                          stat === 'vitality' ? 'VIT' : 'CHA'
                        }</p>
                      </div>
                    ))}
                  </div>
                </div>

                {error && (
                  <p className="mb-4 text-red-400 text-sm text-center">{error}</p>
                )}

                <div className="flex justify-between">
                  <Button variant="ghost" onClick={handleBack} className="gap-2" disabled={isLoading}>
                    <ArrowLeft className="w-4 h-4" />
                    Retour
                  </Button>
                  <Button 
                    onClick={handleSubmit} 
                    className="gap-2"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Création...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4" />
                        Commencer l'aventure !
                      </>
                    )}
                  </Button>
                </div>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
