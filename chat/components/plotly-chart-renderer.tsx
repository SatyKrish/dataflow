"use client"

import React, { useState, useEffect, useMemo } from "react"
import dynamic from "next/dynamic"
import { Loader2, AlertCircle } from "lucide-react"
import type { PlotParams } from "react-plotly.js"

// Dynamically import Plotly to reduce initial bundle size
const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center p-8">
      <Loader2 className="w-6 h-6 animate-spin text-red-500" />
      <span className="ml-2 text-sm text-gray-600">Loading chart...</span>
    </div>
  ),
}) as React.ComponentType<PlotParams>

interface PlotlyChartRendererProps {
  artifact: {
    content: string
  }
}

// Enhanced color palette optimized for data analysis
const COLORS = [
  "#dc2626", // Red (primary accent)
  "#2563eb", // Blue
  "#059669", // Green
  "#d97706", // Orange
  "#7c3aed", // Purple
  "#db2777", // Pink
  "#0891b2", // Cyan
  "#65a30d", // Lime
  "#dc2626", // Red variations
  "#1e40af", // Dark Blue
  "#047857", // Dark Green
  "#92400e", // Dark Orange
  "#6b21a8", // Dark Purple
  "#be185d", // Dark Pink
  "#0e7490", // Dark Cyan
  "#4d7c0f", // Dark Lime
]

// Professional chart theme for business users
const PLOTLY_THEME = {
  layout: {
    font: {
      family: "Inter, Helvetica Neue, Helvetica, Arial, sans-serif",
      size: 12,
      color: "#374151",
    },
    paper_bgcolor: "#ffffff",
    plot_bgcolor: "#ffffff",
    colorway: COLORS,
    margin: { l: 60, r: 30, t: 60, b: 60 },
    showlegend: true,
    legend: {
      orientation: "v",
      x: 1.02,
      y: 1,
      bgcolor: "rgba(255,255,255,0.8)",
      bordercolor: "#e5e7eb",
      borderwidth: 1,
    },
    xaxis: {
      gridcolor: "#f3f4f6",
      linecolor: "#d1d5db",
      tickcolor: "#d1d5db",
      showgrid: true,
      zeroline: false,
    },
    yaxis: {
      gridcolor: "#f3f4f6",
      linecolor: "#d1d5db", 
      tickcolor: "#d1d5db",
      showgrid: true,
      zeroline: false,
    },
  },
  config: {
    displayModeBar: true,
    modeBarButtonsToRemove: ["lasso2d", "select2d"] as any,
    displaylogo: false,
    toImageButtonOptions: {
      format: "png" as const,
      filename: "chart",
      height: 500,
      width: 700,
      scale: 1,
    },
  },
}

// Function to clean JSON by removing comments and extracting from code blocks
function cleanJsonString(jsonString: string): string {
  // Remove markdown code block markers if present
  let cleaned = jsonString.replace(/^```(?:chart|json)?\s*/m, "")
  cleaned = cleaned.replace(/```\s*$/m, "")
  
  // Remove single-line comments (// comment)
  cleaned = cleaned.replace(/\/\/.*$/gm, "")

  // Remove multi-line comments (/* comment */)
  cleaned = cleaned.replace(/\/\*[\s\S]*?\*\//g, "")

  // Remove trailing commas before closing brackets/braces
  cleaned = cleaned.replace(/,(\s*[}\]])/g, "$1")

  return cleaned.trim()
}

// Convert data format to Plotly format
function convertToPlotlyFormat(chartData: any) {
  // Handle both 'type' and 'chartType' field names
  const type = chartData.type || chartData.chartType
  const data = chartData.data
  const config = chartData.config || {}

  if (!type || !data) {
    console.warn("Missing required chart type or data:", { type, dataLength: data?.length })
    return null
  }

  let plotlyData: any[] = []
  let layout: any = {
    ...PLOTLY_THEME.layout,
    title: config.title || chartData.title || "",
    showlegend: config.legend !== false,
  }

  switch (type) {
    case "bar":
      if (config.stacked) {
        // Stacked bar chart
        const keys = config.series?.map((s: any) => s.dataKey) || 
          Object.keys(data[0] || {}).filter(key => key !== (config.xAxis?.dataKey || "name"))
        
        plotlyData = keys.map((key: string, index: number) => ({
          x: data.map((d: any) => d[config.xAxis?.dataKey || "name"]),
          y: data.map((d: any) => d[key]),
          type: "bar",
          name: key,
          marker: { color: COLORS[index % COLORS.length] },
        }))
        
        layout.barmode = "stack"
      } else {
        // Regular bar chart
        const series = config.series || [{ dataKey: "value" }]
        plotlyData = series.map((s: any, index: number) => ({
          x: data.map((d: any) => d[config.xAxis?.dataKey || "name"]),
          y: data.map((d: any) => d[s.dataKey]),
          type: "bar",
          name: s.name || s.dataKey,
          marker: { color: s.fill || COLORS[index % COLORS.length] },
        }))
      }
      break

    case "line":
      const lineSeries = config.series || [{ dataKey: "value" }]
      plotlyData = lineSeries.map((s: any, index: number) => ({
        x: data.map((d: any) => d[config.xAxis?.dataKey || "name"]),
        y: data.map((d: any) => d[s.dataKey]),
        type: "scatter",
        mode: "lines+markers",
        name: s.name || s.dataKey,
        line: { color: s.stroke || COLORS[index % COLORS.length], width: 2 },
        marker: { size: 6 },
      }))
      break

    case "area":
      const areaSeries = config.series || [{ dataKey: "value" }]
      plotlyData = areaSeries.map((s: any, index: number) => ({
        x: data.map((d: any) => d[config.xAxis?.dataKey || "name"]),
        y: data.map((d: any) => d[s.dataKey]),
        type: "scatter",
        mode: "lines",
        fill: "tonexty",
        name: s.name || s.dataKey,
        line: { color: s.fill || COLORS[index % COLORS.length] },
        fillcolor: `${s.fill || COLORS[index % COLORS.length]}40`,
      }))
      break

    case "pie":
      const pieDataKey = config.dataKey || config.series?.[0]?.dataKey || "value"
      const nameKey = config.nameKey || "name"
      
      plotlyData = [{
        values: data.map((d: any) => d[pieDataKey]),
        labels: data.map((d: any) => d[nameKey]),
        type: "pie",
        marker: {
          colors: data.map((_: any, index: number) => COLORS[index % COLORS.length])
        },
        textinfo: "label+percent",
        textposition: "auto",
        hole: 0, // Make it a full pie, not donut
      }]
      
      // Pie charts don't need x/y axis
      layout.xaxis = { visible: false }
      layout.yaxis = { visible: false }
      layout.showlegend = true
      
      // Add subtitle if provided
      if (config.subtitle) {
        layout.annotations = [{
          text: config.subtitle,
          showarrow: false,
          x: 0.5,
          y: -0.1,
          xref: 'paper',
          yref: 'paper',
          font: { size: 12, color: '#666' }
        }]
      }
      break

    case "scatter":
      const scatterSeries = config.series || [{ xDataKey: "x", yDataKey: "y" }]
      plotlyData = scatterSeries.map((s: any, index: number) => ({
        x: data.map((d: any) => d[s.xDataKey || "x"]),
        y: data.map((d: any) => d[s.yDataKey || "y"]),
        type: "scatter",
        mode: "markers",
        name: s.name || `Series ${index + 1}`,
        marker: {
          color: s.fill || COLORS[index % COLORS.length],
          size: s.size || 8,
        },
      }))
      break

    case "heatmap":
      plotlyData = [{
        z: data.map((row: any) => Object.values(row)),
        x: Object.keys(data[0] || {}),
        y: data.map((_: any, index: number) => `Row ${index + 1}`),
        type: "heatmap",
        colorscale: "RdBu",
        reversescale: true,
      }]
      break

    case "box":
      const boxSeries = config.series || [{ dataKey: "value" }]
      plotlyData = boxSeries.map((s: any, index: number) => ({
        y: data.map((d: any) => d[s.dataKey]),
        type: "box",
        name: s.name || s.dataKey,
        marker: { color: COLORS[index % COLORS.length] },
      }))
      break

    case "histogram":
      const histSeries = config.series || [{ dataKey: "value" }]
      plotlyData = histSeries.map((s: any, index: number) => ({
        x: data.map((d: any) => d[s.dataKey]),
        type: "histogram",
        name: s.name || s.dataKey,
        marker: { color: COLORS[index % COLORS.length] },
        opacity: 0.7,
      }))
      break

    case "candlestick":
      plotlyData = [{
        x: data.map((d: any) => d.date || d.time || d.x),
        open: data.map((d: any) => d.open),
        high: data.map((d: any) => d.high),
        low: data.map((d: any) => d.low),
        close: data.map((d: any) => d.close),
        type: "candlestick",
        name: "OHLC",
      }]
      layout.xaxis.rangeslider = { visible: false }
      break

    case "funnel":
      plotlyData = [{
        type: "funnel",
        y: data.map((d: any) => d.name || d.stage),
        x: data.map((d: any) => d.value),
        textinfo: "value+percent initial",
        marker: {
          color: data.map((_: any, index: number) => COLORS[index % COLORS.length])
        },
      }]
      break

    case "waterfall":
      plotlyData = [{
        type: "waterfall",
        x: data.map((d: any) => d.name || d.category),
        y: data.map((d: any) => d.value),
        measure: data.map((d: any) => d.measure || "relative"),
        text: data.map((d: any) => d.text || ""),
        textposition: "outside",
        connector: { line: { color: "rgb(63, 63, 63)" } },
      }]
      break

    case "treemap":
      plotlyData = [{
        type: "treemap",
        labels: data.map((d: any) => d.name || d.label),
        values: data.map((d: any) => d.value),
        parents: data.map((d: any) => d.parent || ""),
        textinfo: "label+value",
        marker: {
          colors: data.map((_: any, index: number) => COLORS[index % COLORS.length])
        },
      }]
      break

    case "sunburst":
      plotlyData = [{
        type: "sunburst",
        labels: data.map((d: any) => d.name || d.label),
        values: data.map((d: any) => d.value),
        parents: data.map((d: any) => d.parent || ""),
        branchvalues: "total",
      }]
      break

    default:
      // Fallback to simple bar chart
      plotlyData = [{
        x: data.map((d: any) => d.name || d.label || d.x),
        y: data.map((d: any) => d.value || d.y),
        type: "bar",
        marker: { color: COLORS[0] },
      }]
  }

  // Apply custom layout overrides
  if (config.layout) {
    layout = { ...layout, ...config.layout }
  }

  return { data: plotlyData, layout }
}

export function PlotlyChartRenderer({ artifact }: PlotlyChartRendererProps) {
  const [chartData, setChartData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const parseChartData = async () => {
      setIsLoading(true)
      setError(null)

      try {
        await new Promise((resolve) => setTimeout(resolve, 100))

        const cleanedJson = cleanJsonString(artifact.content)
        const parsed = JSON.parse(cleanedJson)
        setChartData(parsed)
      } catch (error) {
        console.error("❌ Failed to parse chart JSON:", error)
        console.error("📄 Original content:", artifact.content)
        setError("Invalid Chart Data - The provided data contains invalid JSON syntax.")
      } finally {
        setIsLoading(false)
      }
    }

    parseChartData()
  }, [artifact.content])

  const plotlyConfig = useMemo(() => {
    if (!chartData) return null
    
    const config = convertToPlotlyFormat(chartData)
    if (!config) {
      console.error("Failed to convert chart data to Plotly format")
      return null
    }
    
    return config
  }, [chartData])

  if (isLoading) {
    return (
      <div className="w-full bg-white dark:bg-gray-900 p-8 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-3 text-gray-600 dark:text-gray-400">
          <Loader2 className="w-8 h-8 animate-spin text-red-500" />
          <span className="text-sm font-medium">Rendering chart...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="w-full bg-white dark:bg-gray-900 p-8 rounded-lg border border-red-200 dark:border-red-800 shadow-sm">
        <div className="flex items-start gap-3 text-red-600 dark:text-red-400">
          <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
          <div>
            <h3 className="font-medium mb-2">{error}</h3>
            <details className="mt-3">
              <summary className="cursor-pointer text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
                View raw content
              </summary>
              <pre className="mt-2 p-3 bg-gray-50 dark:bg-gray-800 rounded text-xs overflow-auto max-h-40 whitespace-pre-wrap">
                {artifact.content}
              </pre>
            </details>
          </div>
        </div>
      </div>
    )
  }

  if (!plotlyConfig) {
    return (
      <div className="w-full bg-white dark:bg-gray-900 p-8 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="text-center text-gray-500 dark:text-gray-400">
          No chart data available
        </div>
      </div>
    )
  }

  return (
    <div className="w-full bg-white dark:bg-gray-900 p-6 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
      <div className="w-full h-[500px]">
        <Plot
          data={plotlyConfig.data}
          layout={{
            ...plotlyConfig.layout,
            autosize: true,
            responsive: true,
          }}
          config={{
            ...PLOTLY_THEME.config,
            responsive: true,
          }}
          style={{ width: "100%", height: "100%" }}
          useResizeHandler={true}
        />
      </div>
      
      {/* Chart info footer */}
      {chartData.config?.subtitle && (
        <div className="mt-4 text-sm text-gray-600 dark:text-gray-400 text-center">
          {chartData.config.subtitle}
        </div>
      )}
    </div>
  )
}
