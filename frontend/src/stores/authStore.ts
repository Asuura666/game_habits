import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, Character } from '@/types';

interface AuthState {
  user: User | null;
  character: Character | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  hasCharacter: boolean;
  
  // Computed
  token: string | null;
  
  // Actions
  setUser: (user: User) => void;
  setCharacter: (character: Character | null) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  login: (user: User, accessToken: string, refreshToken: string) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
  setLoading: (loading: boolean) => void;
  fetchUser: () => Promise<void>;
  fetchCharacter: () => Promise<void>;
  checkCharacter: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      character: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: true,
      hasCharacter: false,

      // Getter for token
      get token() {
        return get().accessToken;
      },

      setUser: (user) => set({ user }),
      
      setCharacter: (character) => set({ 
        character, 
        hasCharacter: character !== null 
      }),
      
      setTokens: (accessToken, refreshToken) => 
        set({ accessToken, refreshToken }),
      
      login: (user, accessToken, refreshToken) =>
        set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
          isLoading: false,
        }),
      
      logout: () =>
        set({
          user: null,
          character: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
          hasCharacter: false,
        }),
      
      updateUser: (updates) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        })),
      
      setLoading: (isLoading) => set({ isLoading }),

      fetchUser: async () => {
        const { accessToken } = get();
        if (!accessToken) return;

        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${accessToken}`
            }
          });

          if (response.ok) {
            const user = await response.json();
            set({ user });
          }
        } catch (error) {
          console.error('Failed to fetch user:', error);
        }
      },

      fetchCharacter: async () => {
        const { accessToken } = get();
        if (!accessToken) return;

        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/characters/me`, {
            headers: {
              'Authorization': `Bearer ${accessToken}`
            }
          });

          if (response.ok) {
            const character = await response.json();
            set({ character, hasCharacter: true });
          } else if (response.status === 404) {
            set({ character: null, hasCharacter: false });
          }
        } catch (error) {
          console.error('Failed to fetch character:', error);
          set({ character: null, hasCharacter: false });
        }
      },

      checkCharacter: async () => {
        const { accessToken } = get();
        if (!accessToken) return false;

        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/characters/me`, {
            headers: {
              'Authorization': `Bearer ${accessToken}`
            }
          });

          const hasChar = response.ok;
          set({ hasCharacter: hasChar });
          
          if (hasChar) {
            const character = await response.json();
            set({ character });
          }
          
          return hasChar;
        } catch (error) {
          console.error('Failed to check character:', error);
          return false;
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        character: state.character,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
        hasCharacter: state.hasCharacter,
      }),
    }
  )
);
