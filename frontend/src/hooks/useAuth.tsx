import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { User, LoginCredentials, AuthContextType } from '@/types'
import { authService } from '@/services'

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for stored token on mount
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))

      // Verify token is still valid
      authService
        .getCurrentUser()
        .then((currentUser) => {
          setUser(currentUser)
          localStorage.setItem('user', JSON.stringify(currentUser))
        })
        .catch(() => {
          // Token invalid, clear storage
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          setToken(null)
          setUser(null)
        })
        .finally(() => {
          setIsLoading(false)
        })
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (credentials: LoginCredentials) => {
    const tokenResponse = await authService.login(credentials)
    const accessToken = tokenResponse.access_token

    localStorage.setItem('token', accessToken)
    setToken(accessToken)

    const currentUser = await authService.getCurrentUser()
    localStorage.setItem('user', JSON.stringify(currentUser))
    setUser(currentUser)
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated: !!token && !!user,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
