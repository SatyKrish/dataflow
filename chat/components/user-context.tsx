"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export type UserRole = 'data-analyst' | 'product-owner' | 'finance-analyst' | 'developer' | 'general'

interface UserContextProps {
  role: UserRole
  setRole: (role: UserRole) => void
  preferences: UserPreferences
  updatePreferences: (prefs: Partial<UserPreferences>) => void
  // Method for backend to update role based on conversation analysis
  updateRoleFromBackend: (role: UserRole) => void
}

interface UserPreferences {
  // Performance preferences
  enableAnimations: boolean
  maxDataPoints: number
  autoRefresh: boolean
  compactMode: boolean
  
  // Display preferences  
  chartTheme: 'professional' | 'analytical' | 'business' | 'technical'
  decimalPrecision: number
  showAdvancedFeatures: boolean
  
  // Workflow preferences
  defaultChartType: string
  favoriteTools: string[]
  quickActions: string[]
}

const defaultPreferences: UserPreferences = {
  enableAnimations: true,
  maxDataPoints: 1000,
  autoRefresh: false,
  compactMode: false,
  chartTheme: 'professional',
  decimalPrecision: 2,
  showAdvancedFeatures: false,
  defaultChartType: 'bar',
  favoriteTools: [],
  quickActions: []
}

const roleBasedDefaults: Record<UserRole, Partial<UserPreferences>> = {
  'data-analyst': {
    maxDataPoints: 5000,
    chartTheme: 'analytical',
    decimalPrecision: 4,
    showAdvancedFeatures: true,
    enableAnimations: false, // Better performance for large datasets
    defaultChartType: 'scatter',
    quickActions: ['statistical-summary', 'correlation-analysis', 'data-export']
  },
  'finance-analyst': {
    maxDataPoints: 2000,
    chartTheme: 'professional',
    decimalPrecision: 2,
    showAdvancedFeatures: true,
    defaultChartType: 'line',
    quickActions: ['trend-analysis', 'variance-report', 'financial-summary']
  },
  'product-owner': {
    maxDataPoints: 500,
    chartTheme: 'business',
    decimalPrecision: 1,
    showAdvancedFeatures: false,
    enableAnimations: true,
    defaultChartType: 'bar',
    quickActions: ['kpi-dashboard', 'goal-tracking', 'user-metrics']
  },
  'developer': {
    maxDataPoints: 10000,
    chartTheme: 'technical',
    decimalPrecision: 6,
    showAdvancedFeatures: true,
    enableAnimations: false,
    compactMode: true,
    defaultChartType: 'table',
    quickActions: ['api-explorer', 'data-schema', 'performance-metrics']
  },
  'general': defaultPreferences
}

const UserContext = createContext<UserContextProps | undefined>(undefined)

/**
 * User Context Provider
 * 
 * Manages user roles and preferences for persona-based UI optimization.
 * Role determination is handled by the backend based on conversation analysis.
 */
export function UserProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<UserRole>('general')
  const [preferences, setPreferences] = useState<UserPreferences>(defaultPreferences)

  // Load preferences from localStorage on mount
  useEffect(() => {
    try {
      const savedRole = localStorage.getItem('user-role') as UserRole
      const savedPreferences = localStorage.getItem('user-preferences')
      
      if (savedRole && roleBasedDefaults[savedRole]) {
        setRole(savedRole)
        const basePrefs = { ...defaultPreferences, ...roleBasedDefaults[savedRole] }
        
        if (savedPreferences) {
          const parsedPrefs = JSON.parse(savedPreferences)
          setPreferences({ ...basePrefs, ...parsedPrefs })
        } else {
          setPreferences(basePrefs)
        }
      }
    } catch (error) {
      console.error('Failed to load user preferences:', error)
    }
  }, [])

  // Update role and apply role-based defaults
  const updateRole = (newRole: UserRole) => {
    setRole(newRole)
    const roleDefaults = roleBasedDefaults[newRole] || {}
    setPreferences(prev => ({ ...prev, ...roleDefaults }))
    
    localStorage.setItem('user-role', newRole)
    localStorage.setItem('user-preferences', JSON.stringify({ 
      ...preferences, 
      ...roleDefaults 
    }))
  }

  // Update specific preferences
  const updatePreferences = (newPrefs: Partial<UserPreferences>) => {
    const updated = { ...preferences, ...newPrefs }
    setPreferences(updated)
    localStorage.setItem('user-preferences', JSON.stringify(updated))
  }

  // Method for backend to programmatically update role
  const updateRoleFromBackend = (newRole: UserRole) => {
    console.log(`🤖 Backend detected user role: ${newRole}`)
    updateRole(newRole)
  }

  return (
    <UserContext.Provider value={{
      role,
      setRole: updateRole,
      preferences,
      updatePreferences,
      updateRoleFromBackend
    }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}

/**
 * Hook for role-specific performance optimizations
 */
export function useRoleOptimizations() {
  const { role, preferences } = useUser()

  const getOptimizedSettings = () => {
    const base = {
      // Disable heavy features for better performance
      enableVirtualScrolling: preferences.maxDataPoints > 1000,
      enableLazyLoading: true,
      throttleDelay: preferences.enableAnimations ? 100 : 50,
      maxCacheSize: role === 'developer' ? 500 : 200,
    }

    switch (role) {
      case 'data-analyst':
        return {
          ...base,
          enableStatisticalCalculations: true,
          enableDataProfiling: true,
          chartUpdateDelay: 200, // Slower updates for complex calculations
          enableMemoryOptimization: true,
        }

      case 'finance-analyst':
        return {
          ...base,
          enableTrendAnalysis: true,
          enableForecasting: true,
          chartUpdateDelay: 150,
          precisionCalculations: true,
        }

      case 'product-owner':
        return {
          ...base,
          enableSimpleVisualization: true,
          chartUpdateDelay: 100,
          prioritizeResponsiveness: true,
        }

      case 'developer':
        return {
          ...base,
          enableDebugMode: true,
          enablePerformanceMonitoring: true,
          chartUpdateDelay: 50,
          enableAdvancedCaching: true,
        }

      default:
        return base
    }
  }

  return {
    optimizedSettings: getOptimizedSettings(),
    isHighPerformanceRole: ['data-analyst', 'developer'].includes(role),
    requiresRealTime: role === 'developer',
    prefersSimplicity: role === 'product-owner'
  }
}
