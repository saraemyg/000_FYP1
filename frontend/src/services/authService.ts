import api from './api'
import { LoginCredentials, RegisterData, Token, User } from '@/types'

export const authService = {
  async login(credentials: LoginCredentials): Promise<Token> {
    const response = await api.post<Token>('/auth/login', credentials)
    return response.data
  },

  async register(data: RegisterData): Promise<User> {
    const response = await api.post<User>('/auth/register', data)
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  async listUsers(): Promise<User[]> {
    const response = await api.get<User[]>('/auth/users')
    return response.data
  },

  async toggleUserActive(userId: number): Promise<User> {
    const response = await api.put<User>(`/auth/users/${userId}/toggle-active`)
    return response.data
  },
}
