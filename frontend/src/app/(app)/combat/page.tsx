'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Swords, Shield, Zap, Heart, Sparkles, RotateCcw, Trophy } from 'lucide-react';
import { Card, Button, ProgressBar, Badge } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';
import type { Enemy } from '@/types';

const enemies: Enemy[] = [
  {
    id: '1',
    name: 'Slime Paresseux',
    level: 1,
    hp: 30,
    maxHp: 30,
    attack: 5,
    defense: 2,
    xpReward: 20,
    goldReward: 10,
  },
  {
    id: '2',
    name: 'Gobelin Procrastinateur',
    level: 3,
    hp: 60,
    maxHp: 60,
    attack: 10,
    defense: 5,
    xpReward: 50,
    goldReward: 25,
  },
  {
    id: '3',
    name: 'Dragon de la Mauvaise Habitude',
    level: 5,
    hp: 100,
    maxHp: 100,
    attack: 15,
    defense: 10,
    xpReward: 100,
    goldReward: 50,
  },
];

type BattleState = 'idle' | 'fighting' | 'victory' | 'defeat';

export default function CombatPage() {
  const { user, updateUser } = useAuthStore();
  const [selectedEnemy, setSelectedEnemy] = useState<Enemy | null>(null);
  const [battleState, setBattleState] = useState<BattleState>('idle');
  const [enemyHp, setEnemyHp] = useState(0);
  const [playerHp, setPlayerHp] = useState(user?.hp || 100);
  const [battleLog, setBattleLog] = useState<string[]>([]);
  const [isAttacking, setIsAttacking] = useState(false);

  useEffect(() => {
    setPlayerHp(user?.hp || 100);
  }, [user?.hp]);

  const startBattle = (enemy: Enemy) => {
    setSelectedEnemy(enemy);
    setEnemyHp(enemy.maxHp);
    setPlayerHp(user?.hp || 100);
    setBattleState('fighting');
    setBattleLog([`⚔️ Combat contre ${enemy.name} !`]);
  };

  const attack = async () => {
    if (!selectedEnemy || isAttacking) return;
    
    setIsAttacking(true);
    
    // Player attacks
    const playerDamage = Math.max(10 + (user?.level || 1) * 2 - selectedEnemy.defense, 1);
    const newEnemyHp = Math.max(enemyHp - playerDamage, 0);
    setEnemyHp(newEnemyHp);
    setBattleLog((prev) => [...prev, `🗡️ Tu infliges ${playerDamage} dégâts !`]);

    await new Promise((r) => setTimeout(r, 500));

    if (newEnemyHp <= 0) {
      // Victory
      setBattleState('victory');
      setBattleLog((prev) => [
        ...prev,
        `🎉 Victoire ! +${selectedEnemy.xpReward} XP, +${selectedEnemy.goldReward} Or`,
      ]);
      if (user) {
        updateUser({
          xp: user.xp + selectedEnemy.xpReward,
          gold: user.gold + selectedEnemy.goldReward,
        });
      }
    } else {
      // Enemy attacks back
      await new Promise((r) => setTimeout(r, 500));
      const enemyDamage = Math.max(selectedEnemy.attack - 5, 1);
      const newPlayerHp = Math.max(playerHp - enemyDamage, 0);
      setPlayerHp(newPlayerHp);
      setBattleLog((prev) => [...prev, `👹 ${selectedEnemy.name} inflige ${enemyDamage} dégâts !`]);

      if (newPlayerHp <= 0) {
        setBattleState('defeat');
        setBattleLog((prev) => [...prev, `💀 Défaite... Tu perds 10 PV max.`]);
      }
    }

    setIsAttacking(false);
  };

  const useSkill = async () => {
    if (!selectedEnemy || isAttacking || (user?.mana || 0) < 20) return;
    
    setIsAttacking(true);
    updateUser({ mana: (user?.mana || 0) - 20 });
    
    const skillDamage = 30 + (user?.level || 1) * 5;
    const newEnemyHp = Math.max(enemyHp - skillDamage, 0);
    setEnemyHp(newEnemyHp);
    setBattleLog((prev) => [...prev, `✨ Attaque spéciale ! ${skillDamage} dégâts !`]);

    await new Promise((r) => setTimeout(r, 500));

    if (newEnemyHp <= 0) {
      setBattleState('victory');
      setBattleLog((prev) => [
        ...prev,
        `🎉 Victoire ! +${selectedEnemy.xpReward} XP, +${selectedEnemy.goldReward} Or`,
      ]);
      if (user) {
        updateUser({
          xp: user.xp + selectedEnemy.xpReward,
          gold: user.gold + selectedEnemy.goldReward,
        });
      }
    }

    setIsAttacking(false);
  };

  const resetBattle = () => {
    setSelectedEnemy(null);
    setBattleState('idle');
    setBattleLog([]);
    setPlayerHp(user?.hp || 100);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
          <Swords className="w-8 h-8 text-red-500" />
          Arène de Combat
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mt-1">
          Combattez des monstres pour gagner XP et Or
        </p>
      </div>

      <AnimatePresence mode="wait">
        {battleState === 'idle' ? (
          /* Enemy Selection */
          <motion.div
            key="selection"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-4"
          >
            {enemies.map((enemy) => (
              <Card
                key={enemy.id}
                variant="bordered"
                hover
                onClick={() => startBattle(enemy)}
                className="cursor-pointer"
              >
                <div className="text-center">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center mx-auto mb-4 text-4xl">
                    {enemy.name.includes('Slime') ? '🟢' : enemy.name.includes('Gobelin') ? '👺' : '🐉'}
                  </div>
                  <h3 className="font-bold text-gray-900 dark:text-white">{enemy.name}</h3>
                  <Badge className="mt-2">Niveau {enemy.level}</Badge>
                  
                  <div className="mt-4 space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">PV</span>
                      <span className="text-game-hp">{enemy.maxHp}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Récompense</span>
                      <span className="text-game-xp">+{enemy.xpReward} XP</span>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </motion.div>
        ) : (
          /* Battle Arena */
          <motion.div
            key="battle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-6"
          >
            {/* Battle Field */}
            <Card variant="bordered" padding="lg">
              <div className="grid grid-cols-3 gap-8 items-center">
                {/* Player */}
                <div className="text-center">
                  <motion.div
                    animate={isAttacking ? { x: [0, 50, 0] } : {}}
                    className="w-24 h-24 rounded-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center mx-auto mb-4 text-4xl"
                  >
                    {user?.username.charAt(0).toUpperCase()}
                  </motion.div>
                  <h3 className="font-bold text-gray-900 dark:text-white">{user?.username}</h3>
                  <Badge className="mt-1">Niveau {user?.level}</Badge>
                  
                  <div className="mt-4 space-y-2">
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-game-hp">PV</span>
                        <span>{playerHp}/{user?.maxHp}</span>
                      </div>
                      <ProgressBar value={playerHp} max={user?.maxHp || 100} variant="hp" size="sm" />
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-game-mana">Mana</span>
                        <span>{user?.mana}/{user?.maxMana}</span>
                      </div>
                      <ProgressBar value={user?.mana || 0} max={user?.maxMana || 50} variant="mana" size="sm" />
                    </div>
                  </div>
                </div>

                {/* VS */}
                <div className="text-center">
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                    className="text-4xl font-bold text-red-500"
                  >
                    VS
                  </motion.div>
                </div>

                {/* Enemy */}
                <div className="text-center">
                  <motion.div
                    animate={battleState === 'fighting' && !isAttacking ? { x: [0, -10, 0] } : {}}
                    transition={{ repeat: Infinity, duration: 0.5 }}
                    className={cn(
                      'w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-4 text-4xl',
                      battleState === 'victory' ? 'bg-gray-500 opacity-50' : 'bg-gradient-to-br from-red-500 to-orange-500'
                    )}
                  >
                    {selectedEnemy?.name.includes('Slime') ? '🟢' : selectedEnemy?.name.includes('Gobelin') ? '👺' : '🐉'}
                  </motion.div>
                  <h3 className="font-bold text-gray-900 dark:text-white">{selectedEnemy?.name}</h3>
                  <Badge variant="danger" className="mt-1">Niveau {selectedEnemy?.level}</Badge>
                  
                  <div className="mt-4">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-game-hp">PV</span>
                      <span>{enemyHp}/{selectedEnemy?.maxHp}</span>
                    </div>
                    <ProgressBar value={enemyHp} max={selectedEnemy?.maxHp || 100} variant="hp" size="sm" />
                  </div>
                </div>
              </div>
            </Card>

            {/* Battle Controls */}
            {battleState === 'fighting' && (
              <div className="flex justify-center gap-4">
                <Button onClick={attack} disabled={isAttacking} className="gap-2">
                  <Swords className="w-5 h-5" />
                  Attaquer
                </Button>
                <Button
                  onClick={useSkill}
                  disabled={isAttacking || (user?.mana || 0) < 20}
                  variant="secondary"
                  className="gap-2"
                >
                  <Zap className="w-5 h-5" />
                  Compétence (20 Mana)
                </Button>
                <Button onClick={resetBattle} variant="ghost" className="gap-2">
                  <RotateCcw className="w-5 h-5" />
                  Fuir
                </Button>
              </div>
            )}

            {/* Victory/Defeat */}
            {(battleState === 'victory' || battleState === 'defeat') && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="text-center"
              >
                {battleState === 'victory' ? (
                  <div className="inline-flex items-center gap-3 px-6 py-3 rounded-xl bg-green-500/20 text-green-500">
                    <Trophy className="w-8 h-8" />
                    <span className="text-2xl font-bold">Victoire !</span>
                  </div>
                ) : (
                  <div className="inline-flex items-center gap-3 px-6 py-3 rounded-xl bg-red-500/20 text-red-500">
                    <Heart className="w-8 h-8" />
                    <span className="text-2xl font-bold">Défaite...</span>
                  </div>
                )}
                <div className="mt-4">
                  <Button onClick={resetBattle}>Retour à l'arène</Button>
                </div>
              </motion.div>
            )}

            {/* Battle Log */}
            <Card variant="bordered" padding="md">
              <h4 className="font-semibold text-gray-900 dark:text-white mb-3">Journal de combat</h4>
              <div className="h-32 overflow-y-auto space-y-1 text-sm">
                {battleLog.map((log, i) => (
                  <motion.p
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="text-gray-600 dark:text-gray-400"
                  >
                    {log}
                  </motion.p>
                ))}
              </div>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
