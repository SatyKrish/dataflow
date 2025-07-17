"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  DollarSign, 
  Target,
  ArrowUpRight,
  ArrowDownRight,
  Calendar,
  Filter,
  Download,
  Share2,
  Sparkles
} from "lucide-react"

interface AnalysisDashboardProps {
  data?: {
    insights: Array<{
      id: string
      title: string
      value: string | number
      change: number
      type: 'metric' | 'insight' | 'trend'
      category: string
    }>
    charts: Array<{
      id: string
      title: string
      type: 'bar' | 'line' | 'pie' | 'scatter'
      data: any
    }>
    summary: {
      totalRows: number
      timeRange: string
      lastUpdated: string
      dataQuality: number
    }
  }
}

/**
 * Julius.ai-inspired analysis dashboard
 * Features instant insights, visual summaries, and data quality indicators
 */
export function AnalysisDashboard({ data }: AnalysisDashboardProps) {
  const [activeTab, setActiveTab] = useState("overview")

  if (!data) {
    return (
      <div className="p-8 text-center">
        <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-blue-100 to-purple-100 rounded-xl flex items-center justify-center">
          <BarChart3 className="w-8 h-8 text-blue-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Ready for Analysis</h3>
        <p className="text-gray-600 max-w-md mx-auto">
          Upload your data or connect a data source to start generating insights instantly.
        </p>
      </div>
    )
  }

  const getMetricIcon = (type: string) => {
    switch (type) {
      case 'revenue': return <DollarSign className="w-4 h-4" />
      case 'users': return <Users className="w-4 h-4" />
      case 'conversion': return <Target className="w-4 h-4" />
      default: return <TrendingUp className="w-4 h-4" />
    }
  }

  const getChangeIcon = (change: number) => {
    return change >= 0 ? 
      <ArrowUpRight className="w-3 h-3 text-green-600" /> : 
      <ArrowDownRight className="w-3 h-3 text-red-600" />
  }

  const getChangeColor = (change: number) => {
    return change >= 0 ? 'text-green-600' : 'text-red-600'
  }

  return (
    <div className="w-full max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-blue-600" />
            Analysis Results
          </h2>
          <p className="text-gray-600 mt-1">
            {data.summary.totalRows.toLocaleString()} rows • {data.summary.timeRange} • 
            Updated {data.summary.lastUpdated}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge 
            variant="outline" 
            className={`${data.summary.dataQuality >= 90 ? 'text-green-700 bg-green-50 border-green-200' : 'text-yellow-700 bg-yellow-50 border-yellow-200'}`}
          >
            {data.summary.dataQuality}% Data Quality
          </Badge>
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Button size="sm">
            <Share2 className="w-4 h-4 mr-2" />
            Share
          </Button>
        </div>
      </div>

      {/* Quick Insights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {data.insights.slice(0, 4).map((insight) => (
          <Card key={insight.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2 text-gray-600">
                  {getMetricIcon(insight.category)}
                  <span className="text-sm font-medium">{insight.title}</span>
                </div>
                <div className="flex items-center gap-1">
                  {getChangeIcon(insight.change)}
                  <span className={`text-xs font-medium ${getChangeColor(insight.change)}`}>
                    {Math.abs(insight.change)}%
                  </span>
                </div>
              </div>
              <div className="mt-2">
                <div className="text-2xl font-bold text-gray-900">{insight.value}</div>
                <div className="text-xs text-gray-500 capitalize">{insight.category}</div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="insights">Key Insights</TabsTrigger>
          <TabsTrigger value="charts">Visualizations</TabsTrigger>
          <TabsTrigger value="data">Raw Data</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                  Performance Trends
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <BarChart3 className="w-12 h-12 text-blue-400 mx-auto mb-2" />
                    <p className="text-gray-600">Chart will render here</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Quick Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {data.insights.slice(0, 3).map((insight) => (
                  <div key={insight.id} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">{insight.title}</span>
                    <div className="text-right">
                      <div className="font-semibold">{insight.value}</div>
                      <div className={`text-xs ${getChangeColor(insight.change)}`}>
                        {insight.change >= 0 ? '+' : ''}{insight.change}%
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="insights" className="space-y-4">
          {data.insights.map((insight) => (
            <Card key={insight.id} className="border-l-4 border-l-blue-500">
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-semibold text-gray-900">{insight.title}</h4>
                    <p className="text-2xl font-bold text-blue-600 mt-1">{insight.value}</p>
                    <p className="text-sm text-gray-600 mt-1 capitalize">{insight.type} • {insight.category}</p>
                  </div>
                  <Badge 
                    variant={insight.change >= 0 ? "default" : "destructive"}
                    className="text-xs"
                  >
                    {insight.change >= 0 ? '+' : ''}{insight.change}%
                  </Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="charts" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {data.charts.map((chart) => (
              <Card key={chart.id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>{chart.title}</span>
                    <Badge variant="outline" className="text-xs">
                      {chart.type.toUpperCase()}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                    <div className="text-center">
                      <BarChart3 className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-500 text-sm">{chart.type} chart</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="data" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Data Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <Calendar className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-500">Data table will render here</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
