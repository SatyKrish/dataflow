"use client"

import { lazy, Suspense } from 'react'
import { Loader2 } from 'lucide-react'

// Lazy load the heavy chart renderer only when needed
const ChartRenderer = lazy(() => import('./chart-renderer').then(module => ({
  default: module.ChartRenderer
})))

// Lazy load mermaid diagram renderer  
const MermaidRenderer = lazy(() => import('./chat-message-mermaid-renderer').then(module => ({
  default: module.ChatMessageMermaidRenderer
})))

interface LazyChartRendererProps {
  artifact: {
    content: string
    type: 'code' | 'chart' | 'table' | 'diagram' | 'text'
    language?: string
  }
}

export function LazyChartRenderer({ artifact }: LazyChartRendererProps) {
  // Determine which renderer to use based on artifact type
  const isChart = artifact.type === 'chart' || 
    (artifact.language && ['json', 'javascript', 'typescript'].includes(artifact.language) && 
     artifact.content.includes('data'))

  const isMermaid = artifact.language === 'mermaid' || 
    artifact.content.includes('graph') || 
    artifact.content.includes('flowchart')

  if (isMermaid) {
    return (
      <Suspense fallback={
        <div className="flex items-center justify-center p-8">
          <Loader2 className="w-6 h-6 animate-spin text-red-500" />
          <span className="ml-2 text-sm text-gray-600">Loading diagram...</span>
        </div>
      }>
        <MermaidRenderer code={artifact.content} />
      </Suspense>
    )
  }

  if (isChart) {
    return (
      <Suspense fallback={
        <div className="flex items-center justify-center p-8">
          <Loader2 className="w-6 h-6 animate-spin text-red-500" />
          <span className="ml-2 text-sm text-gray-600">Loading chart...</span>
        </div>
      }>
        <ChartRenderer artifact={artifact} />
      </Suspense>
    )
  }

  // Return null for non-chart artifacts
  return null
}
