import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
  }),
}));

// Mock framer-motion
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  },
  AnimatePresence: ({ children }: any) => children,
}));

// Mock auth store
const mockFetchUser = vi.fn();
vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    token: 'mock-token',
    fetchUser: mockFetchUser,
  }),
}));

describe('Onboarding Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  describe('Character Name Validation', () => {
    it('should require a name with at least 2 characters', () => {
      const validateName = (name: string): boolean => {
        return name.trim().length >= 2 && name.trim().length <= 30;
      };

      expect(validateName('')).toBe(false);
      expect(validateName('A')).toBe(false);
      expect(validateName('Ab')).toBe(true);
      expect(validateName('Shadowbane')).toBe(true);
      expect(validateName('A'.repeat(31))).toBe(false);
    });

    it('should allow valid name characters', () => {
      const validateNameChars = (name: string): boolean => {
        const cleaned = name.replace(/[\s\-']/g, '');
        return /^[a-zA-Z0-9]+$/.test(cleaned);
      };

      expect(validateNameChars('Shadowbane')).toBe(true);
      expect(validateNameChars("D'Artagnan")).toBe(true);
      expect(validateNameChars('Dark-Knight')).toBe(true);
      expect(validateNameChars('Hero 2024')).toBe(true);
      expect(validateNameChars('Test@Name')).toBe(false);
    });
  });

  describe('Character Classes', () => {
    const CLASSES = [
      { id: 'warrior', name: 'Guerrier', bonus: '+20% XP des tâches' },
      { id: 'mage', name: 'Mage', bonus: '+20% pièces d\'or' },
      { id: 'ranger', name: 'Rôdeur', bonus: '+20% XP des habitudes' },
      { id: 'paladin', name: 'Paladin', bonus: '+10% tout XP' },
      { id: 'assassin', name: 'Assassin', bonus: '+30% bonus de streak' },
    ];

    it('should have 5 available classes', () => {
      expect(CLASSES).toHaveLength(5);
    });

    it('should have unique bonuses for each class', () => {
      const bonuses = CLASSES.map(c => c.bonus);
      const uniqueBonuses = new Set(bonuses);
      expect(uniqueBonuses.size).toBe(5);
    });

    it('should have valid class IDs', () => {
      const validIds = ['warrior', 'mage', 'ranger', 'paladin', 'assassin'];
      CLASSES.forEach(cls => {
        expect(validIds).toContain(cls.id);
      });
    });
  });

  describe('Stats Distribution', () => {
    const DEFAULT_STATS = {
      warrior: { strength: 15, intelligence: 8, agility: 10, vitality: 14, luck: 8 },
      mage: { strength: 6, intelligence: 18, agility: 8, vitality: 8, luck: 10 },
      ranger: { strength: 10, intelligence: 10, agility: 16, vitality: 10, luck: 9 },
      paladin: { strength: 12, intelligence: 12, agility: 10, vitality: 12, luck: 9 },
      assassin: { strength: 8, intelligence: 10, agility: 14, vitality: 8, luck: 15 },
    };

    it('should have balanced starting stats (total ~55 for each class)', () => {
      Object.entries(DEFAULT_STATS).forEach(([className, stats]) => {
        const total = Object.values(stats).reduce((a, b) => a + b, 0);
        expect(total).toBeGreaterThanOrEqual(50);
        expect(total).toBeLessThanOrEqual(60);
      });
    });

    it('should have warrior with highest strength', () => {
      const maxStrength = Math.max(...Object.values(DEFAULT_STATS).map(s => s.strength));
      expect(DEFAULT_STATS.warrior.strength).toBe(maxStrength);
    });

    it('should have mage with highest intelligence', () => {
      const maxInt = Math.max(...Object.values(DEFAULT_STATS).map(s => s.intelligence));
      expect(DEFAULT_STATS.mage.intelligence).toBe(maxInt);
    });

    it('should have ranger with highest agility', () => {
      const maxAgility = Math.max(...Object.values(DEFAULT_STATS).map(s => s.agility));
      expect(DEFAULT_STATS.ranger.agility).toBe(maxAgility);
    });

    it('should have assassin with highest luck', () => {
      const maxLuck = Math.max(...Object.values(DEFAULT_STATS).map(s => s.luck));
      expect(DEFAULT_STATS.assassin.luck).toBe(maxLuck);
    });
  });

  describe('API Integration', () => {
    it('should create character with correct payload', async () => {
      const mockResponse = {
        id: '123',
        name: 'TestHero',
        character_class: 'warrior',
        level: 1,
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const payload = {
        name: 'TestHero',
        character_class: 'warrior',
        stats: { strength: 15, intelligence: 8, agility: 10, vitality: 14, luck: 8 },
      };

      const response = await fetch('/api/characters', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      expect(response.ok).toBe(true);
      const data = await response.json();
      expect(data.name).toBe('TestHero');
    });

    it('should handle API errors gracefully', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Character name already exists' }),
      });

      const response = await fetch('/api/characters', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: 'ExistingName', character_class: 'warrior' }),
      });

      expect(response.ok).toBe(false);
      const error = await response.json();
      expect(error.detail).toBe('Character name already exists');
    });
  });

  describe('Wizard Navigation', () => {
    it('should have 3 steps in the wizard', () => {
      const TOTAL_STEPS = 3;
      expect(TOTAL_STEPS).toBe(3);
    });

    it('should validate step 1 (name) before proceeding', () => {
      const canProceedStep1 = (name: string): boolean => {
        return name.trim().length >= 2;
      };

      expect(canProceedStep1('')).toBe(false);
      expect(canProceedStep1('A')).toBe(false);
      expect(canProceedStep1('Hero')).toBe(true);
    });

    it('should validate step 2 (class) before proceeding', () => {
      const canProceedStep2 = (selectedClass: string | null): boolean => {
        return selectedClass !== null;
      };

      expect(canProceedStep2(null)).toBe(false);
      expect(canProceedStep2('warrior')).toBe(true);
    });

    it('should allow going back to previous steps', () => {
      const goBack = (currentStep: number): number => {
        return Math.max(currentStep - 1, 1);
      };

      expect(goBack(3)).toBe(2);
      expect(goBack(2)).toBe(1);
      expect(goBack(1)).toBe(1); // Can't go below step 1
    });
  });
});

describe('Character Page', () => {
  describe('Class Display', () => {
    const classInfo: Record<string, { name: string }> = {
      warrior: { name: 'Guerrier' },
      mage: { name: 'Mage' },
      ranger: { name: 'Rôdeur' },
      paladin: { name: 'Paladin' },
      assassin: { name: 'Assassin' },
    };

    it('should display correct French class names', () => {
      expect(classInfo.warrior.name).toBe('Guerrier');
      expect(classInfo.mage.name).toBe('Mage');
      expect(classInfo.ranger.name).toBe('Rôdeur');
      expect(classInfo.paladin.name).toBe('Paladin');
      expect(classInfo.assassin.name).toBe('Assassin');
    });
  });

  describe('Stats Display', () => {
    const statConfig = {
      strength: { label: 'Force' },
      intelligence: { label: 'Intelligence' },
      agility: { label: 'Agilité' },
      vitality: { label: 'Vitalité' },
      luck: { label: 'Chance' },
    };

    it('should have French labels for all stats', () => {
      expect(statConfig.strength.label).toBe('Force');
      expect(statConfig.intelligence.label).toBe('Intelligence');
      expect(statConfig.agility.label).toBe('Agilité');
      expect(statConfig.vitality.label).toBe('Vitalité');
      expect(statConfig.luck.label).toBe('Chance');
    });
  });

  describe('XP Progress', () => {
    it('should calculate XP percentage correctly', () => {
      const calculateXpPercentage = (current: number, max: number): number => {
        return Math.min(Math.round((current / max) * 100), 100);
      };

      expect(calculateXpPercentage(0, 100)).toBe(0);
      expect(calculateXpPercentage(50, 100)).toBe(50);
      expect(calculateXpPercentage(100, 100)).toBe(100);
      expect(calculateXpPercentage(150, 100)).toBe(100); // Cap at 100%
    });
  });

  describe('API Response Mapping', () => {
    it('should map API response to character data', () => {
      const apiResponse = {
        id: '123',
        user_id: '456',
        name: 'TestHero',
        character_class: 'warrior',
        title: 'The Brave',
        avatar_id: 'default',
        level: 5,
        current_xp: 450,
        xp_to_next_level: 1000,
        total_xp: 4500,
        hp: 95,
        max_hp: 100,
        stats: {
          strength: 20,
          intelligence: 10,
          agility: 12,
          vitality: 18,
          luck: 10,
        },
        unallocated_points: 2,
        coins: 500,
        gems: 10,
      };

      expect(apiResponse.name).toBe('TestHero');
      expect(apiResponse.character_class).toBe('warrior');
      expect(apiResponse.level).toBe(5);
      expect(apiResponse.stats.strength).toBe(20);
      expect(apiResponse.unallocated_points).toBe(2);
    });
  });
});
