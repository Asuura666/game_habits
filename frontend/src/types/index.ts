// User types
export interface User {
  id: string;
  email: string;
  username: string;
  level: number;
  xp: number;
  xpToNextLevel: number;
  gold: number;
  hp: number;
  maxHp: number;
  mana: number;
  maxMana: number;
  streak: number;
  avatarUrl?: string;
  createdAt: string;
}

// Habit types
export type HabitDifficulty = 'trivial' | 'easy' | 'medium' | 'hard';
export type HabitFrequency = 'daily' | 'weekly' | 'monthly';

export interface Habit {
  id: string;
  userId: string;
  title: string;
  description?: string;
  difficulty: HabitDifficulty;
  frequency: HabitFrequency;
  positive: boolean;
  negative: boolean;
  streak: number;
  completedToday: boolean;
  xpReward: number;
  goldReward: number;
  createdAt: string;
  updatedAt: string;
}

// Task types
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Task {
  id: string;
  userId: string;
  title: string;
  description?: string;
  priority: TaskPriority;
  dueDate?: string;
  completed: boolean;
  xpReward: number;
  goldReward: number;
  createdAt: string;
  updatedAt: string;
}

// Character types
export type CharacterClass = 'warrior' | 'mage' | 'ranger' | 'paladin' | 'assassin' | 'rogue' | 'healer';

export interface StatsDistribution {
  strength: number;
  intelligence: number;
  agility: number;
  vitality: number;
  luck: number;
}

export interface Character {
  id: string;
  user_id: string;
  name: string;
  character_class: CharacterClass;
  title?: string;
  avatar_id: string;
  level: number;
  current_xp: number;
  xp_to_next_level: number;
  total_xp: number;
  hp: number;
  max_hp: number;
  stats: StatsDistribution;
  unallocated_points: number;
  coins: number;
  gems: number;
  streak?: number;
  xp?: number; // Alias for current_xp
  created_at: string;
  updated_at: string;
}

export interface Equipment {
  id: string;
  name: string;
  type: 'weapon' | 'armor' | 'accessory';
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
  stats: Record<string, number>;
  iconUrl?: string;
}

// Shop types
export interface ShopItem {
  id: string;
  name: string;
  description: string;
  price: number;
  type: 'equipment' | 'consumable' | 'cosmetic';
  iconUrl?: string;
}

// Combat types
export interface Enemy {
  id: string;
  name: string;
  level: number;
  hp: number;
  maxHp: number;
  attack: number;
  defense: number;
  xpReward: number;
  goldReward: number;
  imageUrl?: string;
}

// Friends types
export interface Friend {
  id: string;
  username: string;
  level: number;
  avatarUrl?: string;
  streak: number;
  status: 'online' | 'offline' | 'away';
}

// Leaderboard types
export interface LeaderboardEntry {
  rank: number;
  userId: string;
  username: string;
  level: number;
  xp: number;
  streak: number;
  avatarUrl?: string;
}

// Stats types
export interface DailyStats {
  date: string;
  habitsCompleted: number;
  tasksCompleted: number;
  xpEarned: number;
  goldEarned: number;
}

export interface UserStats {
  totalHabitsCompleted: number;
  totalTasksCompleted: number;
  longestStreak: number;
  currentStreak: number;
  totalXpEarned: number;
  totalGoldEarned: number;
  dailyStats: DailyStats[];
}

// API types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Auth types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  username: string;
  password: string;
  confirmPassword: string;
}

export interface AuthResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
}
