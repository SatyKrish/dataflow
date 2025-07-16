"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export type UserRole = 'data-analyst' | 'product-owner' | 'finance-analyst' | 'developer' | 'general'

interface UserContextProps {
  role: UserRole
  setRole: (role: UserRole) => void
  preferences: UserPreferences
  updatePreferences: (prefs: Partial<UserPreferences>) => void
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

  return (
    <UserContext.Provider value={{
      role,
      setRole: updateRole,
      preferences,
      updatePreferences
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

/**
 * Component for user role selection and onboarding
 */
export function RoleSelector() {
  const { role, setRole } = useUser()
  const [isOpen, setIsOpen] = useState(!role || role === 'general')

  const roles: { value: UserRole; label: string; description: string; icon: string }[] = [
    {
      value: 'data-analyst',
      label: 'Data Analyst',
      description: 'I work with large datasets and need advanced analytics',
      icon: '📊'
    },
    {
      value: 'finance-analyst',
      label: 'Finance Analyst',
      description: 'I analyze financial data and create reports',
      icon: '💰'
    },
    {
      value: 'product-owner',
      label: 'Product Owner',
      description: 'I need clear insights and KPI dashboards',
      icon: '🎯'
    },
    {
      value: 'developer',
      label: 'Developer',
      description: 'I build with data and need technical capabilities',
      icon: '👨‍💻'
    }
  ]

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="text-sm text-gray-500 hover:text-gray-700"
      >
        Role: {roles.find(r => r.value === role)?.label || 'General'}
      </button>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h2 className="text-xl font-semibold mb-4">Select Your Role</h2>
        <p className="text-gray-600 mb-6">
          This helps us optimize the interface for your specific needs.
        </p>
        
        <div className="space-y-3">
          {roles.map((roleOption) => (
            <button
              key={roleOption.value}
              onClick={() => {
                setRole(roleOption.value)
                setIsOpen(false)
              }}
              className={`w-full p-4 rounded-lg border-2 text-left transition-colors ${
                role === roleOption.value
                  ? 'border-red-500 bg-red-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start space-x-3">
                <span className="text-2xl">{roleOption.icon}</span>
                <div>
                  <div className="font-medium">{roleOption.label}</div>
                  <div className="text-sm text-gray-600">{roleOption.description}</div>
                </div>
              </div>
            </button>
          ))}
        </div>

        <button
          onClick={() => setIsOpen(false)}
          className="w-full mt-4 px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Continue
        </button>
      </div>
    </div>
  )
}
