export interface User {
  user_id: number
  username: string
  email: string
  role: 'admin' | 'security_personnel'
  created_at: string
  last_login: string | null
  is_active: boolean
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  role: 'admin' | 'security_personnel'
}

export interface Token {
  access_token: string
  token_type: string
}

export interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  logout: () => void
}
