export interface HealthStatus {
  status: string
  service: string
  environment: string
  version: string
}

export interface DatabaseHealthStatus {
  status: string
  database: string
  latency_ms?: number
  error?: string
}

export interface SystemStatus {
  api: 'operational' | 'degraded' | 'unavailable' | 'checking'
  database: 'connected' | 'disconnected' | 'checking'
  environment: string
  latency_ms?: number
}

export interface ApiError {
  code: string
  message: string
  request_id: string
}

export interface MetricCardData {
  label: string
  value: string | number
  subtitle: string
  trend?: {
    value: number
    isPositive: boolean
  }
}
