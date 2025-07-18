"use client"

import { useState, useCallback, useRef } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { 
  Upload, 
  FileText, 
  Database, 
  Cloud, 
  CheckCircle, 
  AlertCircle,
  X,
  Zap,
  BarChart3,
  Table,
  FileSpreadsheet
} from "lucide-react"

interface SmartDataUploadProps {
  onFileUpload?: (file: File, analysis: any) => void
  supportedFormats?: string[]
  maxFileSize?: number
}

interface UploadedFile {
  file: File
  id: string
  status: 'uploading' | 'analyzing' | 'complete' | 'error'
  progress: number
  analysis?: {
    rows: number
    columns: number
    fileType: string
    suggestedCharts: string[]
    dataTypes: Record<string, string>
    sampleData: any[]
  }
  error?: string
}

/**
 * Julius.ai-inspired smart data upload with instant analysis
 */
export function SmartDataUpload({ 
  onFileUpload, 
  supportedFormats = ['csv', 'xlsx', 'json', 'tsv'],
  maxFileSize = 100 * 1024 * 1024 // 100MB
}: SmartDataUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isDragActive, setIsDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFiles = useCallback(async (files: FileList | null) => {
    if (!files) return

    const fileArray = Array.from(files)
    const newFiles: UploadedFile[] = fileArray.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'uploading',
      progress: 0
    }))

    setUploadedFiles(prev => [...prev, ...newFiles])

    // Process each file
    for (const fileData of newFiles) {
      await processFile(fileData)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragActive(false)
    handleFiles(e.dataTransfer.files)
  }, [handleFiles])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragActive(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragActive(false)
  }, [])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files)
  }, [handleFiles])

  const processFile = async (fileData: UploadedFile) => {
    try {
      // Simulate upload progress
      for (let progress = 0; progress <= 100; progress += 10) {
        setUploadedFiles(prev => 
          prev.map(f => f.id === fileData.id ? { ...f, progress } : f)
        )
        await new Promise(resolve => setTimeout(resolve, 100))
      }

      // Switch to analyzing
      setUploadedFiles(prev => 
        prev.map(f => f.id === fileData.id ? { ...f, status: 'analyzing', progress: 0 } : f)
      )

      // Simulate analysis
      for (let progress = 0; progress <= 100; progress += 20) {
        setUploadedFiles(prev => 
          prev.map(f => f.id === fileData.id ? { ...f, progress } : f)
        )
        await new Promise(resolve => setTimeout(resolve, 200))
      }

      // Generate mock analysis results
      const analysis = {
        rows: Math.floor(Math.random() * 10000) + 100,
        columns: Math.floor(Math.random() * 20) + 5,
        fileType: fileData.file.name.split('.').pop()?.toUpperCase() || 'UNKNOWN',
        suggestedCharts: ['Bar Chart', 'Line Chart', 'Scatter Plot'].slice(0, Math.floor(Math.random() * 3) + 1),
        dataTypes: {
          'id': 'number',
          'name': 'string',
          'date': 'date',
          'amount': 'currency',
          'category': 'category'
        },
        sampleData: [
          { id: 1, name: 'Sample 1', date: '2024-01-01', amount: 1200, category: 'A' },
          { id: 2, name: 'Sample 2', date: '2024-01-02', amount: 800, category: 'B' },
          { id: 3, name: 'Sample 3', date: '2024-01-03', amount: 1500, category: 'A' }
        ]
      }

      setUploadedFiles(prev => 
        prev.map(f => f.id === fileData.id ? { 
          ...f, 
          status: 'complete', 
          progress: 100, 
          analysis 
        } : f)
      )

      onFileUpload?.(fileData.file, analysis)

    } catch (error) {
      setUploadedFiles(prev => 
        prev.map(f => f.id === fileData.id ? { 
          ...f, 
          status: 'error', 
          error: 'Failed to process file' 
        } : f)
      )
    }
  }

  const removeFile = (id: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== id))
  }

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase()
    switch (extension) {
      case 'csv':
      case 'tsv':
        return <FileText className="w-8 h-8 text-green-500" />
      case 'xlsx':
      case 'xls':
        return <FileSpreadsheet className="w-8 h-8 text-blue-500" />
      case 'json':
        return <Database className="w-8 h-8 text-purple-500" />
      default:
        return <FileText className="w-8 h-8 text-gray-500" />
    }
  }

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'complete':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />
      default:
        return <Zap className="w-5 h-5 text-blue-500 animate-pulse" />
    }
  }

  const getStatusText = (file: UploadedFile) => {
    switch (file.status) {
      case 'uploading':
        return 'Uploading...'
      case 'analyzing':
        return 'Analyzing data...'
      case 'complete':
        return `${file.analysis?.rows.toLocaleString()} rows, ${file.analysis?.columns} columns`
      case 'error':
        return file.error || 'Error processing file'
    }
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Upload Zone */}
      <Card className={`transition-all duration-200 ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-dashed'}`}>
        <CardContent className="p-8">
          <div 
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current?.click()}
            className="cursor-pointer"
          >
            <input 
              ref={fileInputRef}
              type="file"
              multiple
              accept=".csv,.xlsx,.json,.tsv"
              onChange={handleFileInput}
              className="hidden"
            />
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-blue-100 to-purple-100 rounded-xl flex items-center justify-center">
                <Upload className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Drop your data files here
              </h3>
              <p className="text-gray-600 mb-4">
                Upload CSV, Excel, JSON, or TSV files to start analyzing instantly
              </p>
              <div className="flex items-center justify-center gap-2 mb-4">
                {supportedFormats.map(format => (
                  <Badge key={format} variant="outline" className="text-xs">
                    .{format}
                  </Badge>
                ))}
              </div>
              <Button type="button">
                <Cloud className="w-4 h-4 mr-2" />
                Choose Files
              </Button>
              <p className="text-xs text-gray-500 mt-2">
                Maximum file size: {(maxFileSize / (1024 * 1024)).toFixed(0)}MB
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Uploaded Files ({uploadedFiles.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {uploadedFiles.map((file) => (
              <div key={file.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    {getFileIcon(file.file.name)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <h4 className="font-medium text-gray-900 truncate">{file.file.name}</h4>
                        <p className="text-sm text-gray-500">
                          {(file.file.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(file.status)}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(file.id)}
                          className="h-8 w-8 p-0"
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>

                    {(file.status === 'uploading' || file.status === 'analyzing') && (
                      <div className="space-y-2">
                        <Progress value={file.progress} className="h-2" />
                        <p className="text-sm text-gray-600">{getStatusText(file)}</p>
                      </div>
                    )}

                    {file.status === 'complete' && file.analysis && (
                      <div className="space-y-3">
                        <p className="text-sm text-green-600 font-medium">{getStatusText(file)}</p>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="font-medium text-gray-600">File Type</span>
                            <p className="text-gray-900">{file.analysis.fileType}</p>
                          </div>
                          <div>
                            <span className="font-medium text-gray-600">Rows</span>
                            <p className="text-gray-900">{file.analysis.rows.toLocaleString()}</p>
                          </div>
                          <div>
                            <span className="font-medium text-gray-600">Columns</span>
                            <p className="text-gray-900">{file.analysis.columns}</p>
                          </div>
                          <div>
                            <span className="font-medium text-gray-600">Charts</span>
                            <p className="text-gray-900">{file.analysis.suggestedCharts.length} suggested</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Button size="sm" variant="outline">
                            <Table className="w-4 h-4 mr-2" />
                            View Data
                          </Button>
                          <Button size="sm" variant="outline">
                            <BarChart3 className="w-4 h-4 mr-2" />
                            Create Chart
                          </Button>
                        </div>
                      </div>
                    )}

                    {file.status === 'error' && (
                      <p className="text-sm text-red-600">{getStatusText(file)}</p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
