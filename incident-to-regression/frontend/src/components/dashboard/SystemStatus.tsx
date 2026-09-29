import React from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../ui/Card'
import { StatusIndicator } from '../ui/StatusIndicator'
import { Skeleton } from '../ui/Skeleton'
import { ErrorState } from '../ui/ErrorState'
import { useSystemStatus } from '@/hooks/useSystemStatus'

export const SystemStatusCard: React.FC = () => {
  const { apiStatus, dbStatus, environment, latency_ms, isLoading, isError } = useSystemStatus()

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
        </CardContent>
      </Card>
    )
  }

  if (isError) {
    return (
      <Card className="border-red-200">
        <CardContent className="p-0">
          <ErrorState 
            title="Backend Unavailable" 
            message="Unable to connect to the backend API. Please check if the service is running." 
            className="border-none bg-transparent"
          />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-4">
        <CardTitle className="text-lg">System Infrastructure</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-500">API Service</span>
            <StatusIndicator status={apiStatus} />
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-500">PostgreSQL Database</span>
            <StatusIndicator status={dbStatus} />
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-500">Database Latency</span>
            <span className="text-sm font-mono text-slate-700">
              {latency_ms ? `${latency_ms}ms` : '—'}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-500">Environment</span>
            <span className="text-sm font-medium px-2 py-0.5 rounded bg-white/50 backdrop-blur-lg text-slate-700 capitalize">
              {environment}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
