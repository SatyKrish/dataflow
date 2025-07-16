"use client"

import ReactMarkdown from "react-markdown"
import { memo, useState } from "react"
import { ChevronDown, ChevronRight, Code } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { Components } from "react-markdown"

interface MarkdownRendererProps {
  content: string
  className?: string
}

/**
 * Collapsible code block for chart/table JSON data
 */
function CollapsibleCodeBlock({ language, content }: { language: string; content: string }) {
  const [isExpanded, setIsExpanded] = useState(false)
  
  const getTitle = () => {
    switch (language) {
      case 'chart':
        return 'Chart Configuration'
      case 'table':
        return 'Table Data'
      default:
        return 'Code'
    }
  }
  
  return (
    <div className="border border-border rounded-lg my-2 bg-muted/30">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full justify-between p-3 h-auto font-normal hover:bg-muted/50"
      >
        <div className="flex items-center gap-2 text-muted-foreground">
          <Code className="h-4 w-4" />
          <span className="text-sm">View {getTitle()}</span>
        </div>
        {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </Button>
      
      {isExpanded && (
        <div className="border-t border-border">
          <pre className="bg-muted p-3 rounded-b-lg text-sm font-mono overflow-x-auto">
            <code>{content}</code>
          </pre>
        </div>
      )}
    </div>
  )
}

/**
 * Chat-optimized markdown renderer with zero extra spacing
 * 
 * Inspired by chat-sdk.dev patterns:
 * - Flat structure with minimal nesting
 * - Zero margins by default, only add where needed
 * - Inline-first approach for chat messages
 * - Uses CSS Grid for precise spacing control
 */

// Chat-optimized components with zero default margins
const markdownComponents: Partial<Components> = {
  // Remove all paragraph margins - let parent control spacing
  p: ({ children }) => <span className="block">{children}</span>,
  
  // Inline lists with minimal spacing
  ul: ({ children }) => (
    <span className="block my-1">
      {children}
    </span>
  ),
  ol: ({ children }) => (
    <span className="block my-1">
      {children}
    </span>
  ),
  
  // Inline list items
  li: ({ children }) => (
    <span className="block pl-4 relative before:content-['•'] before:absolute before:left-0">
      {children}
    </span>
  ),
  
  // Inline formatting
  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
  em: ({ children }) => <em className="italic">{children}</em>,
  
  // Minimal heading spacing
  h1: ({ children }) => <span className="block text-lg font-bold my-1">{children}</span>,
  h2: ({ children }) => <span className="block text-base font-bold my-1">{children}</span>,
  h3: ({ children }) => <span className="block text-sm font-bold my-1">{children}</span>,
  
  // Inline code
  code: ({ children, ...props }) => {
    const isBlock = props.className?.includes('language-')
    const language = props.className?.replace('language-', '')
    
    if (isBlock) {
      // Check if this is a chart or table JSON block
      const isChartOrTable = language === 'chart' || language === 'table'
      
      if (isChartOrTable) {
        return <CollapsibleCodeBlock language={language} content={String(children)} />
      }
      
      return (
        <span className="block bg-muted p-2 rounded text-sm font-mono my-1 overflow-x-auto">
          {children}
        </span>
      )
    }
    
    return (
      <code className="bg-muted px-1 py-0.5 rounded text-sm font-mono">
        {children}
      </code>
    )
  },
  
  // Block code with minimal spacing
  pre: ({ children }) => (
    <span className="block bg-muted p-2 rounded font-mono text-sm my-1 overflow-x-auto">
      {children}
    </span>
  ),
}

export const MarkdownRenderer = memo(function MarkdownRenderer({ 
  content, 
  className = "" 
}: MarkdownRendererProps) {
  // Function to detect and hide standalone chart/table JSON
  const processContent = (rawContent: string) => {
    // Replace standalone JSON objects that look like chart/table data
    return rawContent.replace(/```(?:json|chart|table)\n?(\{[\s\S]*?\})\n?```/g, (match, jsonContent) => {
      try {
        const parsed = JSON.parse(jsonContent)
        if (parsed.chartType || parsed.type === 'table' || parsed.columns) {
          // Determine type based on content
          const type = parsed.chartType ? 'chart' : 'table'
          return `\`\`\`${type}\n${jsonContent}\n\`\`\``
        }
      } catch (e) {
        // If not valid JSON, return original
      }
      return match
    })
  }

  // Aggressive content normalization for chat context
  const processedContent = processContent(content)
  const normalizedContent = processedContent
    .replace(/\n{2,}/g, '\n') // Convert all multiple newlines to single newlines
    .replace(/^\s+|\s+$/g, '') // Trim all whitespace
    .replace(/\n\s+/g, '\n') // Remove indentation from new lines
  
  return (
    <div 
      className={`leading-tight space-y-0 ${className}`}
      style={{ 
        lineHeight: '1.4',
        wordBreak: 'break-word'
      }}
    >
      <ReactMarkdown 
        components={markdownComponents}
        skipHtml={true}
      >
        {normalizedContent}
      </ReactMarkdown>
    </div>
  )
})
