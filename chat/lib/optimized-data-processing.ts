/**
 * Optimized data processing utilities for charts and tables
 * Designed for Data Analysts, Finance Analysts, and Product Owners
 */

import { useMemo } from 'react'

export interface DataPoint {
  [key: string]: string | number | boolean | null
}

export interface ProcessedChartData {
  data: DataPoint[]
  columns: string[]
  summary: {
    totalRows: number
    totalColumns: number
    numericalColumns: string[]
    categoricalColumns: string[]
    missingValues: Record<string, number>
  }
}

/**
 * Efficiently process large datasets for visualization
 * Includes data validation, type inference, and sampling
 */
export function useOptimizedDataProcessing(
  rawData: any[],
  maxDataPoints: number = 1000
): ProcessedChartData {
  return useMemo(() => {
    if (!Array.isArray(rawData) || rawData.length === 0) {
      return {
        data: [],
        columns: [],
        summary: {
          totalRows: 0,
          totalColumns: 0,
          numericalColumns: [],
          categoricalColumns: [],
          missingValues: {}
        }
      }
    }

    // Sample data if too large
    const sampledData = rawData.length > maxDataPoints 
      ? sampleDataPoints(rawData, maxDataPoints)
      : rawData

    // Clean and normalize data
    const cleanedData = sampledData
      .filter(row => row && typeof row === 'object')
      .map(row => cleanRow(row))

    if (cleanedData.length === 0) {
      return {
        data: [],
        columns: [],
        summary: {
          totalRows: 0,
          totalColumns: 0,
          numericalColumns: [],
          categoricalColumns: [],
          missingValues: {}
        }
      }
    }

    // Infer column types and generate summary
    const allColumns = [...new Set(cleanedData.flatMap(Object.keys))]
    const summary = generateDataSummary(cleanedData, allColumns)

    return {
      data: cleanedData,
      columns: allColumns,
      summary: {
        ...summary,
        totalRows: rawData.length, // Original count
        totalColumns: allColumns.length
      }
    }
  }, [rawData, maxDataPoints])
}

/**
 * Smart sampling algorithm for large datasets
 * Preserves data distribution while reducing size
 */
function sampleDataPoints(data: any[], targetSize: number): any[] {
  if (data.length <= targetSize) return data

  const step = data.length / targetSize
  const sampled: any[] = []
  
  for (let i = 0; i < targetSize; i++) {
    const index = Math.floor(i * step)
    sampled.push(data[index])
  }
  
  return sampled
}

/**
 * Clean and normalize individual data rows
 */
function cleanRow(row: any): DataPoint {
  const cleaned: DataPoint = {}
  
  for (const [key, value] of Object.entries(row)) {
    const cleanKey = String(key).trim()
    if (!cleanKey) continue

    if (value === null || value === undefined || value === '') {
      cleaned[cleanKey] = null
    } else if (typeof value === 'number' && !isNaN(value)) {
      cleaned[cleanKey] = value
    } else if (typeof value === 'boolean') {
      cleaned[cleanKey] = value
    } else {
      const strValue = String(value).trim()
      // Try to parse as number
      const numValue = Number(strValue)
      if (!isNaN(numValue) && strValue !== '') {
        cleaned[cleanKey] = numValue
      } else {
        cleaned[cleanKey] = strValue
      }
    }
  }
  
  return cleaned
}

/**
 * Generate comprehensive data summary for analysts
 */
function generateDataSummary(data: DataPoint[], columns: string[]) {
  const numericalColumns: string[] = []
  const categoricalColumns: string[] = []
  const missingValues: Record<string, number> = {}

  columns.forEach(column => {
    let numericCount = 0
    let nullCount = 0
    
    data.forEach(row => {
      const value = row[column]
      if (value === null) {
        nullCount++
      } else if (typeof value === 'number') {
        numericCount++
      }
    })
    
    missingValues[column] = nullCount
    
    // Consider column numeric if >70% of values are numbers
    if (numericCount > data.length * 0.7) {
      numericalColumns.push(column)
    } else {
      categoricalColumns.push(column)
    }
  })

  return {
    numericalColumns,
    categoricalColumns,
    missingValues
  }
}

/**
 * Optimized chart configuration for different user roles
 */
export function getOptimizedChartConfig(
  userRole: 'data-analyst' | 'product-owner' | 'finance-analyst' | 'developer',
  chartType: string,
  dataSize: number
) {
  const baseConfig = {
    animation: dataSize < 100, // Disable animations for large datasets
    throttleDelay: dataSize > 500 ? 200 : 100,
    margin: { top: 20, right: 30, bottom: 20, left: 20 }
  }

  switch (userRole) {
    case 'finance-analyst':
      return {
        ...baseConfig,
        precision: 2,
        showDataLabels: dataSize < 50,
        enableZoom: true,
        showTooltips: true,
        colorScheme: 'professional' // Conservative colors
      }
    
    case 'data-analyst':
      return {
        ...baseConfig,
        precision: 4,
        showDataLabels: dataSize < 100,
        enableZoom: true,
        showTooltips: true,
        showStatistics: true,
        colorScheme: 'analytical' // High contrast colors
      }
    
    case 'product-owner':
      return {
        ...baseConfig,
        precision: 1,
        showDataLabels: dataSize < 30,
        enableZoom: false,
        showTooltips: true,
        emphasizeTrends: true,
        colorScheme: 'business' // Clear, simple colors
      }
    
    case 'developer':
      return {
        ...baseConfig,
        precision: 6,
        showDataLabels: dataSize < 20,
        enableZoom: true,
        showTooltips: true,
        showDebugInfo: true,
        colorScheme: 'technical' // Detailed color coding
      }
    
    default:
      return baseConfig
  }
}

/**
 * Memoized data aggregation for common operations
 */
export function useDataAggregation(data: DataPoint[], groupByColumn?: string) {
  return useMemo(() => {
    if (!groupByColumn || data.length === 0) return data

    const grouped = data.reduce((acc, row) => {
      const key = String(row[groupByColumn] || 'Unknown')
      if (!acc[key]) acc[key] = []
      acc[key].push(row)
      return acc
    }, {} as Record<string, DataPoint[]>)

    return Object.entries(grouped).map(([key, rows]) => ({
      [groupByColumn]: key,
      count: rows.length,
      ...aggregateNumericalColumns(rows)
    }))
  }, [data, groupByColumn])
}

function aggregateNumericalColumns(rows: DataPoint[]): Record<string, number> {
  const result: Record<string, number> = {}
  const numericalColumns = Object.keys(rows[0] || {}).filter(key => 
    rows.some(row => typeof row[key] === 'number')
  )

  numericalColumns.forEach(column => {
    const values = rows
      .map(row => row[column])
      .filter((val): val is number => typeof val === 'number')
    
    if (values.length > 0) {
      result[`${column}_sum`] = values.reduce((sum, val) => sum + val, 0)
      result[`${column}_avg`] = result[`${column}_sum`] / values.length
      result[`${column}_min`] = Math.min(...values)
      result[`${column}_max`] = Math.max(...values)
    }
  })

  return result
}
