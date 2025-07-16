/**
 * Advanced memory management and caching for chat application
 * Optimized for professional users handling large datasets
 */

import { useRef, useCallback, useEffect } from 'react'
import type { Message } from '@ai-sdk/react'

// LRU Cache for message storage
class LRUCache<K, V> {
  private cache = new Map<K, V>()
  private readonly maxSize: number

  constructor(maxSize: number = 100) {
    this.maxSize = maxSize
  }

  get(key: K): V | undefined {
    const value = this.cache.get(key)
    if (value !== undefined) {
      // Move to end (most recently used)
      this.cache.delete(key)
      this.cache.set(key, value)
    }
    return value
  }

  set(key: K, value: V): void {
    if (this.cache.has(key)) {
      this.cache.delete(key)
    } else if (this.cache.size >= this.maxSize) {
      // Remove least recently used (first item)
      const firstKey = this.cache.keys().next().value
      if (firstKey !== undefined) {
        this.cache.delete(firstKey)
      }
    }
    this.cache.set(key, value)
  }

  clear(): void {
    this.cache.clear()
  }

  size(): number {
    return this.cache.size
  }
}

// Message processing cache
const messageProcessingCache = new LRUCache<string, any>(200)
const artifactCache = new LRUCache<string, any>(50)

/**
 * Hook for efficient message caching and retrieval
 */
export function useMessageCache() {
  const cacheRef = useRef(messageProcessingCache)

  const getCachedProcessedMessage = useCallback((messageId: string) => {
    return cacheRef.current.get(messageId)
  }, [])

  const setCachedProcessedMessage = useCallback((messageId: string, processed: any) => {
    cacheRef.current.set(messageId, processed)
  }, [])

  const clearCache = useCallback(() => {
    cacheRef.current.clear()
  }, [])

  return {
    getCachedProcessedMessage,
    setCachedProcessedMessage,
    clearCache
  }
}

/**
 * Hook for artifact caching with size limits
 */
export function useArtifactCache() {
  const cacheRef = useRef(artifactCache)

  const getCachedArtifact = useCallback((artifactId: string) => {
    return cacheRef.current.get(artifactId)
  }, [])

  const setCachedArtifact = useCallback((artifactId: string, artifact: any) => {
    // Only cache artifacts smaller than 1MB
    const size = JSON.stringify(artifact).length
    if (size < 1024 * 1024) {
      cacheRef.current.set(artifactId, artifact)
    }
  }, [])

  return {
    getCachedArtifact,
    setCachedArtifact
  }
}

/**
 * Memory pressure monitoring and cleanup
 */
export function useMemoryManagement() {
  const cleanupRef = useRef<(() => void) | undefined>(undefined)

  const checkMemoryPressure = useCallback(() => {
    // Check if performance.memory is available (Chrome)
    if ('memory' in performance) {
      const memInfo = (performance as any).memory
      const usedMB = memInfo.usedJSHeapSize / 1024 / 1024
      const totalMB = memInfo.totalJSHeapSize / 1024 / 1024
      const limitMB = memInfo.jsHeapSizeLimit / 1024 / 1024

      // If using more than 80% of available memory, trigger cleanup
      if (usedMB > limitMB * 0.8) {
        console.warn(`🚨 High memory usage detected: ${usedMB.toFixed(2)}MB / ${limitMB.toFixed(2)}MB`)
        return true
      }
    }
    return false
  }, [])

  const performCleanup = useCallback(() => {
    // Clear caches
    messageProcessingCache.clear()
    artifactCache.clear()
    
    // Clear any registered cleanup functions
    if (cleanupRef.current) {
      cleanupRef.current()
    }

    // Force garbage collection if available
    if ('gc' in window && typeof (window as any).gc === 'function') {
      ;(window as any).gc()
    }

    console.log('🧹 Memory cleanup performed')
  }, [])

  const registerCleanupFunction = useCallback((cleanup: () => void) => {
    cleanupRef.current = cleanup
  }, [])

  // Monitor memory usage periodically
  useEffect(() => {
    const interval = setInterval(() => {
      if (checkMemoryPressure()) {
        performCleanup()
      }
    }, 30000) // Check every 30 seconds

    return () => clearInterval(interval)
  }, [checkMemoryPressure, performCleanup])

  return {
    checkMemoryPressure,
    performCleanup,
    registerCleanupFunction
  }
}

/**
 * Debounced local storage for chat sessions
 */
export function useDebouncedStorage(delay: number = 1000) {
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  const debouncedSave = useCallback((key: string, value: any) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }

    timeoutRef.current = setTimeout(() => {
      try {
        localStorage.setItem(key, JSON.stringify(value))
      } catch (error) {
        console.error('Failed to save to localStorage:', error)
        
        // If storage is full, clear some old data
        if (error instanceof DOMException && error.code === 22) {
          console.warn('LocalStorage quota exceeded, clearing old sessions...')
          clearOldSessions()
          
          // Try saving again
          try {
            localStorage.setItem(key, JSON.stringify(value))
          } catch (retryError) {
            console.error('Failed to save even after cleanup:', retryError)
          }
        }
      }
    }, delay)
  }, [delay])

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return { debouncedSave }
}

/**
 * Clear old chat sessions to free up storage space
 */
function clearOldSessions() {
  try {
    const sessions = JSON.parse(localStorage.getItem('agent-chat-sessions') || '{}')
    const now = Date.now()
    const oneWeekAgo = now - 7 * 24 * 60 * 60 * 1000

    // Keep only sessions from the last week
    const recentSessions = Object.entries(sessions)
      .filter(([_, session]: [string, any]) => 
        session.updatedAt && new Date(session.updatedAt).getTime() > oneWeekAgo
      )
      .reduce((acc, [id, session]) => {
        acc[id] = session
        return acc
      }, {} as Record<string, any>)

    localStorage.setItem('agent-chat-sessions', JSON.stringify(recentSessions))
    console.log(`🧹 Cleared ${Object.keys(sessions).length - Object.keys(recentSessions).length} old sessions`)
  } catch (error) {
    console.error('Failed to clear old sessions:', error)
  }
}

/**
 * Optimized data structure for large message lists
 */
export class MessageBuffer {
  private buffer: Message[] = []
  private readonly maxSize: number
  private readonly chunkSize: number

  constructor(maxSize: number = 1000, chunkSize: number = 100) {
    this.maxSize = maxSize
    this.chunkSize = chunkSize
  }

  add(message: Message): void {
    this.buffer.push(message)
    
    if (this.buffer.length > this.maxSize) {
      // Remove oldest chunk
      this.buffer.splice(0, this.chunkSize)
    }
  }

  getRecent(count: number = 50): Message[] {
    return this.buffer.slice(-count)
  }

  getAll(): Message[] {
    return [...this.buffer]
  }

  clear(): void {
    this.buffer = []
  }

  size(): number {
    return this.buffer.length
  }
}
