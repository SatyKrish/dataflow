"use client"

import { PlotlyChartRenderer } from "@/components/plotly-chart-renderer"

// Example chart data for different chart types
const chartExamples = [
  {
    name: "Sales by Quarter (Bar Chart)",
    data: {
      type: "bar",
      data: [
        { name: "Q1", revenue: 12000, profit: 3000 },
        { name: "Q2", revenue: 15000, profit: 4500 },
        { name: "Q3", revenue: 18000, profit: 5400 },
        { name: "Q4", revenue: 22000, profit: 7200 }
      ],
      config: {
        title: "Quarterly Financial Performance",
        xAxis: { dataKey: "name" },
        series: [
          { dataKey: "revenue", name: "Revenue", fill: "#dc2626" },
          { dataKey: "profit", name: "Profit", fill: "#059669" }
        ],
        legend: true
      }
    }
  },
  {
    name: "Stock Price Trend (Line Chart)",
    data: {
      type: "line",
      data: [
        { date: "2024-01", price: 150, volume: 1000 },
        { date: "2024-02", price: 162, volume: 1200 },
        { date: "2024-03", price: 158, volume: 950 },
        { date: "2024-04", price: 175, volume: 1400 },
        { date: "2024-05", price: 185, volume: 1600 },
        { date: "2024-06", price: 192, volume: 1350 }
      ],
      config: {
        title: "Stock Price Movement",
        xAxis: { dataKey: "date" },
        series: [
          { dataKey: "price", name: "Stock Price ($)", stroke: "#2563eb" }
        ],
        legend: true
      }
    }
  },
  {
    name: "Market Share (Pie Chart) - Chat Format",
    data: {
      chartType: "pie",
      title: "Customer Account Type Distribution by Age Group",
      data: [
        { name: "18-25: Basic", value: 120 },
        { name: "18-25: Premium", value: 45 },
        { name: "18-25: Business", value: 15 },
        { name: "26-35: Basic", value: 100 },
        { name: "26-35: Premium", value: 80 },
        { name: "26-35: Business", value: 30 },
        { name: "36-50: Basic", value: 60 },
        { name: "36-50: Premium", value: 90 },
        { name: "36-50: Business", value: 50 },
        { name: "51+: Basic", value: 40 },
        { name: "51+: Premium", value: 35 },
        { name: "51+: Business", value: 25 }
      ],
      config: {
        title: "Customer Account Type by Age Group",
        subtitle: "Pie chart of account types within each age group",
        legend: true,
        series: [
          { dataKey: "value", name: "Number of Customers" }
        ]
      }
    }
  },
  {
    name: "Sales Funnel",
    data: {
      type: "funnel",
      data: [
        { name: "Website Visitors", value: 10000 },
        { name: "Leads Generated", value: 2000 },
        { name: "Qualified Leads", value: 800 },
        { name: "Opportunities", value: 300 },
        { name: "Closed Deals", value: 75 }
      ],
      config: {
        title: "Sales Conversion Funnel"
      }
    }
  },
  {
    name: "Financial Performance (Candlestick)",
    data: {
      type: "candlestick",
      data: [
        { date: "2024-01-01", open: 150, high: 165, low: 148, close: 162 },
        { date: "2024-01-02", open: 162, high: 170, low: 158, close: 168 },
        { date: "2024-01-03", open: 168, high: 175, low: 165, close: 172 },
        { date: "2024-01-04", open: 172, high: 178, low: 169, close: 175 },
        { date: "2024-01-05", open: 175, high: 182, low: 173, close: 180 }
      ],
      config: {
        title: "Stock Price OHLC Chart"
      }
    }
  },
  {
    name: "Revenue Waterfall",
    data: {
      type: "waterfall",
      data: [
        { name: "Starting Revenue", value: 100000, measure: "absolute" },
        { name: "New Customers", value: 25000, measure: "relative" },
        { name: "Upsells", value: 15000, measure: "relative" },
        { name: "Churn", value: -8000, measure: "relative" },
        { name: "Price Changes", value: 3000, measure: "relative" },
        { name: "Ending Revenue", value: 135000, measure: "total" }
      ],
      config: {
        title: "Revenue Breakdown Analysis"
      }
    }
  },
  {
    name: "Customer Satisfaction (Box Plot)",
    data: {
      type: "box",
      data: [
        { product: "A", satisfaction: 4.2 },
        { product: "A", satisfaction: 4.5 },
        { product: "A", satisfaction: 3.8 },
        { product: "A", satisfaction: 4.1 },
        { product: "A", satisfaction: 4.7 },
        { product: "B", satisfaction: 3.9 },
        { product: "B", satisfaction: 4.3 },
        { product: "B", satisfaction: 4.0 },
        { product: "B", satisfaction: 3.7 },
        { product: "B", satisfaction: 4.2 }
      ],
      config: {
        title: "Customer Satisfaction Distribution",
        series: [{ dataKey: "satisfaction", name: "Satisfaction Score" }]
      }
    }
  },
  {
    name: "Correlation Heatmap",
    data: {
      type: "heatmap",
      data: [
        { revenue: 1.0, profit: 0.85, customers: 0.72, satisfaction: 0.61 },
        { revenue: 0.85, profit: 1.0, customers: 0.68, satisfaction: 0.55 },
        { revenue: 0.72, profit: 0.68, customers: 1.0, satisfaction: 0.78 },
        { revenue: 0.61, profit: 0.55, customers: 0.78, satisfaction: 1.0 }
      ],
      config: {
        title: "Business Metrics Correlation Matrix"
      }
    }
  },
  {
    name: "Chat Markdown Format Test",
    data: `\`\`\`chart
{
  "chartType": "pie",
  "title": "Customer Account Type Distribution by Age Group",
  "data": [
    {"name": "18-25: Basic", "value": 120},
    {"name": "18-25: Premium", "value": 45},
    {"name": "18-25: Business", "value": 15},
    {"name": "26-35: Basic", "value": 100},
    {"name": "26-35: Premium", "value": 80},
    {"name": "26-35: Business", "value": 30}
  ],
  "config": {
    "title": "Customer Account Type by Age Group",
    "subtitle": "Test of markdown code block parsing",
    "legend": true,
    "series": [
      {"dataKey": "value", "name": "Number of Customers"}
    ]
  }
}
\`\`\``
  }
]

export default function PlotlyTestPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Plotly Chart Examples
        </h1>
        <p className="text-gray-600 text-lg">
          Showcasing the new Plotly-powered visualization capabilities for data analysts, 
          product owners, finance analysts, and developers.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {chartExamples.map((example, index) => (
          <div key={index} className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-800">
              {example.name}
            </h2>
            <PlotlyChartRenderer 
              artifact={{ 
                content: typeof example.data === 'string' 
                  ? example.data 
                  : JSON.stringify(example.data, null, 2) 
              }} 
            />
          </div>
        ))}
      </div>

      <div className="mt-12 p-6 bg-gray-50 rounded-lg">
        <h3 className="text-xl font-semibold mb-4">Chart Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-green-600">Data Analysis</h4>
            <ul className="text-gray-600 mt-2 space-y-1">
              <li>• Statistical plots (box, violin)</li>
              <li>• Correlation heatmaps</li>
              <li>• Distribution analysis</li>
              <li>• Time series analysis</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-blue-600">Business Intelligence</h4>
            <ul className="text-gray-600 mt-2 space-y-1">
              <li>• Sales funnels</li>
              <li>• Revenue waterfalls</li>
              <li>• Performance dashboards</li>
              <li>• KPI visualization</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-purple-600">Financial Analysis</h4>
            <ul className="text-gray-600 mt-2 space-y-1">
              <li>• Candlestick charts</li>
              <li>• OHLC visualization</li>
              <li>• Financial metrics</li>
              <li>• Portfolio analysis</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="mt-8 p-6 bg-blue-50 rounded-lg">
        <h3 className="text-xl font-semibold mb-4 text-blue-800">
          Interactive Features
        </h3>
        <div className="text-blue-700 space-y-2">
          <p>✅ <strong>Zoom & Pan:</strong> Explore data in detail</p>
          <p>✅ <strong>Hover Tooltips:</strong> Get precise data values</p>
          <p>✅ <strong>Export Options:</strong> Download as PNG, SVG, or PDF</p>
          <p>✅ <strong>Responsive Design:</strong> Works on all screen sizes</p>
          <p>✅ <strong>Professional Styling:</strong> Publication-ready charts</p>
        </div>
      </div>
    </div>
  )
}
