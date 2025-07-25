import { create } from 'zustand'
import { api } from '@/lib/api'

interface User {
  id: string
  email: string
  name: string
  role: string
  institution?: string
  department?: string
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: any) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (email, password) => {
    try {
      await api.login(email, password)
      const response = await api.getCurrentUser()
      set({ user: response.data, isAuthenticated: true })
    } catch (error) {
      throw error
    }
  },

  register: async (data) => {
    try {
      await api.register(data)
      await api.login(data.email, data.password)
      const response = await api.getCurrentUser()
      set({ user: response.data, isAuthenticated: true })
    } catch (error) {
      throw error
    }
  },

  logout: () => {
    api.logout()
    set({ user: null, isAuthenticated: false })
  },

  fetchUser: async () => {
    try {
      set({ isLoading: true })
      const response = await api.getCurrentUser()
      set({ user: response.data, isAuthenticated: true })
    } catch (error) {
      set({ user: null, isAuthenticated: false })
    } finally {
      set({ isLoading: false })
    }
  },
}))