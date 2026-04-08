import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import {
  getCurrentUser,
  signIn as apiSignIn,
  signUp as apiSignUp,
  signOut as apiSignOut,
  type AuthUser,
} from '../lib/authApi'

type AuthContextValue = {
  user: AuthUser | null
  isLoading: boolean
  signIn: (email: string, password: string) => Promise<void>
  signUp: (payload: {
    fullName: string
    email: string
    password: string
    role: 'student'
    sport?: string
    focusArea?: string
    dateOfBirth?: string
  }) => Promise<void>
  signOut: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)
const INTAKE_DRAFT_PREFIX = 'hamsai-athlete-intake-draft:'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    try {
      const currentUser = await getCurrentUser()
      setUser(currentUser)
    } catch {
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void refreshUser()
  }, [refreshUser])

  const signIn = useCallback(async (email: string, password: string) => {
    const currentUser = await apiSignIn({ email, password })
    setUser(currentUser)
  }, [])

  const signUp = useCallback(
    async (payload: {
      fullName: string
      email: string
      password: string
      role: 'student'
      sport?: string
      focusArea?: string
      dateOfBirth?: string
    }) => {
      const currentUser = await apiSignUp(payload)
      setUser(currentUser)
    },
    [],
  )

  const signOut = useCallback(async () => {
    await apiSignOut()
    if (typeof window !== 'undefined') {
      Object.keys(window.localStorage)
        .filter((key) => key.startsWith(INTAKE_DRAFT_PREFIX))
        .forEach((key) => window.localStorage.removeItem(key))
    }
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({
      user,
      isLoading,
      signIn,
      signUp,
      signOut,
      refreshUser,
    }),
    [user, isLoading, signIn, signUp, signOut, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)

  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }

  return context
}
