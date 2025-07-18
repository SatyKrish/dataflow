"use client"

import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  Monitor, 
  Zap, 
  Database, 
  Clock, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { useUser } from './user-context'

interface PerformanceMetrics {
  fps: number
  memoryUsage: number
  memoryLimit: number
  loadTime: number
  renderTime: number
  cacheHitRate: number
  apiResponseTime: number
  messageCount: number
  lastUpdated: number
}

export function PerformanceDashboard() {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    fps: 60,
    memoryUsage: 0,
    memoryLimit: 0,
    loadTime: 0,
    renderTime: 0,
    cacheHitRate: 0,
    apiResponseTime: 0,
    messageCount: 0,
    lastUpdated: Date.now()
  })
  const [isVisible, setIsVisible] = useState(false)
  const [alerts, setAlerts] = useState<string[]>([])
  const frameCountRef = useRef(0)
  const lastTimeRef = useRef(performance.now())
  const { role, preferences } = useUser()

  // Performance monitoring
  useEffect(() => {
    let animationId: number

    const measurePerformance = () => {
      frameCountRef.current++
      const now = performance.now()
      const delta = now - lastTimeRef.current

      if (delta >= 1000) {
        const fps = Math.round((frameCountRef.current * 1000) / delta)
        frameCountRef.current = 0
        lastTimeRef.current = now

        // Get memory info if available
        let memoryUsage = 0
        let memoryLimit = 0
        if ('memory' in performance) {
          const memInfo = (performance as any).memory
          memoryUsage = memInfo.usedJSHeapSize / 1024 / 1024 // MB
          memoryLimit = memInfo.jsHeapSizeLimit / 1024 / 1024 // MB
        }

        // Update metrics
        setMetrics(prev => ({
          ...prev,
          fps,
          memoryUsage,
          memoryLimit,
          lastUpdated: Date.now()
        }))

        // Check for performance issues
        checkPerformanceAlerts(fps, memoryUsage, memoryLimit)
      }

      animationId = requestAnimationFrame(measurePerformance)
    }

    if (isVisible) {
      animationId = requestAnimationFrame(measurePerformance)
    }

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId)
      }
    }
  }, [isVisible])

  const checkPerformanceAlerts = (fps: number, memoryUsage: number, memoryLimit: number) => {
    const newAlerts: string[] = []

    if (fps < 30) {
      newAlerts.push(`Low FPS: ${fps}fps`)
    }

    if (memoryLimit > 0 && memoryUsage > memoryLimit * 0.8) {
      newAlerts.push(`High memory usage: ${memoryUsage.toFixed(1)}MB`)
    }

    if (metrics.apiResponseTime > 2000) {
      newAlerts.push(`Slow API response: ${metrics.apiResponseTime}ms`)
    }

    setAlerts(newAlerts)
  }

  const getPerformanceStatus = () => {
    if (alerts.length > 0) return 'warning'
    if (metrics.fps >= 45 && metrics.memoryUsage < metrics.memoryLimit * 0.6) return 'good'
    return 'moderate'
  }

  const getStatusIcon = () => {
    const status = getPerformanceStatus()
    switch (status) {
      case 'good': return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'warning': return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      default: return <XCircle className="w-4 h-4 text-red-500" />
    }
  }

  const getOptimizationSuggestions = () => {
    const suggestions: string[] = []
    
    if (metrics.fps < 30) {
      suggestions.push('Consider reducing animation effects')
      suggestions.push('Enable compact mode for better performance')
    }
    
    if (metrics.memoryUsage > metrics.memoryLimit * 0.7) {
      suggestions.push('Clear browser cache and restart')
      suggestions.push('Close other browser tabs')
    }
    
    if (metrics.messageCount > 100) {
      suggestions.push('Consider archiving old conversations')
    }

    return suggestions
  }

  if (!isVisible) {
    return (
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsVisible(true)}
        className="fixed bottom-4 right-4 z-50"
      >
        <Monitor className="w-4 h-4 mr-2" />
        Performance {getStatusIcon()}
      </Button>
    )
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-80">
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center justify-between">
            <span className="flex items-center">
              <Monitor className="w-4 h-4 mr-2" />
              Performance Monitor
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsVisible(false)}
            >
              ×
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          {/* Overall Status */}
          <div className="flex items-center justify-between">
            <span>Status</span>
            <div className="flex items-center space-x-2">
              {getStatusIcon()}
              <Badge variant={alerts.length > 0 ? "destructive" : "default"}>
                {getPerformanceStatus()}
              </Badge>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Zap className="w-3 h-3 mr-1" />
                <span>FPS</span>
              </div>
              <span className={metrics.fps < 30 ? 'text-red-500' : 'text-green-500'}>
                {metrics.fps}
              </span>
            </div>

            {metrics.memoryLimit > 0 && (
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Database className="w-3 h-3 mr-1" />
                    <span>Memory</span>
                  </div>
                  <span>{metrics.memoryUsage.toFixed(1)}MB</span>
                </div>
                <Progress 
                  value={(metrics.memoryUsage / metrics.memoryLimit) * 100} 
                  className="h-1"
                />
              </div>
            )}

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Clock className="w-3 h-3 mr-1" />
                <span>API Response</span>
              </div>
              <span className={metrics.apiResponseTime > 1000 ? 'text-yellow-500' : 'text-green-500'}>
                {metrics.apiResponseTime}ms
              </span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <TrendingUp className="w-3 h-3 mr-1" />
                <span>Messages</span>
              </div>
              <span>{metrics.messageCount}</span>
            </div>
          </div>

          {/* Alerts */}
          {alerts.length > 0 && (
            <div className="space-y-1">
              <div className="text-xs font-medium text-yellow-600">Alerts:</div>
              {alerts.map((alert, index) => (
                <div key={index} className="text-xs text-yellow-600 flex items-center">
                  <AlertTriangle className="w-3 h-3 mr-1" />
                  {alert}
                </div>
              ))}
            </div>
          )}

          {/* Role-specific optimizations */}
          <div className="pt-2 border-t">
            <div className="text-xs text-gray-500 mb-1">
              Optimized for: {role.replace('-', ' ')}
            </div>
            <div className="text-xs">
              Max data points: {preferences.maxDataPoints.toLocaleString()}
            </div>
            <div className="text-xs">
              Animations: {preferences.enableAnimations ? 'On' : 'Off'}
            </div>
          </div>

          {/* Suggestions */}
          {getOptimizationSuggestions().length > 0 && (
            <div className="space-y-1">
              <div className="text-xs font-medium">Suggestions:</div>
              {getOptimizationSuggestions().slice(0, 2).map((suggestion, index) => (
                <div key={index} className="text-xs text-gray-600">
                  • {suggestion}
                </div>
              ))}
            </div>
          )}

          {/* Quick Actions */}
          <div className="flex space-x-2 pt-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => window.location.reload()}
              className="text-xs"
            >
              Refresh
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                if ('gc' in window && typeof (window as any).gc === 'function') {
                  ;(window as any).gc()
                }
              }}
              className="text-xs"
            >
              Free Memory
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
