"use client"

import ReactMarkdown from "react-markdown"
import { memo, useState } from "react"
import { ChevronDown, ChevronUp, Code, BarChart3, Table2, Download, Copy, Eye, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import type { Components } from "react-markdown"

interface MarkdownRendererProps {
  content: string
  className?: string
  enableAnalytics?: boolean // Julius.ai-style analytics features
}

/**
 * Julius.ai-inspired result card for data analysis outputs
 */
function AnalysisResultCard({ 
  type, 
  title, 
  content, 
  metadata 
}: { 
  type: 'insight' | 'summary' | 'recommendation'
  title: string
  content: string
  metadata?: { confidence?: number; dataPoints?: number }
}) {
  const getIcon = () => {
    switch (type) {
      case 'insight': return <Sparkles className="h-4 w-4 text-foreground" />
      case 'summary': return <BarChart3 className="h-4 w-4 text-accent" />
      case 'recommendation': return <Eye className="h-4 w-4 text-muted-foreground" />
    }
  }

  const getBadgeColor = () => {
    switch (type) {
      case 'insight': return 'bg-muted text-foreground border-border'
      case 'summary': return 'bg-accent/10 text-accent border-accent/20'
      case 'recommendation': return 'bg-muted text-muted-foreground border-border'
    }
  }

  return (
    <Card className="my-3 border-l-4 border-l-accent bg-gradient-to-r from-accent/5 to-transparent">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getIcon()}
            <Badge className={`text-xs ${getBadgeColor()}`}>
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </Badge>
          </div>
          {metadata?.confidence && (
            <Badge variant="outline" className="text-xs">
              {Math.round(metadata.confidence * 100)}% confidence
            </Badge>
          )}
        </div>
        <h4 className="font-semibold text-sm text-foreground">{title}</h4>
      </CardHeader>
      <CardContent className="pt-0">
        <p className="text-sm text-muted-foreground leading-relaxed">{content}</p>
        {metadata?.dataPoints && (
          <p className="text-xs text-muted-foreground mt-2">
            Based on {metadata.dataPoints.toLocaleString()} data points
          </p>
        )}
      </CardContent>
    </Card>
  )
}

/**
 * Enhanced collapsible code block with Julius.ai-style actions
 */
function CollapsibleCodeBlock({ language, content }: { language: string; content: string }) {
  const [isExpanded, setIsExpanded] = useState(false)
  
  const getTitle = () => {
    switch (language) {
      case 'chart':
        return 'Chart Configuration'
      case 'table':
        return 'Table Data'
      case 'sql':
        return 'SQL Query'
      case 'python':
        return 'Python Code'
      case 'analysis':
        return 'Analysis Results'
      default:
        return 'Code'
    }
  }

  const getIcon = () => {
    switch (language) {
      case 'chart':
        return <BarChart3 className="h-4 w-4" />
      case 'table':
        return <Table2 className="h-4 w-4" />
      default:
        return <Code className="h-4 w-4" />
    }
  }

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(content)
  }
  
  return (
    <div className="border border-gray-300 rounded my-1 bg-gray-100 shadow-none">
      <div className="flex items-center justify-between px-2 py-1 border-b border-gray-300">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="h-auto p-0 font-normal hover:bg-accent/10"
        >
          <div className="flex items-center gap-2 text-gray-600">
            {getIcon()}
            <span className="text-sm font-medium text-gray-800">{getTitle()}</span>
          </div>
          {isExpanded ? <ChevronUp className="h-4 w-4 ml-2 text-gray-600" /> : <ChevronDown className="h-4 w-4 ml-2 text-gray-600" />}
        </Button>
        
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={copyToClipboard}
            className="h-7 w-7 p-0 hover:bg-gray-200 text-gray-600 hover:text-gray-800"
          >
            <Copy className="h-3 w-3" />
          </Button>
          {(language === 'chart' || language === 'table') && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0 hover:bg-gray-200 text-gray-600 hover:text-gray-800"
            >
              <Download className="h-3 w-3" />
            </Button>
          )}
        </div>
      </div>
      
      {isExpanded && (
        <div className="px-2 py-1 bg-gray-800 rounded-b">
          <pre className="text-sm font-mono overflow-x-auto leading-relaxed text-gray-100">
            <code className="text-gray-100">{content}</code>
          </pre>
        </div>
      )}
    </div>
  )
}

/**
 * Julius.ai-inspired data summary component
 */
function DataSummaryBlock({ summary }: { summary: any }) {
  return (
    <div className="my-3 p-4 bg-gradient-to-r from-accent/5 to-accent/10 border border-accent/20 rounded-lg">
      <div className="flex items-center gap-2 mb-2">
        <BarChart3 className="h-4 w-4 text-accent" />
        <span className="font-semibold text-sm text-foreground">Data Summary</span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
        {Object.entries(summary).map(([key, value]) => (
          <div key={key} className="text-center">
            <div className="font-bold text-lg text-foreground">{String(value)}</div>
            <div className="text-muted-foreground capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

// Enhanced markdown components with Julius.ai-style features
const markdownComponents: Partial<Components> = {
  // Remove all paragraph margins - let parent control spacing
  p: ({ children }) => <span className="block leading-relaxed">{children}</span>,
  
  // Enhanced lists with better spacing
  ul: ({ children }) => (
    <div className="my-2 space-y-1">
      {children}
    </div>
  ),
  ol: ({ children }) => (
    <div className="my-2 space-y-1">
      {children}
    </div>
  ),
  
  // Better list items
  li: ({ children }) => (
    <div className="flex items-start gap-2 pl-4 relative">
      <span className="w-1.5 h-1.5 bg-accent rounded-full mt-2 flex-shrink-0"></span>
      <span>{children}</span>
    </div>
  ),
  
  // Inline formatting
  strong: ({ children }) => <strong className="font-semibold text-foreground">{children}</strong>,
  em: ({ children }) => <em className="italic text-muted-foreground">{children}</em>,
  
  // Enhanced headings with app theme
  h1: ({ children }) => (
    <div className="border-b border-border pb-2 mb-3">
      <h1 className="text-xl font-bold text-foreground">{children}</h1>
    </div>
  ),
  h2: ({ children }) => (
    <h2 className="text-lg font-semibold text-foreground mt-4 mb-2 flex items-center gap-2">
      <span className="w-1 h-4 bg-accent rounded"></span>
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-base font-semibold text-foreground mt-3 mb-2">{children}</h3>
  ),
  
  // Enhanced code blocks
  code: ({ children, ...props }) => {
    const isBlock = props.className?.includes('language-')
    const language = props.className?.replace('language-', '') || ''
    
    if (isBlock) {
      // Check for special data analysis blocks
      const isDataBlock = ['chart', 'table', 'sql', 'python', 'analysis'].includes(language)
      
      if (isDataBlock) {
        return <CollapsibleCodeBlock language={language} content={String(children)} />
      }
      
      return (
        <div className="my-3 bg-muted border border-border rounded-lg overflow-hidden">
          <div className="px-3 py-2 bg-muted border-b border-border text-xs font-medium text-muted-foreground">
            {language || 'Code'}
          </div>
          <pre className="p-3 text-sm font-mono overflow-x-auto leading-relaxed text-foreground">
            <code>{children}</code>
          </pre>
        </div>
      )
    }
    
    return (
      <code className="bg-muted px-2 py-1 rounded text-sm font-mono text-foreground border border-border">
        {children}
      </code>
    )
  },
}

export const MarkdownRenderer = memo(function MarkdownRenderer({ 
  content, 
  className = "",
  enableAnalytics = false
}: MarkdownRendererProps) {
  // Enhanced content processing for Julius.ai-style features
  const processContent = (rawContent: string) => {
    let processed = rawContent

    // Replace standalone JSON objects that look like chart/table data
    processed = processed.replace(/```(?:json|chart|table)\n?(\{[\s\S]*?\})\n?```/g, (match, jsonContent) => {
      try {
        const parsed = JSON.parse(jsonContent)
        if (parsed.chartType || parsed.type === 'table' || parsed.columns) {
          const type = parsed.chartType ? 'chart' : 'table'
          return `\`\`\`${type}\n${jsonContent}\n\`\`\``
        }
      } catch (e) {
        // If not valid JSON, return original
      }
      return match
    })

    return processed
  }

  // Aggressive content normalization for chat context
  const processedContent = processContent(content)
  const normalizedContent = processedContent
    .replace(/\n{3,}/g, '\n\n') // Keep paragraph breaks but limit excessive spacing
    .replace(/^\s+|\s+$/g, '') // Trim whitespace
  
  return (
    <div 
      className={`prose prose-sm max-w-none leading-relaxed ${className}`}
      style={{ 
        lineHeight: '1.6',
        wordBreak: 'break-word'
      }}
    >
      <ReactMarkdown 
        components={markdownComponents}
        skipHtml={false} // Allow our custom HTML components
      >
        {normalizedContent}
      </ReactMarkdown>
    </div>
  )
})
