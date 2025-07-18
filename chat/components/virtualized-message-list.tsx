"use client"

import { Message } from "@ai-sdk/react"
import { MessageBubble } from "@/components/message-bubble"
import { useEffect, useRef, useCallback, useState, useMemo } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Loader2 } from "lucide-react"

interface VirtualizedMessageListProps {
  messages: Message[]
  onArtifactToggle?: (artifactId?: string) => void
  isLoading: boolean
}

const ITEM_HEIGHT = 120 // Estimated height per message
const BUFFER_SIZE = 5 // Number of items to render outside viewport

export function VirtualizedMessageList({ 
  messages, 
  onArtifactToggle, 
  isLoading 
}: VirtualizedMessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [scrollTop, setScrollTop] = useState(0)
  const [containerHeight, setContainerHeight] = useState(600)

  // Calculate visible range
  const visibleRange = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / ITEM_HEIGHT) - BUFFER_SIZE)
    const endIndex = Math.min(
      messages.length - 1,
      Math.ceil((scrollTop + containerHeight) / ITEM_HEIGHT) + BUFFER_SIZE
    )
    return { startIndex, endIndex }
  }, [scrollTop, containerHeight, messages.length])

  // Get visible messages
  const visibleMessages = useMemo(() => {
    return messages.slice(visibleRange.startIndex, visibleRange.endIndex + 1)
  }, [messages, visibleRange])

  // Handle scroll events with throttling
  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    const target = event.currentTarget
    setScrollTop(target.scrollTop)
  }, [])

  // Update container height on resize
  useEffect(() => {
    const updateHeight = () => {
      if (containerRef.current) {
        setContainerHeight(containerRef.current.clientHeight)
      }
    }

    updateHeight()
    window.addEventListener('resize', updateHeight)
    return () => window.removeEventListener('resize', updateHeight)
  }, [])

  // Auto-scroll to bottom for new messages
  useEffect(() => {
    if (containerRef.current && messages.length > 0) {
      const isNearBottom = scrollTop + containerHeight >= 
        (messages.length * ITEM_HEIGHT) - 200

      if (isNearBottom || messages.length === 1) {
        setTimeout(() => {
          if (containerRef.current) {
            containerRef.current.scrollTop = messages.length * ITEM_HEIGHT
          }
        }, 100)
      }
    }
  }, [messages.length, scrollTop, containerHeight])

  // For small message counts, use regular rendering
  if (messages.length < 20) {
    return (
      <ScrollArea className="flex-1 h-full" ref={containerRef}>
        <div className="p-4 sm:p-6 space-y-3 sm:space-y-4 min-h-full">
          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              onArtifactToggle={onArtifactToggle}
            />
          ))}
          {isLoading && (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
              <span className="text-sm text-gray-500">AI is thinking...</span>
            </div>
          )}
        </div>
      </ScrollArea>
    )
  }

  // Virtualized rendering for large message lists
  const totalHeight = messages.length * ITEM_HEIGHT
  const offsetY = visibleRange.startIndex * ITEM_HEIGHT

  return (
    <div 
      ref={containerRef}
      className="flex-1 h-full overflow-auto"
      onScroll={handleScroll}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div 
          style={{ 
            transform: `translateY(${offsetY}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0
          }}
          className="p-4 sm:p-6 space-y-3 sm:space-y-4"
        >
          {visibleMessages.map((message, index) => (
            <div 
              key={message.id}
              style={{ minHeight: ITEM_HEIGHT }}
            >
              <MessageBubble
                message={message}
                onArtifactToggle={onArtifactToggle}
              />
            </div>
          ))}
          {isLoading && visibleRange.endIndex >= messages.length - 1 && (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
              <span className="text-sm text-gray-500">AI is thinking...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
